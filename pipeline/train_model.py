import pandas as pd
import numpy as np
import xgboost as xgb
import pickle
import shap

from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import roc_auc_score, confusion_matrix

print("="*60)
print("MODEL TRAINING + SHAP")
print("="*60)

df = pd.read_csv("data/processed/features.csv")

X = df.drop(columns=["target","subject_id","hadm_id","charttime"])
y = df["target"]
groups = df["subject_id"]

gss = GroupShuffleSplit(test_size=0.2, random_state=42)
train_idx, test_idx = next(gss.split(X,y,groups))

X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

# MODEL
model = xgb.XGBClassifier(
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="auc",
    random_state=42
)

model.fit(X_train, y_train)

y_pred = model.predict_proba(X_test)[:,1]

auc = roc_auc_score(y_test, y_pred)
print("AUROC:", auc)

# CONFUSION MATRIX
from sklearn.metrics import precision_recall_curve

precision, recall, thresholds = precision_recall_curve(y_test, y_pred)
f1 = 2*(precision*recall)/(precision+recall+1e-8)
best = np.argmax(f1)
threshold = thresholds[best]

y_bin = (y_pred > threshold).astype(int)
cm = confusion_matrix(y_test, y_bin)

print("\nConfusion Matrix:")
print(cm)
print("\nThreshold:", threshold)

# ---------------- SHAP ----------------
print("\nGenerating SHAP...")

explainer = shap.Explainer(model, X_train)

# save explainer
with open("models/shap_explainer.pkl", "wb") as f:
    pickle.dump(explainer, f)

# SAVE MODEL + FEATURES
model.save_model("models/xgb_model.json")

with open("models/feature_columns.pkl","wb") as f:
    pickle.dump(list(X.columns), f)

print("\nModel + SHAP saved.")
print("="*60)