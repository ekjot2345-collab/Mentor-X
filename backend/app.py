"""FastAPI application for the MentorX demo backend."""

from __future__ import annotations

from dataclasses import asdict
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:  # Supports both `python app.py` and `uvicorn backend.app:app`.
    from .models.hint_engine import HintEngine
    from .models.explanation_evaluator import ExplanationEvaluator
    from .models.mentor_session import MentorSession
    from .models.model_service import NudgePredictionService
    from .models.progress_repository import ProgressRepository
    from .models.question_bank import QuestionBank
    from .models.struggle_detector import MentoringMode, StruggleDetector
except ImportError:  # pragma: no cover - only used when run from backend/.
    from models.hint_engine import HintEngine
    from models.explanation_evaluator import ExplanationEvaluator
    from models.mentor_session import MentorSession
    from models.model_service import NudgePredictionService
    from models.progress_repository import ProgressRepository
    from models.question_bank import QuestionBank
    from models.struggle_detector import MentoringMode, StruggleDetector


class StartSessionRequest(BaseModel):
    learner_name: str = Field(default="Demo learner", min_length=1, max_length=80)
    problem_id: str = "two-sum"
    difficulty: int = Field(default=2, ge=1, le=3)


class EventRequest(BaseModel):
    event_type: Literal["retry", "breakthrough", "time_update"]
    minutes_stuck: float | None = Field(default=None, ge=0)


class FeedbackRequest(BaseModel):
    helpful: bool
    note: str = Field(default="", max_length=500)


class ExplanationRequest(BaseModel):
    explanation: str = Field(min_length=10, max_length=4_000)


app = FastAPI(title="MentorX API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Local demonstration only; restrict this list before a real deployment.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = StruggleDetector()
hints = HintEngine()
repository = ProgressRepository()
predictor = NudgePredictionService()
question_bank = QuestionBank()
explanation_evaluator = ExplanationEvaluator(question_bank)
sessions: dict[str, MentorSession] = {}


def _status_for(session: MentorSession) -> dict:
    rule_assessment = detector.assess(
        minutes_stuck=session.minutes_stuck,
        repeated_attempts=session.repeated_attempts,
        hint_requests=session.hint_requests,
        breakthroughs=session.breakthroughs,
    )
    prediction = predictor.predict(session, rule_assessment)
    return {
        "session": {
            "session_id": session.session_id,
            "learner_name": session.learner_name,
            "problem_id": session.problem_id,
            "difficulty": session.difficulty,
            "current_hint_level": session.current_hint_level,
            **session.features(),
        },
        "rule_assessment": {
            "score": rule_assessment.score,
            "mode": rule_assessment.mode.value,
            "recommended_action": rule_assessment.recommended_action,
            "reasons": rule_assessment.reasons,
        },
        "prediction": {**asdict(prediction), "mode": prediction.mode.value},
    }


def _get_session(session_id: str) -> MentorSession:
    session = sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found. Start a new session first.")
    return session


@app.get("/health")
def health() -> dict:
    metrics = predictor.metrics()
    return {"status": "ok", "model_available": metrics["available"], "model": metrics.get("selected_model")}


@app.get("/problems")
def list_problems() -> list[dict]:
    return hints.list_problems()


@app.get("/practice-questions")
def practice_questions() -> list[dict]:
    return question_bank.list_questions()


@app.get("/problems/{problem_id}/hint-analysis")
def hint_analysis(problem_id: str) -> dict:
    try:
        return hints.analyze_problem_hints(problem_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.post("/start-session")
def start_session(request: StartSessionRequest) -> dict:
    try:
        hints.get_problem(request.problem_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    session = MentorSession(
        learner_name=request.learner_name.strip(),
        problem_id=request.problem_id,
        difficulty=request.difficulty,
    )
    sessions[session.session_id] = session
    repository.save_session(session)
    return _status_for(session)


@app.get("/sessions/{session_id}")
def get_session(session_id: str) -> dict:
    return _status_for(_get_session(session_id))


@app.post("/sessions/{session_id}/events")
def log_event(session_id: str, request: EventRequest) -> dict:
    session = _get_session(session_id)
    if request.event_type == "retry":
        session.log_retry()
        repository.save_event(session_id, "retry")
    elif request.event_type == "breakthrough":
        session.log_breakthrough()
        repository.save_event(session_id, "breakthrough")
    else:
        if request.minutes_stuck is None:
            raise HTTPException(status_code=422, detail="minutes_stuck is required for time_update")
        session.set_minutes_stuck(request.minutes_stuck)
        repository.save_event(session_id, "time_update", request.minutes_stuck)

    repository.save_session(session)
    return _status_for(session)


@app.post("/sessions/{session_id}/next-hint")
def next_hint(session_id: str) -> dict:
    session = _get_session(session_id)
    session.log_hint_request()
    status = _status_for(session)
    hint = hints.get_next_hint(
        problem_id=session.problem_id,
        current_level=session.current_hint_level,
        mode=MentoringMode(status["prediction"]["mode"]),
    )
    if hint is None:
        raise HTTPException(status_code=409, detail="All five hints have already been used.")

    session.current_hint_level = hint.level
    repository.save_event(session_id, "hint_requested", hint.level)
    repository.save_session(session)
    return {**_status_for(session), "hint": asdict(hint)}


@app.post("/sessions/{session_id}/feedback")
def save_feedback(session_id: str, request: FeedbackRequest) -> dict:
    _get_session(session_id)
    repository.save_feedback(session_id, request.helpful, request.note)
    return {"saved": True, "message": "Thanks. This feedback can validate future ML models."}


@app.post("/sessions/{session_id}/explanation")
def evaluate_explanation(session_id: str, request: ExplanationRequest) -> dict:
    session = _get_session(session_id)
    evaluation = explanation_evaluator.evaluate(session.problem_id, request.explanation)
    repository.save_explanation(session_id, request.explanation, evaluation.score, evaluation.level)
    return evaluation.to_dict()


@app.get("/ml/metrics")
def model_metrics() -> dict:
    return predictor.metrics()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
