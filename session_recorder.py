"""In-memory session event recorder that writes one JSON log per bot call."""

from __future__ import annotations

import json
import re
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger
from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    CancelFrame,
    EndFrame,
    ErrorFrame,
    FatalErrorFrame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    LLMTextFrame,
    MetricsFrame,
    TranscriptionFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
)
from pipecat.observers.base_observer import BaseObserver, FramePushed

_LOGS_DIR = Path(__file__).resolve().parent / "logs"
_FILENAME_RE = re.compile(
    r"^(?P<month>[A-Z]{3})_(?P<day>\d{2})_(?P<year>\d{4})_(?P<num>\d{3})\.json$"
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _safe_json(value: Any) -> Any:
    """Return a JSON-serializable copy, dropping binary and non-serializable values."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, bytes):
        return f"<bytes:{len(value)}>"
    if isinstance(value, dict):
        return {str(k): _safe_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe_json(v) for v in value]
    if hasattr(value, "model_dump"):
        try:
            return _safe_json(value.model_dump())
        except Exception:
            return str(value)
    if hasattr(value, "dict"):
        try:
            return _safe_json(value.dict())
        except Exception:
            return str(value)
    return str(value)


def _sanitize_messages(messages: list[Any] | None) -> list[Any]:
    if not messages:
        return []
    return _safe_json(messages)


def next_log_path(logs_dir: Path | None = None, when: datetime | None = None) -> Path:
    """Pick the first unused ``MMM_DD_YYYY_NNN.json`` path under ``logs/``."""
    logs_dir = logs_dir or _LOGS_DIR
    logs_dir.mkdir(parents=True, exist_ok=True)
    when = when or _utc_now()
    # Local calendar date matches the example filename style (AUG_20_2026_001).
    local = when.astimezone()
    prefix = local.strftime("%b").upper() + local.strftime("_%d_%Y_")
    used: set[int] = set()
    for path in logs_dir.iterdir():
        if not path.is_file():
            continue
        match = _FILENAME_RE.match(path.name)
        if not match:
            continue
        if path.name.startswith(prefix):
            used.add(int(match.group("num")))
    number = 1
    while number in used:
        number += 1
    return logs_dir / f"{prefix}{number:03d}.json"


class SessionRecorder(BaseObserver):
    """Collect meaningful server-side pipeline events for one bot session."""

    def __init__(self, *, logs_dir: Path | None = None, session_id: str | None = None) -> None:
        super().__init__()
        self.session_id = session_id or str(uuid.uuid4())
        self.logs_dir = Path(logs_dir) if logs_dir else _LOGS_DIR
        self.started_at = _utc_now()
        self.ended_at: datetime | None = None
        self._events: list[dict[str, Any]] = []
        self._seen_frame_ids: set[int] = set()
        self._llm_text_parts: list[str] = []
        self._saved = False
        self._lock = threading.Lock()
        self._context = None

    def bind_context(self, context: Any) -> None:
        """Keep a reference to ``LLMContext`` for final history on save."""
        self._context = context

    def record(self, event: str, data: dict[str, Any] | None = None) -> None:
        """Append one structured event to the in-memory session log."""
        entry = {
            "timestamp": _iso(_utc_now()),
            "event": event,
            "data": _safe_json(data or {}),
        }
        with self._lock:
            if self._saved:
                return
            self._events.append(entry)

    def start(self) -> None:
        """Mark the session as started (call when the client connects)."""
        self.started_at = _utc_now()
        self.record("session_started", {"session_id": self.session_id})

    async def on_push_frame(self, data: FramePushed) -> None:
        frame = data.frame
        frame_id = getattr(frame, "id", None)
        if frame_id is not None:
            sibling_id = getattr(frame, "broadcast_sibling_id", None)
            if frame_id in self._seen_frame_ids or sibling_id in self._seen_frame_ids:
                return
            self._seen_frame_ids.add(frame_id)
            if sibling_id is not None:
                self._seen_frame_ids.add(sibling_id)
            # Bound memory for long sessions.
            if len(self._seen_frame_ids) > 5000:
                self._seen_frame_ids.clear()

        if isinstance(frame, UserStartedSpeakingFrame):
            self.record("user_started_speaking")
        elif isinstance(frame, UserStoppedSpeakingFrame):
            self.record("user_stopped_speaking")
        elif isinstance(frame, BotStartedSpeakingFrame):
            self.record("bot_started_speaking")
        elif isinstance(frame, BotStoppedSpeakingFrame):
            self.record("bot_stopped_speaking")
        elif isinstance(frame, TranscriptionFrame):
            text = (frame.text or "").strip()
            if text:
                payload: dict[str, Any] = {"text": text}
                if getattr(frame, "user_id", None):
                    payload["user_id"] = frame.user_id
                self.record("user_transcript", payload)
        elif isinstance(frame, LLMFullResponseStartFrame):
            self._llm_text_parts = []
        elif isinstance(frame, LLMTextFrame):
            if frame.text:
                self._llm_text_parts.append(frame.text)
        elif isinstance(frame, LLMFullResponseEndFrame):
            text = "".join(self._llm_text_parts).strip()
            self._llm_text_parts = []
            if text:
                self.record("assistant_response", {"text": text})
        elif isinstance(frame, MetricsFrame):
            metrics = []
            for item in frame.data or []:
                metrics.append(_safe_json(item))
            if metrics:
                self.record("metrics", {"items": metrics})
        elif isinstance(frame, (ErrorFrame, FatalErrorFrame)):
            self.record(
                "error",
                {
                    "error": getattr(frame, "error", str(frame)),
                    "fatal": bool(getattr(frame, "fatal", isinstance(frame, FatalErrorFrame))),
                    "processor": str(getattr(frame, "processor", None) or ""),
                },
            )
        elif isinstance(frame, EndFrame):
            self.record("pipeline_end", {"reason": "end_frame"})
            self.save(reason="end_frame")
        elif isinstance(frame, CancelFrame):
            self.record("pipeline_cancel", {"reason": "cancel_frame"})
            self.save(reason="cancel_frame")

    def save(self, *, reason: str | None = None) -> Path | None:
        """Write the session JSON once. Safe to call from multiple end paths."""
        with self._lock:
            if self._saved:
                return None
            self._saved = True
            self.ended_at = _utc_now()
            if reason:
                self._events.append(
                    {
                        "timestamp": _iso(self.ended_at),
                        "event": "session_ended",
                        "data": {"reason": reason},
                    }
                )
            else:
                self._events.append(
                    {
                        "timestamp": _iso(self.ended_at),
                        "event": "session_ended",
                        "data": {},
                    }
                )

            history: list[Any] = []
            if self._context is not None:
                try:
                    history = _sanitize_messages(self._context.get_messages())
                except Exception as exc:
                    logger.warning(f"Could not read LLM context for session log: {exc}")

            payload = {
                "session_id": self.session_id,
                "started_at": _iso(self.started_at),
                "ended_at": _iso(self.ended_at),
                "events": list(self._events),
            }
            if history:
                payload["conversation_history"] = history

            path = next_log_path(self.logs_dir, self.ended_at)
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            logger.info(f"Session log saved: {path} ({reason or 'unspecified'})")
            return path
