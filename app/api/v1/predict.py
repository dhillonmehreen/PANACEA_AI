from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
import traceback
from app.schemas.response import PatientsListResponse, PatientDetailResponse

from app.core.model import model, feature_columns, df, explainer

router = APIRouter()


def get_risk_level(risk: float) -> str:
    if risk > 0.7:
        return "HIGH"
    elif risk > 0.4:
        return "MEDIUM"
    return "LOW"


def get_recommendation(risk: float) -> str:
    if risk > 0.7:
        return "Immediate attention required"
    elif risk > 0.4:
        return "Monitor closely"
    return "Stable"


def build_features(row) -> pd.DataFrame:
    features = {
        col: float(row[col]) if col in row.index and pd.notna(row[col]) else 0.0
        for col in feature_columns
    }
    return pd.DataFrame([features])[feature_columns].fillna(0)


def check_ready():
    if model is None or feature_columns is None or df is None:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Server not ready",
                "model": model is not None,
                "features": feature_columns is not None,
                "data": df is not None
            }
        )


@router.get("/patients", response_model=PatientsListResponse)
def get_patients():
    check_ready()
    try:
        latest = df.sort_values("charttime").groupby("subject_id").tail(1)
        results = []

        for _, row in latest.iterrows():
            X_input = build_features(row)
            risk = float(model.predict_proba(X_input)[0][1])

            results.append({
                "patient_id": f"P{int(row['subject_id'])}",
                "current_risk": round(risk, 3),
                "risk_level": get_risk_level(risk),
                "key_vitals": {
                    "hr": float(row.get("HR_mean", 0)),
                    "spo2": float(row.get("SpO2_mean", 0)),
                    "rr": float(row.get("RR_mean", 0)),
                    "sbp": float(row.get("SBP_mean", 0))
                },
                "news2_score": float(row.get("NEWS2", 0))
            })

        results.sort(key=lambda x: x["current_risk"], reverse=True)
        return {"patients": results}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "traceback": traceback.format_exc()}
        )


@router.get("/patient/{patient_id}", response_model=PatientDetailResponse)
def get_patient(patient_id: str):
    check_ready()
    try:
        subject_id = int(str(patient_id).replace("P", ""))
        patient_rows = df[df["subject_id"] == subject_id]

        if patient_rows.empty:
            raise HTTPException(status_code=404, detail="Patient not found")

        row = patient_rows.sort_values("charttime").iloc[-1]
        X_input = build_features(row)
        risk = float(model.predict_proba(X_input)[0][1])

        explanation = []
        if explainer:
            try:
                shap_values = explainer(X_input)
                vals = shap_values.values[0]
                names = X_input.columns
                top_idx = np.argsort(np.abs(vals))[-5:]

                for i in top_idx[::-1]:
                    explanation.append({
                        "feature": names[i],
                        "impact": round(float(vals[i]), 4),
                        "direction": "increase" if vals[i] > 0 else "decrease"
                    })
            except Exception:
                pass

        return {
            "patient_id": f"P{subject_id}",
            "current_risk": round(risk, 3),
            "risk_level": get_risk_level(risk),
            "vitals": {
                "heart_rate": float(row.get("HR_mean", 0)),
                "spo2": float(row.get("SpO2_mean", 0)),
                "respiratory_rate": float(row.get("RR_mean", 0)),
                "blood_pressure": float(row.get("SBP_mean", 0))
            },
            "news2_score": float(row.get("NEWS2", 0)),
            "shap_explanation": explanation,
            "recommendation": get_recommendation(risk)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "traceback": traceback.format_exc()}
        )