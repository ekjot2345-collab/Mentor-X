"""Route-function tests without opening a local network socket."""

import unittest

from app import ExplanationRequest, StartSessionRequest, evaluate_explanation, hint_analysis, next_hint, start_session


class MentorXApiTests(unittest.TestCase):
    def test_session_can_request_progressive_hint(self) -> None:
        created = start_session(StartSessionRequest(learner_name="Aanya", problem_id="two-sum"))

        response = next_hint(created["session"]["session_id"])

        self.assertEqual(response["hint"]["level"], 1)
        self.assertEqual(response["session"]["current_hint_level"], 1)

    def test_hint_analysis_reports_progressive_content(self) -> None:
        response = hint_analysis("two-sum")

        self.assertTrue(response["checks"]["five_progressive_levels"])

    def test_session_explanation_is_evaluated(self) -> None:
        created = start_session(StartSessionRequest(learner_name="Aanya", problem_id="two-sum"))
        response = evaluate_explanation(
            created["session"]["session_id"],
            ExplanationRequest(explanation="Use a hash map to find the complement in one scan with O(n) time."),
        )

        self.assertGreater(response["score"], 0)
