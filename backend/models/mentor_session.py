"""State for one learner's MentorX problem-solving session."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


@dataclass
class MentorSession:
    learner_name: str
    problem_id: str
    difficulty: int = 2
    session_id: str = field(default_factory=lambda: str(uuid4()))
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    current_hint_level: int = 0
    minutes_stuck: float = 0
    repeated_attempts: int = 0
    hint_requests: int = 0
    breakthroughs: int = 0

    def log_retry(self) -> None:
        self.repeated_attempts += 1

    def log_breakthrough(self) -> None:
        self.breakthroughs += 1

    def log_hint_request(self) -> None:
        self.hint_requests += 1

    def set_minutes_stuck(self, minutes: float) -> None:
        if minutes < 0:
            raise ValueError("minutes_stuck cannot be negative")
        self.minutes_stuck = minutes

    def features(self) -> dict[str, float | int]:
        """Return the ML feature vector in one stable, documented shape."""
        return {
            "minutes_stuck": self.minutes_stuck,
            "repeated_attempts": self.repeated_attempts,
            "hint_requests": self.hint_requests,
            "breakthroughs": self.breakthroughs,
            "current_hint_level": self.current_hint_level,
            "difficulty": self.difficulty,
        }
