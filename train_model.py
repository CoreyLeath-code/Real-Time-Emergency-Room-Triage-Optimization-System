"""Train the deterministic MediTriage pipeline and persist held-out metrics."""
from __future__ import annotations

import json
from pathlib import Path

import joblib

from triage.modeling import evaluate, train_holdout

DATA_PATH = Path("database/patient_records_sample.csv")
MODEL_PATH = Path("ml_model/triage_model.pkl")
METRICS_PATH = Path("metrics/latest_model_metrics.json")


def main() -> int:
    model, x_test, y_test = train_holdout(DATA_PATH)
    metrics = evaluate(model, x_test, y_test)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(metrics, indent=2))
    print(f"Model saved to {MODEL_PATH}")
    print(f"Held-out metrics saved to {METRICS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
