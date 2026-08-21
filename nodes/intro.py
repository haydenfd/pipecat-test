"""The node that starts the technical interview."""

from loguru import logger
from pipecat.flows import FlowManager, NodeConfig

from nodes.discussion import create_discussion_node
from nodes.session import record_flow


async def start_interview(flow_manager: FlowManager) -> tuple[None, NodeConfig]:
    """Advance from the ready check to the problem discussion."""
    logger.info("User is ready — transitioning to discussion")
    from_node = getattr(flow_manager, "current_node", None) or "intro"
    record_flow("flow_transition", {"from": from_node, "to": "discussion", "via": "start_interview"})
    record_flow("flow_node_entered", {"node": "discussion"})
    return None, create_discussion_node()


def create_intro_node() -> NodeConfig:
    """Greet the user and wait for confirmation to begin."""
    return NodeConfig(
        name="intro",
        role_message=(
            "You are a software engineering technical interviewer conducting a live voice interview.\n\n"
            "Act like a thoughtful human interviewer. Let the candidate drive the solution. "
            "Listen to their reasoning and use it to guide how you respond.\n\n"
            "Do not reveal the solution, provide the final algorithm, or solve the problem "
            "for the candidate. When the candidate needs help, prefer the smallest useful "
            "hint rather than giving away the answer.\n\n"
            "Ask one question at a time.\n\n"
            "Prefer concise responses when a short response is sufficient, but use "
            "additional explanation when it is genuinely useful.\n\n"
            "Everything you write will be spoken aloud. Write for listening, not for reading. "
            "Express technical notation and code naturally for text-to-speech.\n\n"
            "Do not use markdown, code fences, bullets, headings, tables, or other visual formatting."
        ),
        task_messages=[
            {
                "role": "developer",
                "content": (
                    "Greet the candidate warmly in one short sentence, then ask if they are ready "
                    "to begin the interview. Wait for a clear yes or confirmation. When they "
                    "confirm, call start_interview. If they are not ready or ask a quick clarifying "
                    "question, answer briefly and ask again when they are ready."
                ),
            }
        ],
        functions=[start_interview],
    )
