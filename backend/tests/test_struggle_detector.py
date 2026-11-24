import unittest

from models.struggle_detector import MentoringMode, StruggleDetector


class StruggleDetectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.detector = StruggleDetector()

    def test_no_signals_means_momentum(self) -> None:
        assessment = self.detector.assess(
            minutes_stuck=0,
            repeated_attempts=0,
            hint_requests=0,
            breakthroughs=0,
        )

        self.assertEqual(assessment.score, 0)
        self.assertEqual(assessment.mode, MentoringMode.MOMENTUM)

    def test_multiple_signals_trigger_guided_reset(self) -> None:
        assessment = self.detector.assess(
            minutes_stuck=45,
            repeated_attempts=4,
            hint_requests=3,
            breakthroughs=0,
        )

        self.assertEqual(assessment.score, 90)
        self.assertEqual(assessment.mode, MentoringMode.GUIDED_RESET)

    def test_breakthrough_reduces_the_score(self) -> None:
        without_recovery = self.detector.assess(
            minutes_stuck=38,
            repeated_attempts=2,
            hint_requests=1,
            breakthroughs=0,
        )
        with_recovery = self.detector.assess(
            minutes_stuck=38,
            repeated_attempts=2,
            hint_requests=1,
            breakthroughs=2,
        )

        self.assertLess(with_recovery.score, without_recovery.score)

    def test_negative_signals_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.detector.assess(
                minutes_stuck=-1,
                repeated_attempts=0,
                hint_requests=0,
                breakthroughs=0,
            )


if __name__ == "__main__":
    unittest.main()
