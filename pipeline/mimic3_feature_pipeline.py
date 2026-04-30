import pandas as pd
import numpy as np

print("="*60)
print("MIMIC-III FEATURE PIPELINE (FINAL - NO LEAKAGE)")
print("="*60)

base = "data/mimic-iii/"

# ---------------- LOAD ----------------
chartevents = pd.read_csv(base + "CHARTEVENTS.csv", low_memory=False)
chartevents = chartevents[chartevents["valuenum"].notna()]

# ---------------- FILTER VITALS ----------------
vital_itemids = {
    "HR": [211, 220045],
    "SpO2": [646, 220277],
    "RR": [618, 220210],
    "SBP": [51, 442, 455, 220179, 220050]
}

all_ids = sum(vital_itemids.values(), [])
chartevents = chartevents[chartevents["itemid"].isin(all_ids)]

def map_vital(i):
    if i in vital_itemids["HR"]: return "HR"
    if i in vital_itemids["SpO2"]: return "SpO2"
    if i in vital_itemids["RR"]: return "RR"
    if i in vital_itemids["SBP"]: return "SBP"

chartevents["vital"] = chartevents["itemid"].apply(map_vital)
chartevents["charttime"] = pd.to_datetime(chartevents["charttime"])

# ---------------- PIVOT ----------------
vitals = chartevents.pivot_table(
    index=["subject_id","hadm_id","charttime"],
    columns="vital",
    values="valuenum",
    aggfunc="mean"
).reset_index()

vitals = vitals.sort_values(["subject_id","charttime"])

print("Vitals shape:", vitals.shape)

# ---------------- FUTURE TARGET (NO LEAKAGE) ----------------
vitals["target"] = (
    (vitals.groupby("subject_id")["SpO2"].shift(-3) < 90) |
    (vitals.groupby("subject_id")["SBP"].shift(-3) < 90) |
    (vitals.groupby("subject_id")["RR"].shift(-3) > 30)
).astype(int)

# ---------------- FEATURE ENGINEERING ----------------
rows = []

def calculate_news2(hr, spo2, rr, sbp):
    score = 0
    if hr > 130: score += 3
    if spo2 < 92: score += 3
    if rr > 25: score += 3
    if sbp < 90: score += 3
    return score

for subject_id, group in vitals.groupby("subject_id"):

    group = group.dropna()
    group = group.sort_values("charttime")

    for i in range(6, len(group)-3):  # IMPORTANT: avoid future leakage

        current_time = group.iloc[i]["charttime"]

        window_3 = group.iloc[i-3:i+1]
        window_6 = group.iloc[i-6:i+1]

        row = {
            "subject_id": subject_id,
            "hadm_id": group.iloc[i]["hadm_id"],
            "charttime": current_time,

            "time_from_admission": (
                current_time - group.iloc[0]["charttime"]
            ).total_seconds() / 3600,

            # HR
            "HR_mean": window_6["HR"].mean(),
            "HR_std": window_6["HR"].std(),
            "HR_range": window_6["HR"].max() - window_6["HR"].min(),
            "HR_trend": window_3["HR"].iloc[-1] - window_3["HR"].iloc[0],

            # SpO2
            "SpO2_mean": window_6["SpO2"].mean(),
            "SpO2_min": window_6["SpO2"].min(),
            "SpO2_drop": window_6["SpO2"].max() - window_6["SpO2"].min(),
            "SpO2_trend": window_3["SpO2"].iloc[-1] - window_3["SpO2"].iloc[0],

            # RR
            "RR_mean": window_6["RR"].mean(),
            "RR_std": window_6["RR"].std(),
            "RR_trend": window_3["RR"].iloc[-1] - window_3["RR"].iloc[0],

            # SBP
            "SBP_mean": window_6["SBP"].mean(),
            "SBP_min": window_6["SBP"].min(),
            "SBP_drop": window_6["SBP"].max() - window_6["SBP"].min(),
            "SBP_trend": window_3["SBP"].iloc[-1] - window_3["SBP"].iloc[0],

            # derived
            "shock_index": window_6["HR"].mean() / (window_6["SBP"].mean()+1e-6),
            "resp_stress": window_6["RR"].mean() / (window_6["SpO2"].mean()+1e-6),

            # NEWS2
            "NEWS2": calculate_news2(
                window_6["HR"].mean(),
                window_6["SpO2"].mean(),
                window_6["RR"].mean(),
                window_6["SBP"].mean()
            ),

            "target": group.iloc[i]["target"]
        }

        rows.append(row)

df = pd.DataFrame(rows).dropna()

print("Final dataset:", df.shape)

df.to_csv("data/processed/features.csv", index=False)

print("="*60)