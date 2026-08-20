"""Conversation nodes and actions for the starter Pipecat Flow."""

from loguru import logger
from pipecat.flows import FlowManager, NodeConfig


async def record_like(flow_manager: FlowManager, liked: bool) -> tuple[str, NodeConfig]:
    """Record the user's yes/no answer and transition to the goodbye node."""
    logger.info("User likes this: {}", liked)
    return "liked" if liked else "not liked", create_goodbye_node()


def create_greeting_node() -> NodeConfig:
    """Build the first node that greets the user and asks the starter question."""
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
    """Build the final node that thanks the user and closes the conversation."""
    return NodeConfig(
        name="goodbye",
        task_messages=[
            {"role": "developer", "content": "Thank the user and say goodbye."}
        ],
        post_actions=[{"type": "end_conversation"}],
    )
