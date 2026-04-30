from pydantic import BaseModel, Field
from typing import Optional


class PatientFeaturesRequest(BaseModel):
    subject_id: int = Field(..., description="Patient subject ID")

    # Vitals
    HR_mean: Optional[float] = Field(0.0, description="Mean Heart Rate")
    SpO2_mean: Optional[float] = Field(0.0, description="Mean SpO2")
    RR_mean: Optional[float] = Field(0.0, description="Mean Respiratory Rate")
    SBP_mean: Optional[float] = Field(0.0, description="Mean Systolic Blood Pressure")
    NEWS2: Optional[float] = Field(0.0, description="NEWS2 Score")

    class Config:
        json_schema_extra = {
            "example": {
                "subject_id": 12345,
                "HR_mean": 88.5,
                "SpO2_mean": 96.2,
                "RR_mean": 18.0,
                "SBP_mean": 120.0,
                "NEWS2": 3.0
            }
        }