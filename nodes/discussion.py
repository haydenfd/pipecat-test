"""The node where the candidate discusses their solution approach."""

from loguru import logger
from pipecat.flows import ContextStrategy, ContextStrategyConfig, FlowManager, NodeConfig

from nodes.complexity_followup import create_complexity_followup_node
from nodes.session import record_flow


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


async def start_complexity_followup(flow_manager: FlowManager) -> tuple[None, NodeConfig]:
    """Advance after the candidate has finished discussing their approach."""
    logger.info("Candidate approach is ready — transitioning to complexity follow-up")
    from_node = getattr(flow_manager, "current_node", None) or "discussion"
    record_flow(
        "flow_transition",
        {"from": from_node, "to": "complexity_followup", "via": "start_complexity_followup"},
    )
    record_flow("flow_node_entered", {"node": "complexity_followup"})
    return None, create_complexity_followup_node()


def create_discussion_node() -> NodeConfig:
    """Introduce the coding problem and guide the approach discussion."""
    return NodeConfig(
        name="discussion",
        context_strategy=ContextStrategyConfig(strategy=ContextStrategy.RESET),
        task_messages=[
            {
                "role": "developer",
                "content": (
                    "You are now in the discussion phase of the interview.\n\n"
                    "Introduce the coding problem briefly and naturally. Do not dump the full "
                    "prompt or greet the candidate again.\n\n"
                    "The full coding problem for this round is below. It is for YOUR context only — "
                    "do not recite examples or constraints, and do not dump the full prompt.\n\n"
                    "The candidate may ask clarifying questions, propose an approach, revise their "
                    "approach, or ask for guidance. Answer relevant questions and give small hints "
                    "instead of solving the problem for them.\n\n"
                    "Keep the discussion going. Do not call start_complexity_followup after the "
                    "first question or answer. Call it only after the candidate has sufficiently "
                    "discussed a sound approach.\n\n"
                    "--- FULL PROBLEM (context only) ---\n"
                    f"{INTERVIEW_QUESTION_MD}"
                ),
            }
        ],
        functions=[start_complexity_followup],
    )
