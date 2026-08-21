"""The final node that ends the interview."""

from pipecat.flows import FlowManager, NodeConfig

from nodes.session import record_flow, save_session


def create_conclusion_node() -> NodeConfig:
    """Build the final node that closes the interview."""
    return NodeConfig(
        name="conclusion",
        task_messages=[
            {
                "role": "developer",
                "content": (
                    "The interview is over. In one or two short natural sentences, say you're "
                    "happy to call the interview here and thank them for their time. Do not ask "
                    "any questions or open a new topic."
                ),
            }
        ],
        post_actions=[
            {"type": "function", "handler": _record_end_conversation},
            {"type": "end_conversation"},
        ],
    )


async def _record_end_conversation(action: dict, flow_manager: FlowManager) -> None:
    """Record and save the session before the transport disconnects."""
    record_flow("end_conversation", {"node": getattr(flow_manager, "current_node", None)})
    save_session(reason="end_conversation")
