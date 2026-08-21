# Pipecat interview flow

A minimal voice assistant with:

- Pipecat Flows for discussing an approach, capturing its time and space
  complexity, and concluding the interview
- SmallWebRTC for browser audio connections
- Deepgram Nova 3 STT and Aura 2 TTS
- Groq `openai/gpt-oss-120b` for the LLM
- Pipecat Voice UI Kit's console template

## Run it

1. Add your keys:

   ```bash
   cp .env.example env.local
   ```

   Set `DEEPGRAM_API_KEY` and `GROQ_API_KEY` in `env.local`.

2. Start both the bot and console UI. This installs Python and Node dependencies automatically:

   ```bash
   make dev
   ```

3. Open [http://localhost:5100](http://localhost:5100), click Connect, and allow microphone access.

The bot listens on `http://127.0.0.1:1212`. The Vite proxy forwards `/api/offer` to it, so the browser does not need separate connection or signaling code.

You can override the ports if needed:

```bash
make dev BOT_PORT=1213 CLIENT_PORT=5101
```
