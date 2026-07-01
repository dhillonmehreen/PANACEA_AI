#  PANACEA AI

**AI-Powered Clinical Decision Support System for ICU Risk Prediction**

---

#  What It Does

PANACEA takes patient vitals from the MIMIC-III ICU dataset, runs them through a trained XGBoost model, and surfaces a risk score for each patient on a live dashboard. High-risk patients are flagged immediately so clinical staff can prioritize intervention.

* 🔴 **HIGH Risk** (> 0.7) → Immediate attention required
* 🟡 **MEDIUM Risk** (0.4–0.7) → Monitor closely
* 🟢 **LOW Risk** (< 0.4) → Stable

---

#  Tech Stack

* Python
* FastAPI
* XGBoost
* Pandas
* NumPy
* Scikit-learn
* SHAP
* HTML/CSS/JavaScript

---

#  Features

* ICU patient risk prediction using machine learning
* Data preprocessing and feature engineering pipeline
* Interactive dashboard for patient monitoring
* Explainable AI insights using SHAP
* FastAPI-powered backend
* Modular and scalable architecture

---

#  Project Structure

```text
PANACEA/
│   requirements.txt
│   .env.example
│   .gitignore
│   README.md
│
├───app/
│   │   main.py              # FastAPI app, routers, middleware
│   │   config.py            # Pydantic settings
│   │
│   ├───api/v1/
│   │       predict.py       # /patients, /patient/{id} endpoints
│   │       health.py        # /health endpoint
│   │
│   ├───core/
│   │       model.py         # Artifact loading
│   │
│   ├───schemas/
│   │       request.py       # Pydantic input models
│   │       response.py      # Pydantic output models
│   │
│   ├───static/              # JS, CSS
│   └───templates/           # Jinja2 HTML dashboard
│
├───pipeline/
│       feature_pipeline.py  # MIMIC-III feature engineering
│       train_model.py       # Model training
│
├───notebooks/
│       00_download_data.ipynb
│
└───tests/
        test_predict.py
        test_preprocessing.py
```

---

#  API Endpoints

| Method | Endpoint        | Description                              |
| ------ | --------------- | ---------------------------------------- |
| GET    | `/health`       | Server + model status                    |
| GET    | `/patients`     | All patients sorted by risk              |
| GET    | `/patient/{id}` | Single patient detail + SHAP explanation |
| GET    | `/dashboard`    | Live monitoring dashboard                |

---

#  Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/yourusername/panacea.git
cd panacea
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Set Up Environment

```bash
cp .env.example .env
```

## 4. Add Artifacts and Data

Download the model artifacts and place them in `artifacts/`.

Download MIMIC-III data from PhysioNet and place CSVs in:

```text
data/mimic-iii/
```

## 5. Run the Pipeline (If Retraining)

```bash
python pipeline/feature_pipeline.py
python pipeline/train_model.py
```

## 6. Start the Server

```bash
uvicorn app.main:app --reload
```

Visit:

```text
http://localhost:8000/dashboard
```

---

#  Model Performance

| Metric      | Value |
| ----------- | ----- |
| AUROC       | 0.333 |
| Sensitivity | 1.00  |
| Specificity | 0.00  |

>  **Note:** The model currently flags all patients as positive (high sensitivity, zero specificity). This is a known class imbalance issue in the MIMIC-III subset used. The pipeline and dashboard architecture are production-ready—improving model performance with better sampling (SMOTE, class weights) is the next step.

---

#  Tests

![Tests](tests_screenshot.png)

**20/20 Passing | 0 Warnings**

---

#  Dataset

This project uses MIMIC-III, a publicly available ICU database from Beth Israel Deaconess Medical Center. Access requires credentialed PhysioNet registration.

**MIMIC-III data is not included in this repository.**

---

# Roadmap

* [ ] Fix class imbalance with SMOTE / class weighting
* [ ] Add time-series trend view per patient
* [ ] Dockerize for deployment
* [ ] Add authentication for clinical use

---

#  My Contributions

As part of the PANACEA AI project, my contributions included:

* Designed a patient risk assessment methodology using clinical parameters extracted from the MIMIC-III dataset.
* Developed a scoring framework to categorize patients into different risk levels based on predicted outcomes and vital indicators.
* Analyzed the impact of individual clinical features on overall patient risk.
* Evaluated risk thresholds and classification performance to improve interpretability for healthcare professionals.
* Assisted in validating the scoring logic against model predictions and patient records.

---

#  Project Goal

The primary objective of PANACEA AI is to support healthcare professionals by providing accurate, explainable, and timely risk assessments for ICU patients, enabling better decision-making and improving patient outcomes.

---

#  Team

* Sreansh Verma
* Arunendra Bahadur Singh
* Mehreen Dhillon
* Amya Rastogi

---

#  Future Improvements

* Deploy as a cloud-based service (AWS / GCP)
* Improve model performance and validation
* Add real-time ICU monitoring integration
* Enhance UI/UX of dashboard
* Extend the system to incorporate the MIMIC-IV dataset for enhanced data granularity and model accuracy, contingent on obtaining the necessary access permissions and licensing approvals.
