from fastapi import FastAPI, HTTPException

from api.schema.user_input import UserInput
from api.schema.prediction_response import PredictionResponse
from api.model.predict import predict, MODEL, CONFIG

app = FastAPI(
    title="AML Transaction Monitoring API",
    version="1.0.0",
    description="Real-time fraud scoring API. Returns risk score, risk band, and fraud decision for a given transaction."
)


@app.get("/")
def home():
    return {
        "service": "AML Transaction Monitoring API",
        "version": "1.0.0",
        "status":  "running",
        "docs":    "/docs"
    }


@app.get("/health")
def health():
    return {
        "status":       "ok",
        "model_loaded": MODEL is not None,
        "n_features":   len(CONFIG["feature_columns"]),
        "threshold":    CONFIG["threshold"]
    }


@app.post("/predict", response_model=PredictionResponse)
def predict_endpoint(payload: UserInput):
    try:
        return predict(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))