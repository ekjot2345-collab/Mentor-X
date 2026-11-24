"""Train, compare, and save three MentorX demo models."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

try:
    from .generate_synthetic_data import FEATURE_NAMES, generate_sessions, write_csv
except ImportError:  # Supports `python ml/train_models.py` from backend/.
    from generate_synthetic_data import FEATURE_NAMES, generate_sessions, write_csv


ARTIFACT_DIRECTORY = Path(__file__).resolve().parent / "artifacts"


def _metrics(model, x_test, y_test) -> dict[str, float]:
    predictions = model.predict(x_test)
    probabilities = model.predict_proba(x_test)[:, 1]
    return {
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "precision": round(float(precision_score(y_test, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, predictions, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, predictions, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, probabilities)), 4),
    }


def train_models() -> dict:
    """Generate 3,000 synthetic sessions, evaluate three models, save the best."""
    x, y = generate_sessions(count=3_000, seed=42)
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.25, random_state=42, stratify=y
    )

    candidates = {
        "logistic_regression": Pipeline(
            [("scaler", StandardScaler()), ("model", LogisticRegression(max_iter=2_000, random_state=42))]
        ),
        "decision_tree": DecisionTreeClassifier(max_depth=6, min_samples_leaf=12, random_state=42),
        "random_forest": RandomForestClassifier(
            n_estimators=300, max_depth=9, min_samples_leaf=5, random_state=42, n_jobs=-1
        ),
    }

    results: dict[str, dict] = {}
    for name, model in candidates.items():
        model.fit(x_train, y_train)
        results[name] = {"model": model, "metrics": _metrics(model, x_test, y_test)}

    # F1 protects against choosing a model that inflates accuracy by ignoring
    # sessions where a useful nudge is needed. Accuracy breaks close ties.
    selected_name, selected = max(
        results.items(),
        key=lambda item: (item[1]["metrics"]["f1"], item[1]["metrics"]["accuracy"]),
    )

    ARTIFACT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    joblib.dump(selected["model"], ARTIFACT_DIRECTORY / "best_model.joblib")
    write_csv(ARTIFACT_DIRECTORY / "synthetic_sessions.csv", count=3_000, seed=42)

    report = {
        "selected_model": selected_name,
        "selection_metric": "highest validation F1, then accuracy",
        "feature_names": FEATURE_NAMES,
        "dataset": {
            "total_synthetic_sessions": 3_000,
            "training_sessions": len(x_train),
            "held_out_validation_sessions": len(x_test),
            "random_seed": 42,
        },
        "results": {name: result["metrics"] for name, result in results.items()},
        "synthetic_data_notice": (
            "These validation metrics measure fit to simulated data only. "
            "They are not evidence of performance with real students."
        ),
        "real_world_validation_plan": (
            "Collect consented learner feedback after hints, split future data by learner, "
            "and compare model recommendations against the rule-based baseline."
        ),
    }
    (ARTIFACT_DIRECTORY / "model_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    outcome = train_models()
    print(json.dumps(outcome, indent=2))
