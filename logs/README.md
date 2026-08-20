# Session logs

One JSON file is written per bot call when the session ends.

## Filename

```
MMM_DD_YYYY_<NUMBER>.json
```

Example: `AUG_20_2026_001.json`

- Date is the local calendar day when the file is saved.
- `<NUMBER>` is the first unused three-digit sequence for that day (`001`, `002`, …).
- Existing files are never overwritten.

## JSON shape

```json
{
  "session_id": "uuid",
  "started_at": "ISO-8601 timestamp",
  "ended_at": "ISO-8601 timestamp",
  "events": [
    {
      "timestamp": "ISO-8601 timestamp",
      "event": "user_transcript",
      "data": { "text": "..." }
    }
  ],
  "conversation_history": []
}
```

`conversation_history` is included when the session’s `LLMContext` is available at save time.

## Event types

| Event | Meaning |
| --- | --- |
| `session_started` | Recorder started for this call |
| `client_connected` / `client_disconnected` | SmallWebRTC client lifecycle |
| `flow_node_entered` | Flow entered Intro, Discussion, or Conclusion |
| `flow_transition` | Flow moved between nodes |
| `user_transcript` | Final user transcription |
| `assistant_response` | Full assistant/LLM text for one response |
| `user_started_speaking` / `user_stopped_speaking` | User VAD speech boundaries |
| `bot_started_speaking` / `bot_stopped_speaking` | Bot speech boundaries |
| `metrics` | Pipeline metrics / token usage when emitted |
| `error` | Pipeline error frame |
| `end_conversation` | Flow `end_conversation` action |
| `pipeline_end` / `pipeline_cancel` | Pipeline `EndFrame` / `CancelFrame` |
| `session_ended` | Log finalized (includes `reason`) |

Logs are server-side only. They do not include browser/UI events, raw audio, API keys, or transport signaling.
