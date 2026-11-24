"""Transparent rubric for checking a learner's written explanation."""

from __future__ import annotations

from dataclasses import dataclass, asdict

from .question_bank import QuestionBank


@dataclass(frozen=True)
class ExplanationEvaluation:
    score: int
    level: str
    word_count: int
    matched_concepts: tuple[str, ...]
    missing_concepts: tuple[str, ...]
    feedback: str
    disclaimer: str = "This checks conceptual coverage in writing; it does not prove the learner can implement the solution independently."

    def to_dict(self) -> dict:
        return asdict(self)


class ExplanationEvaluator:
    """Scores concept coverage, clarity, and complexity discussion using a rubric."""

    def __init__(self, question_bank: QuestionBank | None = None) -> None:
        self._question_bank = question_bank or QuestionBank()

    def evaluate(self, question_id: str, explanation: str) -> ExplanationEvaluation:
        question = self._question_bank.get_question(question_id)
        normalized = explanation.lower()
        words = explanation.split()
        groups = question["expected_concepts"]
        matched_groups = [group for group in groups if any(term in normalized for term in group)]
        matched = tuple(group[0] for group in matched_groups)
        missing = tuple(group[0] for group in groups if group not in matched_groups)

        coverage_points = round((len(matched) / len(groups)) * 65)
        clarity_points = 15 if len(words) >= 35 else 8 if len(words) >= 15 else 2
        complexity_points = 10 if "o(" in normalized or "complexity" in normalized else 0
        reasoning_points = 10 if any(word in normalized for word in ("because", "therefore", "so that", "why")) else 0
        score = min(100, coverage_points + clarity_points + complexity_points + reasoning_points)

        if score >= 75:
            level = "strong"
            feedback = "Strong explanation. You covered the key idea; now try implementing it without looking at a hint."
        elif score >= 50:
            level = "developing"
            feedback = "Good direction. Add the missing concept and explain why the method works, not only what it does."
        else:
            level = "needs_reflection"
            feedback = "Start with the main data structure or technique, then explain the decision made at each step."

        return ExplanationEvaluation(
            score=score,
            level=level,
            word_count=len(words),
            matched_concepts=matched,
            missing_concepts=missing,
            feedback=feedback,
        )
