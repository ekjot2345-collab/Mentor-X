"""Create reproducible synthetic mentoring-session data for a demo only."""

from __future__ import annotations

import csv
from math import exp
from pathlib import Path

import numpy as np


FEATURE_NAMES = [
    "minutes_stuck",
    "repeated_attempts",
    "hint_requests",
    "breakthroughs",
    "current_hint_level",
    "difficulty",
]


def generate_sessions(count: int = 3_000, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Return sessions and `nudge_needed` labels from a documented simulation.

    The relationship intentionally includes noise and a small interaction so
    training several model families is meaningful. These labels are simulated,
    not student evidence.
    """
    generator = np.random.default_rng(seed)
    minutes = np.clip(generator.gamma(shape=2.1, scale=12, size=count), 0, 75)
    retries = np.clip(generator.poisson(lam=1.8, size=count), 0, 7)
    hints = np.clip(generator.poisson(lam=1.1, size=count), 0, 5)
    breakthroughs = np.clip(generator.poisson(lam=0.65, size=count), 0, 3)
    current_level = generator.integers(0, 5, size=count)
    difficulty = generator.integers(1, 4, size=count)

    nonlinear_stuck_pattern = ((minutes > 32) & (retries >= 2)).astype(float) * 0.55
    log_odds = (
        -3.1
        + 0.060 * minutes
        + 0.48 * retries
        + 0.54 * hints
        - 1.05 * breakthroughs
        + 0.24 * difficulty
        + 0.12 * current_level
        + nonlinear_stuck_pattern
        + generator.normal(0, 0.72, count)
    )
    probabilities = 1 / (1 + np.exp(-log_odds))
    labels = generator.binomial(1, probabilities)
    features = np.column_stack((minutes, retries, hints, breakthroughs, current_level, difficulty))
    return features, labels


def write_csv(output_path: Path, count: int = 3_000, seed: int = 42) -> Path:
    features, labels = generate_sessions(count=count, seed=seed)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(output_file)
        writer.writerow([*FEATURE_NAMES, "nudge_needed"])
        for row, label in zip(features, labels, strict=True):
            writer.writerow([*row, int(label)])
    return output_path


if __name__ == "__main__":
    default_output = Path(__file__).resolve().parent / "artifacts" / "synthetic_sessions.csv"
    print(write_csv(default_output))
