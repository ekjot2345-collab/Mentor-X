"""Curated example questions and their explanation concepts."""

from __future__ import annotations

import json
from pathlib import Path


class QuestionBank:
    def __init__(self, questions_path: Path | None = None) -> None:
        path = questions_path or Path(__file__).resolve().parents[1] / "data" / "practice_questions.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        self._questions = {question["id"]: question for question in payload["questions"]}

    def list_questions(self) -> list[dict]:
        return list(self._questions.values())

    def get_question(self, question_id: str) -> dict:
        try:
            return self._questions[question_id]
        except KeyError as error:
            raise ValueError(f"Unknown question_id: {question_id}") from error
