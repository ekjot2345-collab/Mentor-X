"""Loads the selected ML model and exposes a safe nudge-probability interface."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import joblib

from .mentor_session import MentorSession
from .struggle_detector import FrictionAssessment, MentoringMode


@dataclass(frozen=True)
class ModelPrediction:
    nudge_probability: float
    mode: MentoringMode
    source: str
    selected_model: str | None


class NudgePredictionService:
    def __init__(self, artifact_directory: Path | None = None) -> None:
        self._artifact_directory = artifact_directory or Path(__file__).resolve().parents[1] / "ml" / "artifacts"
        self._model_path = self._artifact_directory / "best_model.joblib"
        self._report_path = self._artifact_directory / "model_report.json"
        self._model = joblib.load(self._model_path) if self._model_path.exists() else None
        self._report = self._load_report()

    def predict(self, session: MentorSession, fallback: FrictionAssessment) -> ModelPrediction:
        if self._model is None:
            probability = fallback.score / 100
            return ModelPrediction(
                nudge_probability=round(probability, 3),
                mode=fallback.mode,
                source="rule_based_fallback",
                selected_model=None,
            )

        features = session.features()
        values = [[features[name] for name in self._report["feature_names"]]]
        probability = float(self._model.predict_proba(values)[0][1])
        return ModelPrediction(
            nudge_probability=round(probability, 3),
            mode=self._mode_for(probability),
            source="trained_synthetic_model",
            selected_model=self._report["selected_model"],
        )

    def metrics(self) -> dict:
        if not self._report:
            return {"available": False, "message": "Run python ml/train_models.py to train demo models."}
        return {"available": True, **self._report}

    @staticmethod
    def _mode_for(probability: float) -> MentoringMode:
        if probability >= 0.72:
            return MentoringMode.GUIDED_RESET
        if probability >= 0.45:
            return MentoringMode.GENTLE_PAUSE
        return MentoringMode.MOMENTUM

    def _load_report(self) -> dict:
        if not self._report_path.exists():
            return {}
        return json.loads(self._report_path.read_text(encoding="utf-8"))
