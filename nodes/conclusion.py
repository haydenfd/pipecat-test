"""The final node that ends the interview."""

from pipecat.flows import NodeConfig


def create_conclusion_node() -> NodeConfig:
    """Build the final node that closes the interview."""
    return NodeConfig(
        name="conclusion",
        task_messages=[
            {"role": "developer", "content": "Thank the user and conclude the interview."}
        ],
        post_actions=[{"type": "end_conversation"}],
    )
