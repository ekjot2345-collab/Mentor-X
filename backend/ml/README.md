# MentorX ML demo

Run from the `backend` folder:

```powershell
python ml/train_models.py
```

This creates three artifacts in `ml/artifacts/`:

- `synthetic_sessions.csv` - 3,000 reproducible, simulated sessions.
- `best_model.joblib` - the best of Logistic Regression, Decision Tree, and Random Forest.
- `model_report.json` - held-out validation metrics and the selection decision.

The selected model is chosen by validation F1 score, then accuracy. Synthetic
metrics are suitable for a technical demonstration only; use real, consented
learner feedback before making performance claims about students.
