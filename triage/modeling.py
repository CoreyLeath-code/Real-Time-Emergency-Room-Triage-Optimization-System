"""Validated, reproducible training and evaluation for the triage model.

This module supports research and educational evaluation only. It is not a
clinical decision system and must not be used to direct patient care.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

FEATURE_COLUMNS = (
    "age",
    "blood_pressure",
    "heart_rate",
    "temperature",
    "symptom_score",
)
TARGET_COLUMN = "priority_level"
CLASS_LABELS = (0, 1, 2)
CLASS_NAMES = {0: "low", 1: "urgent", 2: "immediate"}
RANDOM_STATE = 42


def load_dataset(path: str | Path) -> tuple[pd.DataFrame, pd.Series]:
    """Load and validate the synthetic triage dataset contract."""
    frame = pd.read_csv(path)
    required = set(FEATURE_COLUMNS) | {TARGET_COLUMN}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"dataset is missing required columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("dataset must contain at least one row")

    features = frame.loc[:, FEATURE_COLUMNS].apply(pd.to_numeric, errors="raise")
    target = pd.to_numeric(frame[TARGET_COLUMN], errors="raise").astype(int)
    if features.isnull().any().any() or target.isnull().any():
        raise ValueError("dataset contains null values")
    unexpected = set(target.unique()) - set(CLASS_LABELS)
    if unexpected:
        raise ValueError(f"unsupported priority labels: {sorted(unexpected)}")
    if set(target.unique()) != set(CLASS_LABELS):
        raise ValueError("dataset must contain all three priority classes")
    return features, target


def split_dataset(
    features: pd.DataFrame,
    target: pd.Series,
    *,
    test_size: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Create a deterministic, stratified holdout split."""
    return train_test_split(
        features,
        target,
        test_size=test_size,
        random_state=RANDOM_STATE,
        stratify=target,
    )


def build_model() -> Pipeline:
    """Build the versioned preprocessing and classifier pipeline."""
    preprocessing = ColumnTransformer(
        [("numeric", SimpleImputer(strategy="median"), list(FEATURE_COLUMNS))],
        remainder="drop",
        verbose_feature_names_out=False,
    )
    classifier = RandomForestClassifier(
        n_estimators=200,
        random_state=RANDOM_STATE,
        class_weight="balanced_subsample",
        n_jobs=1,
    )
    return Pipeline([("preprocess", preprocessing), ("classifier", classifier)])


def train_holdout(
    path: str | Path = "database/patient_records_sample.csv",
) -> tuple[Pipeline, pd.DataFrame, pd.Series]:
    """Train on the stratified training partition and return holdout evidence."""
    features, target = load_dataset(path)
    x_train, x_test, y_train, y_test = split_dataset(features, target)
    model = build_model()
    model.fit(x_train, y_train)
    return model, x_test, y_test


def evaluate(model: Pipeline, features: pd.DataFrame, target: pd.Series) -> dict[str, Any]:
    """Return safety-relevant multiclass metrics for the held-out partition."""
    predicted = model.predict(features)
    probabilities = model.predict_proba(features)
    matrix = confusion_matrix(target, predicted, labels=CLASS_LABELS)
    per_class_recall = recall_score(
        target, predicted, labels=CLASS_LABELS, average=None, zero_division=0
    )
    return {
        "samples": int(len(target)),
        "accuracy": float(accuracy_score(target, predicted)),
        "balanced_accuracy": float(balanced_accuracy_score(target, predicted)),
        "precision_macro": float(precision_score(target, predicted, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(target, predicted, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(target, predicted, average="macro", zero_division=0)),
        "f1_weighted": float(f1_score(target, predicted, average="weighted", zero_division=0)),
        "roc_auc_ovr_weighted": float(
            roc_auc_score(target, probabilities, labels=CLASS_LABELS, multi_class="ovr", average="weighted")
        ),
        "per_class_recall": {
            CLASS_NAMES[label]: float(value)
            for label, value in zip(CLASS_LABELS, per_class_recall)
        },
        "confusion_matrix": matrix.tolist(),
    }
