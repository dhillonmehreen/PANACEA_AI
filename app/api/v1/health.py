from fastapi import APIRouter
from app.core.model import model, feature_columns, df
from app.schemas.response import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "features_loaded": feature_columns is not None,
        "data_loaded": df is not None
    }