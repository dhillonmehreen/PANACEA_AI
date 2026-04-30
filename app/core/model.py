import pickle
import xgboost as xgb
import pandas as pd
from app.config import settings

model = None
feature_columns = None
explainer = None
df = None

try:
    model = xgb.XGBClassifier()
    model.load_model(str(settings.MODEL_PATH))
except Exception as e:
    print(f"❌ Model load failed: {e}")

try:
    with open(settings.FEATURE_COLUMNS_PATH, "rb") as f:
        feature_columns = pickle.load(f)
except Exception as e:
    print(f"❌ Features load failed: {e}")

try:
    with open(settings.SHAP_EXPLAINER_PATH, "rb") as f:
        explainer = pickle.load(f)
except Exception as e:
    print(f"⚠️ SHAP load failed: {e}")

try:
    df = pd.read_csv(settings.DATA_DIR / "processed" / "features.csv")
except Exception as e:
    print(f"❌ Data load failed: {e}")