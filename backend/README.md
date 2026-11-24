# MentorX backend foundation

This folder contains a runnable end-to-end MentorX demo backend.

Run the API from the `backend` directory:

```powershell
python -m uvicorn app:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Open the frontend while
the API is running; it automatically connects to the backend. If the API is
not running, the frontend remains usable in rule-based demo mode.

Run its tests from the `backend` directory:

```powershell
python -m unittest discover -s tests -v
```

## API routes

- `GET /health` - backend and selected-model status.
- `GET /problems` - available DSA problems.
- `GET /practice-questions` - 18 example DSA questions and expected concepts.
- `GET /problems/{id}/hint-analysis` - quality preflight for written hints.
- `POST /start-session` - create a learner session.
- `POST /sessions/{id}/events` - log retry, breakthrough, or time update.
- `POST /sessions/{id}/next-hint` - release exactly one next hint level.
- `POST /sessions/{id}/feedback` - save whether a hint was useful.
- `POST /sessions/{id}/explanation` - check a written explanation against a transparent concept rubric.
- `GET /ml/metrics` - training comparison and selected model.

## Train the demo models

```powershell
python ml/train_models.py
```

The training script creates 3,000 reproducible synthetic sessions, compares
Logistic Regression, Decision Tree, and Random Forest, then saves the best
validation-F1 model. Synthetic scores are for technical demonstration only;
real student feedback is required to validate actual learning benefit.

## Editing hints

Edit `data/hints.json`. Each problem must have a unique `id` and exactly five
hint objects. Keep `level` values in order from `1` to `5`:

1. `Reflect` - a question that makes the learner think.
2. `Connect` - link the problem to a useful idea without naming the full method.
3. `Sketch` - give the high-level approach.
4. `Pseudocode` - describe the algorithm steps without full code.
5. `Explain` - explain complexity, edge cases, or why the approach works.

Example hint object:

```json
{
  "level": 2,
  "stage": "Connect",
  "text": "Write your hint here."
}
```

JSON rules: use double quotes around all keys and text, separate items with
commas, and do not leave a comma after the final item in a list.

## Explanation check

The explanation checker uses `data/practice_questions.json`. It scores written
concept coverage, clarity, complexity discussion, and reasoning words. It is a
learning prompt and not a substitute for reviewing the student's code or oral
explanation. The learner's response and score are saved in SQLite for progress
tracking.
