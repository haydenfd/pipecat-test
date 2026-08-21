"""The node that asks the user to describe their approach."""

from loguru import logger
from pipecat.flows import FlowManager, NodeConfig

from nodes.complexity_followup import create_complexity_followup_node


async def record_approach(flow_manager: FlowManager, approach: str) -> tuple[str, NodeConfig]:
    """Record the discussed approach and advance to the complexity question."""
    logger.info("User's approach: {}", approach)
    return approach, create_complexity_followup_node()


def create_discussion_node() -> NodeConfig:
    """Build the node that captures the user's proposed approach."""
    return NodeConfig(
        name="discussion",
        role_message=(
            "You are a concise technical interviewer. Ask the user to explain "
            "the approach they built. After they answer, use record_approach."
        ),
        task_messages=[
            {
                "role": "developer",
                "content": "Ask the user to describe their approach.",
            }
        ],
        functions=[record_approach],
    )
