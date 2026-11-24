"""Explainable, rule-based struggle detection for MentorX.

This is the initial MVP baseline. It deliberately uses transparent rules instead
of a trained model, so every recommendation can be explained to the learner.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MentoringMode(str, Enum):
    """The amount and style of intervention MentorX should use."""

    MOMENTUM = "momentum"
    GENTLE_PAUSE = "gentle_pause"
    GUIDED_RESET = "guided_reset"


@dataclass(frozen=True)
class FrictionAssessment:
    """An explainable recommendation produced from a learner's session signals."""

    score: int
    mode: MentoringMode
    recommended_action: str
    reasons: tuple[str, ...]


class StruggleDetector:
    """Converts observable learning signals into a non-judgmental nudge level.

    The score estimates whether a mentoring nudge may be useful. It does not
    measure intelligence, ability, or emotion.
    """

    MAX_MINUTES_STUCK = 45
    MAX_REPEATED_ATTEMPTS = 4
    MAX_HINT_REQUESTS = 3
    MAX_BREAKTHROUGHS = 2

    TIME_WEIGHT = 34
    RETRY_WEIGHT = 28
    HINT_WEIGHT = 28
    RECOVERY_CREDIT = 18

    GENTLE_PAUSE_THRESHOLD = 45
    GUIDED_RESET_THRESHOLD = 72

    def assess(
        self,
        *,
        minutes_stuck: float,
        repeated_attempts: int,
        hint_requests: int,
        breakthroughs: int,
    ) -> FrictionAssessment:
        """Return a score, intervention mode, and human-readable reasons.

        Inputs are session events collected with the learner's knowledge. The
        values are capped for scoring so a very long session cannot dominate
        every other signal.
        """

        self._validate_non_negative(
            minutes_stuck=minutes_stuck,
            repeated_attempts=repeated_attempts,
            hint_requests=hint_requests,
            breakthroughs=breakthroughs,
        )

        score = round(
            self._weighted_signal(minutes_stuck, self.MAX_MINUTES_STUCK, self.TIME_WEIGHT)
            + self._weighted_signal(repeated_attempts, self.MAX_REPEATED_ATTEMPTS, self.RETRY_WEIGHT)
            + self._weighted_signal(hint_requests, self.MAX_HINT_REQUESTS, self.HINT_WEIGHT)
            - self._weighted_signal(breakthroughs, self.MAX_BREAKTHROUGHS, self.RECOVERY_CREDIT)
        )
        score = max(0, min(100, score))
        mode, action = self._recommendation_for(score)

        return FrictionAssessment(
            score=score,
            mode=mode,
            recommended_action=action,
            reasons=self._reasons_for(
                minutes_stuck=minutes_stuck,
                repeated_attempts=repeated_attempts,
                hint_requests=hint_requests,
                breakthroughs=breakthroughs,
            ),
        )

    @staticmethod
    def _weighted_signal(value: float, maximum: float, weight: int) -> float:
        return min(value / maximum, 1) * weight

    @staticmethod
    def _validate_non_negative(**signals: float | int) -> None:
        invalid = [name for name, value in signals.items() if value < 0]
        if invalid:
            raise ValueError(f"Signals cannot be negative: {', '.join(invalid)}")

    def _recommendation_for(self, score: int) -> tuple[MentoringMode, str]:
        if score >= self.GUIDED_RESET_THRESHOLD:
            return (
                MentoringMode.GUIDED_RESET,
                "Pause the solution path and ask the learner to name the input, target, and one useful lookup.",
            )
        if score >= self.GENTLE_PAUSE_THRESHOLD:
            return (
                MentoringMode.GENTLE_PAUSE,
                "Ask one focused question that narrows the search space without revealing the technique.",
            )
        return (
            MentoringMode.MOMENTUM,
            "Invite the learner to explain or sketch their approach before writing code.",
        )

    @staticmethod
    def _reasons_for(
        *,
        minutes_stuck: float,
        repeated_attempts: int,
        hint_requests: int,
        breakthroughs: int,
    ) -> tuple[str, ...]:
        reasons: list[str] = []
        if minutes_stuck > 0:
            reasons.append(f"{minutes_stuck:g} minutes spent on this problem")
        if repeated_attempts > 0:
            reasons.append(f"{repeated_attempts} repeated attempt(s)")
        if hint_requests > 0:
            reasons.append(f"{hint_requests} hint request(s)")
        if breakthroughs > 0:
            reasons.append(f"{breakthroughs} recovery signal(s) reduced the score")
        return tuple(reasons) or ("No friction signals have been logged yet",)
