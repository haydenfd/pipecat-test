"""Minimal Pipecat Flows bot with the built-in SmallWebRTC dev runner."""

import os

from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.flows import FlowManager, NodeConfig
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineParams, PipelineWorker
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.deepgram.tts import DeepgramTTSService
from pipecat.services.groq.llm import GroqLLMService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.workers.runner import WorkerRunner

# Prefer local developer files, while keeping `.env` as a fallback.
load_dotenv(".env", override=False)
load_dotenv("env.local", override=True)
load_dotenv(".env.local", override=True)


async def record_like(flow_manager: FlowManager, liked: bool) -> tuple[str, NodeConfig]:
    """Handle the user's answer and move to the short goodbye node."""
    logger.info("User likes this: {}", liked)
    return "liked" if liked else "not liked", create_goodbye_node()


def create_greeting_node() -> NodeConfig:
    return NodeConfig(
        name="greeting",
        role_message=(
            "You are a friendly voice assistant. Be brief. "
            "Ask whether the user likes Pipecat, then use record_like."
        ),
        task_messages=[
            {
                "role": "developer",
                "content": "Say hello and ask if the user likes Pipecat.",
            }
        ],
        functions=[record_like],
    )


def create_goodbye_node() -> NodeConfig:
    return NodeConfig(
        name="goodbye",
        task_messages=[
            {
                "role": "developer",
                "content": "Thank the user and say goodbye.",
            }
        ],
        post_actions=[{"type": "end_conversation"}],
    )


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments) -> None:
    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY", ""),
        settings=DeepgramSTTService.Settings(model="nova-3", language="en-US"),
    )
    tts = DeepgramTTSService(
        api_key=os.getenv("DEEPGRAM_API_KEY", ""),
        settings=DeepgramTTSService.Settings(voice="aura-2-thalia-en"),
    )
    llm = GroqLLMService(
        api_key=os.getenv("GROQ_API_KEY", ""),
        settings=GroqLLMService.Settings(
            model="openai/gpt-oss-120b",
            temperature=0.4,
            max_completion_tokens=512,
            extra={
                "reasoning_effort": "low",
            },
        ),
    )

    context = LLMContext()
    context_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=SileroVADAnalyzer(),
            filter_incomplete_user_turns=True,
        ),
    )
    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            context_aggregator.user(),
            llm,
            tts,
            transport.output(),
            context_aggregator.assistant(),
        ]
    )
    worker = PipelineWorker(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        idle_timeout_secs=runner_args.pipeline_idle_timeout_secs,
    )
    flow_manager = FlowManager(
        worker=worker,
        llm=llm,
        context_aggregator=context_aggregator,
        transport=transport,
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport: BaseTransport, client) -> None:
        logger.info("Client connected")
        await flow_manager.initialize(create_greeting_node())

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport: BaseTransport, client) -> None:
        logger.info("Client disconnected")
        await worker.cancel()

    runner = WorkerRunner(handle_sigint=runner_args.handle_sigint)
    await runner.add_workers(worker)
    await runner.run()


async def bot(runner_args: RunnerArguments) -> None:
    transport = await create_transport(
        runner_args,
        {
            "webrtc": lambda: TransportParams(
                audio_in_enabled=True,
                audio_in_stream_on_start=True,
                audio_out_enabled=True,
                video_in_enabled=False,
                video_out_enabled=False,
            )
        },
    )
    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
