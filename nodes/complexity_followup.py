"""The node that asks for the approach's time and space complexity."""

from loguru import logger
from pipecat.flows import FlowManager, NodeConfig

from nodes.conclusion import create_conclusion_node


async def record_complexity(
    flow_manager: FlowManager, time_complexity: str, space_complexity: str
) -> tuple[str, NodeConfig]:
    """Record the user's Big-O answer and advance to the conclusion."""
    logger.info(
        "User's complexity answer — time: {}, space: {}",
        time_complexity,
        space_complexity,
    )
    return "complexity recorded", create_conclusion_node()


def create_complexity_followup_node() -> NodeConfig:
    """Build the one-question follow-up about the discussed approach's Big-O."""
    return NodeConfig(
        name="complexity_followup",
        task_messages=[
            {
                "role": "developer",
                "content": (
                    "Ask once: What are the time and space complexities of the "
                    "approach you just described? After the user answers, use "
                    "record_complexity. Do not evaluate, correct, or ask follow-up "
                    "questions."
                ),
            }
        ],
        functions=[record_complexity],
    )
