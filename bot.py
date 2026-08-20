"""Pipecat bot entrypoint and SmallWebRTC pipeline orchestration."""

from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.flows import FlowManager
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineParams, PipelineWorker
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.workers.runner import WorkerRunner

from config import get_bot_config
from flow import create_intro_node
from services import create_services


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments) -> None:
    """Assemble the audio pipeline, wire FlowManager, and run one bot worker."""
    services = create_services(get_bot_config())
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
            services.stt,
            context_aggregator.user(),
            services.llm,
            services.tts,
            transport.output(),
            context_aggregator.assistant(),
        ]
    )
    worker = PipelineWorker(
        pipeline,
        params=PipelineParams(
            allow_interruptions=False,
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        idle_timeout_secs=runner_args.pipeline_idle_timeout_secs,
    )
    flow_manager = FlowManager(
        worker=worker,
        llm=services.llm,
        context_aggregator=context_aggregator,
        transport=transport,
    )

    # Start Intro only after SmallWebRTC has finished connecting.
    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport: BaseTransport, client) -> None:
        """Initialize the conversation when a browser client joins the session."""
        logger.info("Client connected")
        await flow_manager.initialize(create_intro_node())

    # Cancel the worker when the browser disconnects so the next session starts cleanly.
    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport: BaseTransport, client) -> None:
        """Stop the session worker and release its pipeline resources."""
        logger.info("Client disconnected")
        await worker.cancel()

    # WorkerRunner owns the event loop and keeps the pipeline alive until shutdown.
    runner = WorkerRunner(handle_sigint=runner_args.handle_sigint)
    await runner.add_workers(worker)
    await runner.run()


async def bot(runner_args: RunnerArguments) -> None:
    """Create the audio-only SmallWebRTC transport for the Pipecat runner."""
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
    # The Pipecat development runner exposes /api/offer and starts the server.
    from pipecat.runner.run import main

    main()
