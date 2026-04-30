from pydantic_settings import BaseSettings
from pydantic import ConfigDict  # add this
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8") 

    APP_NAME: str = "PANACEA"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    ARTIFACTS_DIR: Path = BASE_DIR / "artifacts"
    DATA_DIR: Path = BASE_DIR / "data"

    MODEL_PATH: Path = ARTIFACTS_DIR / "xgb_model.json"
    SCALER_PATH: Path = ARTIFACTS_DIR / "scaler.pkl"
    SHAP_EXPLAINER_PATH: Path = ARTIFACTS_DIR / "shap_explainer.pkl"
    FEATURE_COLUMNS_PATH: Path = ARTIFACTS_DIR / "feature_columns.pkl"
    METRICS_PATH: Path = ARTIFACTS_DIR / "metrics.pkl"

settings = Settings()