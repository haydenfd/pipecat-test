"""Unit tests for the interview flow transitions."""

import asyncio
import unittest

from nodes import (
    create_complexity_followup_node,
    create_discussion_node,
    record_complexity,
    start_complexity_followup,
)


class InterviewFlowTests(unittest.TestCase):
    def test_discussion_transitions_to_complexity_followup(self) -> None:
        _, next_node = asyncio.run(start_complexity_followup(None))

        self.assertEqual(next_node["name"], "complexity_followup")

    def test_complexity_followup_requests_both_big_o_values(self) -> None:
        node = create_complexity_followup_node()
        prompt = node["task_messages"][0]["content"].lower()

        self.assertEqual(node["name"], "complexity_followup")
        self.assertIn("time", prompt)
        self.assertIn("space", prompt)
        self.assertIn("record_complexity", prompt)

    def test_complexity_answer_transitions_to_conclusion(self) -> None:
        _, next_node = asyncio.run(record_complexity(None, "O(n)", "O(1)"))

        self.assertEqual(next_node["name"], "conclusion")
        self.assertEqual(next_node["post_actions"][-1], {"type": "end_conversation"})

    def test_discussion_exposes_the_approach_transition(self) -> None:
        node = create_discussion_node()

        self.assertEqual(node["functions"], [start_complexity_followup])


if __name__ == "__main__":
    unittest.main()
