# AML Risk API

An Anti-Money Laundering (AML) transaction risk scoring system built on the [PaySim](https://www.kaggle.com/datasets/ealaxi/paysim1) synthetic mobile money dataset. The project covers the full ML lifecycle — data ingestion, exploratory analysis, model comparison, training, and production serving — all containerized with Docker Compose.

---

## Architecture

```
aml-risk-api/
├── download_data.py            # Kaggle dataset fetch script
├── train_model.py              # Train winner model on full data, save artifacts
├── sample_requests.json        # Known fraud + legitimate payloads for testing
├── docker-compose.yml
├── api/
│   ├── main.py                 # FastAPI app — GET /, GET /health, POST /predict
│   ├── schema/
│   │   ├── user_input.py       # Pydantic request model (transaction features)
│   │   └── prediction_response.py  # Pydantic response model (score, band, label)
│   ├── model/
│   │   ├── predict.py          # Loads model.pkl + config.json, exposes predict()
│   │   ├── model.pkl           # Serialized sklearn/XGBoost model
│   │   ├── config.json         # Decision threshold + risk band boundaries
│   │   ├── metrics.json        # Eval metrics snapshot
│   │   ├── orig_agg_lookup.parquet  # Per-originator behavioural aggregates
│   │   └── dest_agg_lookup.parquet  # Per-destination behavioural aggregates
│   ├── requirements.txt
│   └── Dockerfile
├── ui/
│   ├── app.py                  # Streamlit front-end — calls POST /predict
│   ├── requirements.txt
│   └── Dockerfile
└── notebooks/
    ├── 1_eda.ipynb             # Exploratory data analysis
    ├── 02_model_comparision.ipynb  # Candidate model comparison
    ├── 1_eda_report.md         # GitHub-readable EDA summary
    └── docs/                   # Quarto-rendered HTML reports
```

### Request → Response flow

1. The Streamlit UI submits a transaction JSON to `POST /predict`.
2. `user_input.py` validates the incoming request via Pydantic.
3. `predict.py` loads `model.pkl` and applies the trained classifier to produce a fraud probability.
4. The probability is mapped to a named risk band using the cutoffs in `config.json`.
5. `prediction_response.py` structures the response: risk score, risk band, and `is_fraud` label.

---

## Quickstart

### 1. Get the data

The PaySim CSV is too large for git. Fetch it from Kaggle:

```bash
python download_data.py
```

> Requires a Kaggle API token (`~/.kaggle/kaggle.json`).

### 2. Set up the Python environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

pip install -r api/requirements.txt
pip install -r ui/requirements.txt
```

### 3. Train the model

```bash
python train_model.py
```

Writes:
- `api/model/model.pkl` — serialized classifier
- `api/model/config.json` — decision threshold + risk band cutoffs
- `api/model/metrics.json` — evaluation metrics snapshot

### 4. Run with Docker Compose (recommended)

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| UI | http://localhost:8501 |

### 5. Run individual services (dev mode)

```bash
# API
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# UI
streamlit run ui/app.py
```

---

## API reference

### `POST /predict`

Scores a single transaction and returns a risk assessment.

**Request body** (JSON):

```json
{
  "step": 1,
  "type": "TRANSFER",
  "amount": 181.0,
  "nameOrig": "C1305486145",
  "oldbalanceOrg": 181.0,
  "newbalanceOrig": 0.0,
  "nameDest": "C553264065",
  "oldbalanceDest": 0.0,
  "newbalanceDest": 0.0
}
```

**Response** (JSON):

```json
{
  "fraud_probability": 0.94,
  "risk_band": "HIGH",
  "is_fraud": true
}
```

### `GET /health`

Returns `{"status": "ok"}` — suitable for container health checks.

### `GET /`

Returns API metadata and version info.

---

## Risk bands

Risk band boundaries are defined in `api/model/config.json` and are not hardcoded in application logic. Typical bands:

| Band | Score range | Description |
|------|-------------|-------------|
| LOW | < 0.3 | Likely legitimate transaction |
| MEDIUM | 0.3 – 0.7 | Elevated risk, warrants review |
| HIGH | ≥ 0.7 | High fraud probability, flag for investigation |

---

## Notebooks

Notebooks are rendered to HTML via [Quarto](https://quarto.org/) and committed under `notebooks/docs/`.

```bash
quarto render notebooks/1_eda.ipynb --to html --output-dir docs
quarto render notebooks/02_model_comparision.ipynb --to html --output-dir docs
```

| Notebook | Purpose |
|----------|---------|
| `1_eda.ipynb` | Class imbalance, feature distributions, correlation analysis |
| `02_model_comparision.ipynb` | Compares candidate models (precision, recall, AUC-PR), selects winner |

A GitHub-readable EDA summary is also available at [`notebooks/1_eda_report.md`](notebooks/1_eda_report.md).

---

## Dataset

[PaySim](https://www.kaggle.com/datasets/ealaxi/paysim1) is a synthetic mobile money transaction simulator based on real transaction logs. It contains ~6.3 million transactions with a ~0.13% fraud rate, making it a realistic highly-imbalanced classification benchmark.

---

## License

This project is for educational and demonstration purposes. The PaySim dataset is provided by Kaggle under its own terms.
