"""Conversation nodes and actions for the interview flow."""

from loguru import logger
from pipecat.flows import FlowManager, NodeConfig

# In production this comes from the DB and is injected per session.
# Keep the full problem text here so Discussion can put it in LLM context
# without the bot reading it aloud.
INTERVIEW_QUESTION_MD = """
# Climbing Stairs

You are climbing a staircase. It takes `n` steps to reach the top.

Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?

## Example 1

**Input:** `n = 2`
**Output:** `2`

**Explanation:** There are two ways to climb to the top.
1. 1 step + 1 step
2. 2 steps

## Example 2

**Input:** `n = 3`
**Output:** `3`

**Explanation:** There are three ways to climb to the top.
1. 1 step + 1 step + 1 step
2. 1 step + 2 steps
3. 2 steps + 1 step

## Constraints

- `1 <= n <= 45`
""".strip()


async def start_interview(flow_manager: FlowManager) -> tuple[None, NodeConfig]:
    """Call when the user confirms they are ready to begin the interview."""
    logger.info("User is ready — transitioning to discussion")
    return None, create_discussion_node()


async def conclude_interview(flow_manager: FlowManager) -> tuple[None, NodeConfig]:
    """Call after answering one candidate question, then move to conclusion."""
    logger.info("One Q&A complete — transitioning to conclusion")
    return None, create_conclusion_node()


def create_intro_node() -> NodeConfig:
    """Greet the user and wait for them to signal they are ready to start."""
    return NodeConfig(
        name="Intro",
        role_message=(
            "You are a calm, professional technical interview coach. "
            "Speak briefly and naturally — your words are spoken aloud, "
            "so avoid lists, markdown, code, or special characters. "
            "You must use the available function to progress when appropriate."
        ),
        task_messages=[
            {
                "role": "developer",
                "content": (
                    "Greet the candidate warmly in one short sentence, then ask "
                    "if they are ready to begin the interview. "
                    "Wait for a clear yes or confirmation. "
                    "When they confirm, call start_interview. "
                    "If they are not ready or ask a quick clarifying question, "
                    "answer briefly and ask again when they are ready."
                ),
            }
        ],
        functions=[start_interview],
    )


def create_discussion_node() -> NodeConfig:
    """Introduce the coding problem; full text is context-only, not read aloud."""
    return NodeConfig(
        name="Discussion",
        task_messages=[
            {
                "role": "developer",
                "content": (
                    "You are now in the discussion phase of the interview.\n\n"
                    "The full coding problem for this round is below. It is for YOUR "
                    "context only — do NOT read it aloud word-for-word, do NOT recite "
                    "examples or constraints, and do NOT dump the full prompt.\n\n"
                    "FIRST TURN (opening): do only the following, briefly:\n"
                    "1. Introduce that you have a coding problem for them (climbing stairs / "
                    "counting distinct ways with 1- or 2-step moves).\n"
                    "2. Summarize what is expected in one or two short sentences.\n"
                    "3. Tell them the full question is now available in the left panel, "
                    "so they should read it through carefully there and let you know "
                    "if they have any questions.\n"
                    "Then stop and wait.\n\n"
                    "AFTER the candidate asks one question: answer it helpfully and briefly "
                    "in plain speech (no code dumps unless they specifically ask for a "
                    "tiny clarifying detail). Then immediately call conclude_interview. "
                    "Do not invite more questions. Do not stay in this phase for a second Q&A.\n\n"
                    "--- FULL PROBLEM (context only) ---\n"
                    f"{INTERVIEW_QUESTION_MD}"
                ),
            }
        ],
        functions=[conclude_interview],
    )


def create_conclusion_node() -> NodeConfig:
    """Wrap up the interview, then disconnect the call."""
    return NodeConfig(
        name="Conclusion",
        task_messages=[
            {
                "role": "developer",
                "content": (
                    "The interview is over. In one or two short natural sentences, "
                    "say you're happy to call the interview here and thank them for "
                    "their time. Do not ask any questions. Do not open a new topic."
                ),
            }
        ],
        post_actions=[
            {
                "type": "end_conversation",
            }
        ],
    )


# Back-compat alias if anything still imports the old name.
create_greeting_node = create_intro_node
