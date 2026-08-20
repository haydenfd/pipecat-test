"""Speech and language-model service construction."""

from dataclasses import dataclass

from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.deepgram.tts import DeepgramTTSService
from pipecat.services.groq.llm import GroqLLMService

from config import BotConfig


@dataclass(frozen=True)
class BotServices:
    """The three provider services that make up the voice pipeline."""

    stt: DeepgramSTTService
    tts: DeepgramTTSService
    llm: GroqLLMService


def create_services(config: BotConfig) -> BotServices:
    """Create Deepgram speech services and the Groq GPT-OSS language model."""
    stt = DeepgramSTTService(
        api_key=config.deepgram_api_key,
        settings=DeepgramSTTService.Settings(
            model=config.stt_model,
            language=config.stt_language,
            # Preserve spoken fillers such as "uh" and "um" in transcripts.
            extra={"filler_words": True},
        ),
    )
    tts = DeepgramTTSService(
        api_key=config.deepgram_api_key,
        settings=DeepgramTTSService.Settings(voice=config.tts_voice),
    )
    llm = GroqLLMService(
        api_key=config.groq_api_key,
        settings=GroqLLMService.Settings(
            model=config.llm_model,
            temperature=config.llm_temperature,
            max_completion_tokens=config.llm_max_completion_tokens,
            extra={"reasoning_effort": config.llm_reasoning_effort},
        ),
    )
    return BotServices(stt=stt, tts=tts, llm=llm)
