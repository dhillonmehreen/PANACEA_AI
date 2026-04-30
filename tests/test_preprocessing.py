import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch

from app.api.v1.predict import get_risk_level, get_recommendation, build_features


FEATURE_COLS = ["HR_mean", "SpO2_mean", "RR_mean", "SBP_mean", "NEWS2"]

MOCK_ROW = pd.Series({
    "subject_id": 12345,
    "charttime": "2100-01-01 10:00:00",
    "HR_mean": 88.5,
    "SpO2_mean": 96.2,
    "RR_mean": 18.0,
    "SBP_mean": 120.0,
    "NEWS2": 3.0
})


# ==================== get_risk_level ====================

def test_risk_high():
    assert get_risk_level(0.75) == "HIGH"
    assert get_risk_level(1.0) == "HIGH"


def test_risk_medium():
    assert get_risk_level(0.5) == "MEDIUM"
    assert get_risk_level(0.41) == "MEDIUM"


def test_risk_low():
    assert get_risk_level(0.3) == "LOW"
    assert get_risk_level(0.0) == "LOW"


def test_risk_boundaries():
    assert get_risk_level(0.7) == "MEDIUM"  # not > 0.7
    assert get_risk_level(0.4) == "LOW"     # not > 0.4


# ==================== get_recommendation ====================

def test_recommendation_high():
    assert get_recommendation(0.8) == "Immediate attention required"


def test_recommendation_medium():
    assert get_recommendation(0.5) == "Monitor closely"


def test_recommendation_low():
    assert get_recommendation(0.2) == "Stable"


# ==================== build_features ====================

@patch("app.api.v1.predict.feature_columns", FEATURE_COLS)
def test_build_features_shape():
    X = build_features(MOCK_ROW)
    assert isinstance(X, pd.DataFrame)
    assert X.shape == (1, len(FEATURE_COLS))


@patch("app.api.v1.predict.feature_columns", FEATURE_COLS)
def test_build_features_columns():
    X = build_features(MOCK_ROW)
    assert list(X.columns) == FEATURE_COLS


@patch("app.api.v1.predict.feature_columns", FEATURE_COLS)
def test_build_features_missing_col():
    # Row missing a feature — should default to 0.0
    row = MOCK_ROW.drop("NEWS2")
    X = build_features(row)
    assert X["NEWS2"].iloc[0] == 0.0


@patch("app.api.v1.predict.feature_columns", FEATURE_COLS)
def test_build_features_no_nan():
    X = build_features(MOCK_ROW)
    assert not X.isnull().values.any()