"""Evaluate the saved model on the deterministic stratified holdout."""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from triage.modeling import CLASS_NAMES, evaluate, load_dataset, split_dataset

DATA_PATH = Path("database/patient_records_sample.csv")
MODEL_PATH = Path("ml_model/triage_model.pkl")
METRICS_PATH = Path("metrics/latest_model_metrics.json")
MATRIX_PATH = Path("metrics/confusion_matrix.png")


def main() -> int:
    features, target = load_dataset(DATA_PATH)
    _, x_test, _, y_test = split_dataset(features, target)
    model = joblib.load(MODEL_PATH)
    metrics = evaluate(model, x_test, y_test)

    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    labels = [CLASS_NAMES[index] for index in sorted(CLASS_NAMES)]
    plt.figure(figsize=(6, 5))
    sns.heatmap(
        metrics["confusion_matrix"],
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels,
    )
    plt.title("Held-out confusion matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.savefig(MATRIX_PATH)
    plt.close()

    print(json.dumps(metrics, indent=2))
    print(f"Confusion matrix saved to {MATRIX_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
