"""Conversation nodes and actions for the starter Pipecat Flow."""

from loguru import logger
from pipecat.flows import FlowManager, NodeConfig


async def record_color(flow_manager: FlowManager, color: str) -> tuple[str, NodeConfig]:
    """Log the user's favorite color and transition to the goodbye node."""
    logger.info("User's favorite color: {}", color)
    return color, create_goodbye_node()


def create_greeting_node() -> NodeConfig:
    """Build the first node that greets the user and asks for their favorite color."""
    return NodeConfig(
        name="greeting",
        role_message=(
            "You are a friendly voice assistant. Be brief. "
            "Ask for the user's favorite color, then use record_color."
        ),
        task_messages=[
            {
                "role": "developer",
                "content": "Say hello and ask the user for their favorite color.",
            }
        ],
        functions=[record_color],
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
