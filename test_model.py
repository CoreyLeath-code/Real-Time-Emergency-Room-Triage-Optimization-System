"""Regression tests for the validated MediTriage modeling pipeline."""
from __future__ import annotations

import joblib
import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

from triage.modeling import (
    CLASS_LABELS,
    FEATURE_COLUMNS,
    evaluate,
    load_dataset,
    split_dataset,
)

DATA_PATH = "database/patient_records_sample.csv"
MODEL_PATH = "ml_model/triage_model.pkl"


@pytest.fixture(scope="module")
def dataset():
    return load_dataset(DATA_PATH)


@pytest.fixture(scope="module")
def holdout(dataset):
    features, target = dataset
    return split_dataset(features, target)


@pytest.fixture(scope="module")
def model():
    loaded = joblib.load(MODEL_PATH)
    assert isinstance(loaded, Pipeline)
    return loaded


def test_dataset_contract(dataset):
    features, target = dataset
    assert tuple(features.columns) == FEATURE_COLUMNS
    assert set(target.unique()) == set(CLASS_LABELS)
    assert not features.isnull().any().any()


def test_split_is_deterministic_and_stratified(dataset, holdout):
    features, target = dataset
    _, first_test, _, first_target = holdout
    _, second_test, _, second_target = split_dataset(features, target)
    pd.testing.assert_frame_equal(first_test, second_test)
    pd.testing.assert_series_equal(first_target, second_target)
    assert set(first_target.unique()) == set(CLASS_LABELS)


def test_model_produces_valid_probabilities(model, holdout):
    _, x_test, _, _ = holdout
    probabilities = model.predict_proba(x_test.iloc[:8])
    assert probabilities.shape == (8, 3)
    assert (probabilities >= 0).all()
    assert (probabilities <= 1).all()
    assert probabilities.sum(axis=1) == pytest.approx([1.0] * 8)


def test_heldout_metrics_are_complete(model, holdout):
    _, x_test, _, y_test = holdout
    metrics = evaluate(model, x_test, y_test)
    assert metrics["samples"] == len(y_test)
    assert 0.0 <= metrics["balanced_accuracy"] <= 1.0
    assert 0.0 <= metrics["f1_macro"] <= 1.0
    assert set(metrics["per_class_recall"]) == {"low", "urgent", "immediate"}
    assert len(metrics["confusion_matrix"]) == 3


def test_missing_columns_are_rejected(tmp_path):
    invalid = tmp_path / "invalid.csv"
    pd.DataFrame({"age": [30], "priority_level": [1]}).to_csv(invalid, index=False)
    with pytest.raises(ValueError, match="missing required columns"):
        load_dataset(invalid)
