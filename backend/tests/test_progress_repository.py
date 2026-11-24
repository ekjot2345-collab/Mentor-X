import tempfile
import unittest
from pathlib import Path

from models.mentor_session import MentorSession
from models.progress_repository import ProgressRepository


class ProgressRepositoryTests(unittest.TestCase):
    def test_session_is_persisted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = ProgressRepository(Path(temporary_directory) / "test.db")
            session = MentorSession(learner_name="Test learner", problem_id="two-sum")
            session.log_retry()
            repository.save_session(session)
            repository.save_event(session.session_id, "retry")
            repository.save_feedback(session.session_id, helpful=True, note="Useful hint")

            stored = repository.session_summary(session.session_id)

        self.assertEqual(stored["learner_name"], "Test learner")
        self.assertEqual(stored["repeated_attempts"], 1)
