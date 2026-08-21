"""Shared session-recording helpers for interview node transitions."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from session_recorder import SessionRecorder


_session_recorder: SessionRecorder | None = None


def set_session_recorder(recorder: SessionRecorder | None) -> None:
    """Attach the recorder used to log flow transitions for one session."""
    global _session_recorder
    _session_recorder = recorder


def record_flow(event: str, data: dict | None = None) -> None:
    """Record a flow event when a session recorder is active."""
    if _session_recorder is not None:
        _session_recorder.record(event, data)


def save_session(*, reason: str) -> None:
    """Persist the active session log, if one exists."""
    if _session_recorder is not None:
        _session_recorder.save(reason=reason)
