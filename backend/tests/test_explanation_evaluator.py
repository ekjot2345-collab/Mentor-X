import unittest

from models.explanation_evaluator import ExplanationEvaluator
from models.question_bank import QuestionBank


class ExplanationEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evaluator = ExplanationEvaluator(QuestionBank())

    def test_complete_two_sum_explanation_scores_as_strong(self) -> None:
        explanation = (
            "I scan the array in one pass and keep a hash map from each value to its index. "
            "For each value, I calculate its complement as target minus the current value. "
            "If the complement is already in the lookup, I return both indices. "
            "This is O(n) because each value is processed once."
        )

        evaluation = self.evaluator.evaluate("two-sum", explanation)

        self.assertGreaterEqual(evaluation.score, 75)
        self.assertEqual(evaluation.level, "strong")

    def test_short_explanation_requests_reflection(self) -> None:
        evaluation = self.evaluator.evaluate("two-sum", "I would use a loop.")

        self.assertLess(evaluation.score, 50)
        self.assertEqual(evaluation.level, "needs_reflection")

    def test_question_bank_has_eighteen_examples(self) -> None:
        self.assertEqual(len(QuestionBank().list_questions()), 18)
