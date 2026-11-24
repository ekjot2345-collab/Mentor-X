"""Progressive, guardrailed hint selection."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .struggle_detector import MentoringMode


@dataclass(frozen=True)
class HintResponse:
    problem_id: str
    level: int
    stage: str
    text: str
    mentor_message: str


class HintEngine:
    """Loads author-written hints and releases at most one level per request."""

    def __init__(self, hints_path: Path | None = None) -> None:
        self._hints_path = hints_path or Path(__file__).resolve().parents[1] / "data" / "hints.json"
        self._problems = self._load_problems()

    def get_problem(self, problem_id: str) -> dict:
        try:
            return self._problems[problem_id]
        except KeyError as error:
            raise ValueError(f"Unknown problem_id: {problem_id}") from error

    def get_next_hint(
        self,
        *,
        problem_id: str,
        current_level: int,
        mode: MentoringMode,
    ) -> HintResponse | None:
        """Return only the next hint. The engine never skips to a final solution."""
        problem = self.get_problem(problem_id)
        next_level = current_level + 1
        hints = problem["hints"]

        if next_level > len(hints):
            return None

        hint = next(item for item in hints if item["level"] == next_level)
        return HintResponse(
            problem_id=problem_id,
            level=hint["level"],
            stage=hint["stage"],
            text=hint["text"],
            mentor_message=self._message_for(mode),
        )

    def analyze_problem_hints(self, problem_id: str) -> dict:
        """Run a conservative quality preflight over author-written hint content.

        This checks structure and possible early answer leakage. It cannot prove a
        hint improves learning; that requires learner feedback gathered in use.
        """
        problem = self.get_problem(problem_id)
        hints = problem["hints"]
        expected_levels = list(range(1, 6))
        levels = [hint.get("level") for hint in hints]
        early_text = " ".join(hint.get("text", "").lower() for hint in hints[:2])
        code_markers = ("for (", "while (", "return ", "def ", "function ", "```")
        leakage_warnings = [marker.strip() for marker in code_markers if marker in early_text]
        question_in_reflect = "?" in hints[0].get("text", "") if hints else False

        checks = {
            "five_progressive_levels": levels == expected_levels,
            "reflective_first_hint": question_in_reflect,
            "no_code_like_content_in_early_hints": not leakage_warnings,
            "all_hints_have_text": all(bool(hint.get("text", "").strip()) for hint in hints),
        }
        passed = sum(checks.values())
        return {
            "problem_id": problem_id,
            "quality_score": round((passed / len(checks)) * 100),
            "checks": checks,
            "warnings": (
                ["Early hints may reveal implementation details: " + ", ".join(leakage_warnings)]
                if leakage_warnings
                else []
            ),
            "note": "This is a content-quality preflight. Validate real usefulness with learner feedback after each hint.",
        }

    def list_problems(self) -> list[dict]:
        return [
            {
                "id": problem["id"],
                "title": problem["title"],
                "topic": problem["topic"],
                "difficulty": problem["difficulty"],
            }
            for problem in self._problems.values()
        ]

    def _load_problems(self) -> dict[str, dict]:
        with self._hints_path.open(encoding="utf-8") as hints_file:
            payload = json.load(hints_file)
        problems = {problem["id"]: problem for problem in payload["problems"]}
        if not problems:
            raise ValueError("hints.json must contain at least one problem")
        return problems

    @staticmethod
    def _message_for(mode: MentoringMode) -> str:
        messages = {
            MentoringMode.MOMENTUM: "You have momentum. Try this one small thought before asking for more help.",
            MentoringMode.GENTLE_PAUSE: "Let’s narrow the problem without taking the solution away from you.",
            MentoringMode.GUIDED_RESET: "Let’s reset with one manageable step. You are still doing the thinking.",
        }
        return messages[mode]
