"""SQLite persistence for session activity and learner feedback."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .mentor_session import MentorSession


class ProgressRepository:
    def __init__(self, database_path: Path | None = None) -> None:
        self._database_path = database_path or Path(__file__).resolve().parents[1] / "data" / "mentorx.db"
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def save_session(self, session: MentorSession) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO sessions (
                    session_id, learner_name, problem_id, difficulty, started_at,
                    current_hint_level, minutes_stuck, repeated_attempts,
                    hint_requests, breakthroughs
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.session_id,
                    session.learner_name,
                    session.problem_id,
                    session.difficulty,
                    session.started_at.isoformat(),
                    session.current_hint_level,
                    session.minutes_stuck,
                    session.repeated_attempts,
                    session.hint_requests,
                    session.breakthroughs,
                ),
            )

    def save_event(self, session_id: str, event_type: str, value: float | int = 1) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO events (session_id, event_type, value) VALUES (?, ?, ?)",
                (session_id, event_type, value),
            )

    def save_feedback(self, session_id: str, helpful: bool, note: str = "") -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO feedback (session_id, helpful, note) VALUES (?, ?, ?)",
                (session_id, int(helpful), note.strip()),
            )

    def save_explanation(self, session_id: str, explanation: str, score: int, level: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO explanations (session_id, explanation, score, level) VALUES (?, ?, ?, ?)",
                (session_id, explanation.strip(), score, level),
            )

    def session_summary(self, session_id: str) -> dict | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
            if row is None:
                return None
            return dict(row)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    learner_name TEXT NOT NULL,
                    problem_id TEXT NOT NULL,
                    difficulty INTEGER NOT NULL,
                    started_at TEXT NOT NULL,
                    current_hint_level INTEGER NOT NULL,
                    minutes_stuck REAL NOT NULL,
                    repeated_attempts INTEGER NOT NULL,
                    hint_requests INTEGER NOT NULL,
                    breakthroughs INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS feedback (
                    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    helpful INTEGER NOT NULL CHECK (helpful IN (0, 1)),
                    note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS explanations (
                    explanation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    explanation TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    level TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
