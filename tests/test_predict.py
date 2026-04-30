import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# ==================== MOCK DATA ====================

FEATURE_COLS = ["HR_mean", "SpO2_mean", "RR_mean", "SBP_mean", "NEWS2"]

MOCK_DF = pd.DataFrame([
    {
        "subject_id": 12345,
        "charttime": "2100-01-01 10:00:00",
        "HR_mean": 88.5,
        "SpO2_mean": 96.2,
        "RR_mean": 18.0,
        "SBP_mean": 120.0,
        "NEWS2": 3.0
    },
    {
        "subject_id": 99999,
        "charttime": "2100-01-01 10:00:00",
        "HR_mean": 110.0,
        "SpO2_mean": 88.0,
        "RR_mean": 28.0,
        "SBP_mean": 85.0,
        "NEWS2": 9.0
    }
])

def make_mock_model(proba: float = 0.8):
    mock = MagicMock()
    mock.predict_proba.return_value = np.array([[1 - proba, proba]])
    return mock


# ==================== /patients ====================

@patch("app.api.v1.predict.df", MOCK_DF)
@patch("app.api.v1.predict.feature_columns", FEATURE_COLS)
@patch("app.api.v1.predict.model", make_mock_model(0.8))
@patch("app.api.v1.predict.explainer", None)
def test_get_patients_success():
    response = client.get("/patients")
    assert response.status_code == 200
    data = response.json()
    assert "patients" in data
    assert len(data["patients"]) == 2


@patch("app.api.v1.predict.df", MOCK_DF)
@patch("app.api.v1.predict.feature_columns", FEATURE_COLS)
@patch("app.api.v1.predict.model", make_mock_model(0.8))
@patch("app.api.v1.predict.explainer", None)
def test_get_patients_sorted_by_risk():
    response = client.get("/patients")
    patients = response.json()["patients"]
    risks = [p["current_risk"] for p in patients]
    assert risks == sorted(risks, reverse=True)


@patch("app.api.v1.predict.df", None)
@patch("app.api.v1.predict.feature_columns", FEATURE_COLS)
@patch("app.api.v1.predict.model", make_mock_model())
@patch("app.api.v1.predict.explainer", None)
def test_get_patients_server_not_ready():
    response = client.get("/patients")
    assert response.status_code == 503


# ==================== /patient/{patient_id} ====================

@patch("app.api.v1.predict.df", MOCK_DF)
@patch("app.api.v1.predict.feature_columns", FEATURE_COLS)
@patch("app.api.v1.predict.model", make_mock_model(0.85))
@patch("app.api.v1.predict.explainer", None)
def test_get_patient_success():
    response = client.get("/patient/P12345")
    assert response.status_code == 200
    data = response.json()
    assert data["patient_id"] == "P12345"
    assert "current_risk" in data
    assert "risk_level" in data
    assert "vitals" in data
    assert "shap_explanation" in data
    assert "recommendation" in data


@patch("app.api.v1.predict.df", MOCK_DF)
@patch("app.api.v1.predict.feature_columns", FEATURE_COLS)
@patch("app.api.v1.predict.model", make_mock_model(0.85))
@patch("app.api.v1.predict.explainer", None)
def test_get_patient_not_found():
    response = client.get("/patient/P00000")
    assert response.status_code == 404


@patch("app.api.v1.predict.df", None)
@patch("app.api.v1.predict.feature_columns", FEATURE_COLS)
@patch("app.api.v1.predict.model", make_mock_model())
@patch("app.api.v1.predict.explainer", None)
def test_get_patient_server_not_ready():
    response = client.get("/patient/P12345")
    assert response.status_code == 503


# ==================== Risk level & recommendation ====================

@patch("app.api.v1.predict.df", MOCK_DF)
@patch("app.api.v1.predict.feature_columns", FEATURE_COLS)
@patch("app.api.v1.predict.model", make_mock_model(0.85))
@patch("app.api.v1.predict.explainer", None)
def test_high_risk_label():
    response = client.get("/patient/P12345")
    data = response.json()
    assert data["risk_level"] == "HIGH"
    assert data["recommendation"] == "Immediate attention required"


@patch("app.api.v1.predict.df", MOCK_DF)
@patch("app.api.v1.predict.feature_columns", FEATURE_COLS)
@patch("app.api.v1.predict.model", make_mock_model(0.5))
@patch("app.api.v1.predict.explainer", None)
def test_medium_risk_label():
    response = client.get("/patient/P12345")
    data = response.json()
    assert data["risk_level"] == "MEDIUM"
    assert data["recommendation"] == "Monitor closely"


@patch("app.api.v1.predict.df", MOCK_DF)
@patch("app.api.v1.predict.feature_columns", FEATURE_COLS)
@patch("app.api.v1.predict.model", make_mock_model(0.2))
@patch("app.api.v1.predict.explainer", None)
def test_low_risk_label():
    response = client.get("/patient/P12345")
    data = response.json()
    assert data["risk_level"] == "LOW"
    assert data["recommendation"] == "Stable"