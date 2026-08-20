"""Application configuration and environment loading for the voice bot."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load the conventional `.env` file first, then let either local filename
# override it. This supports both `env.local` and `.env.local` without
# requiring developers to rename an existing local secrets file.
load_dotenv(".env", override=False)
load_dotenv("env.local", override=True)
load_dotenv(".env.local", override=True)


@dataclass(frozen=True)
class BotConfig:
    """The provider credentials and model settings used by one bot session."""

    deepgram_api_key: str
    groq_api_key: str
    stt_model: str = "nova-3"
    stt_language: str = "en-US"
    tts_voice: str = "aura-2-thalia-en"
    llm_model: str = "openai/gpt-oss-120b"
    llm_temperature: float = 0.4
    llm_max_completion_tokens: int = 512
    llm_reasoning_effort: str = "low"


def get_bot_config() -> BotConfig:
    """Read provider credentials and stable model defaults from the environment."""
    return BotConfig(
        deepgram_api_key=os.getenv("DEEPGRAM_API_KEY", ""),
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
    )
