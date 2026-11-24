import unittest

from models.hint_engine import HintEngine
from models.struggle_detector import MentoringMode


class HintEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = HintEngine()

    def test_releases_only_the_next_level(self) -> None:
        hint = self.engine.get_next_hint(
            problem_id="two-sum", current_level=2, mode=MentoringMode.GENTLE_PAUSE
        )

        self.assertEqual(hint.level, 3)
        self.assertEqual(hint.stage, "Sketch")

    def test_does_not_return_a_sixth_hint(self) -> None:
        hint = self.engine.get_next_hint(
            problem_id="two-sum", current_level=5, mode=MentoringMode.GUIDED_RESET
        )

        self.assertIsNone(hint)

    def test_hint_quality_preflight_passes_for_all_sample_problems(self) -> None:
        for problem in self.engine.list_problems():
            analysis = self.engine.analyze_problem_hints(problem["id"])
            self.assertTrue(analysis["checks"]["five_progressive_levels"])
            self.assertTrue(analysis["checks"]["all_hints_have_text"])
