from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class RiskLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class KeyVitals(BaseModel):
    hr: float = Field(..., description="Heart Rate")
    spo2: float = Field(..., description="SpO2")
    rr: float = Field(..., description="Respiratory Rate")
    sbp: float = Field(..., description="Systolic Blood Pressure")


class FullVitals(BaseModel):
    heart_rate: float
    spo2: float
    respiratory_rate: float
    blood_pressure: float


class SHAPExplanation(BaseModel):
    feature: str
    impact: float
    direction: str = Field(..., description="'increase' or 'decrease'")


class PatientSummaryResponse(BaseModel):
    patient_id: str
    current_risk: float = Field(..., ge=0.0, le=1.0)
    risk_level: RiskLevel
    key_vitals: KeyVitals
    news2_score: float


class PatientDetailResponse(BaseModel):
    patient_id: str
    current_risk: float = Field(..., ge=0.0, le=1.0)
    risk_level: RiskLevel
    vitals: FullVitals
    news2_score: float
    shap_explanation: List[SHAPExplanation] = []
    recommendation: str


class PatientsListResponse(BaseModel):
    patients: List[PatientSummaryResponse]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    features_loaded: bool
    data_loaded: bool