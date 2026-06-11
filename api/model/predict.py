import json
import pickle
from pathlib import Path

import pandas as pd

_DIR    = Path(__file__).parent
CONFIG  = json.load(open(_DIR / "config.json"))
MODEL   = pickle.load(open(_DIR / "model.pkl", "rb"))

FEATURE_COLUMNS = CONFIG["feature_columns"]
THRESHOLD       = CONFIG["threshold"]
RISK_BANDS      = CONFIG["risk_bands"]


def _get_risk_band(score: float) -> str:
    for band_name, (low, high) in RISK_BANDS.items():
        if low <= score < high:
            return band_name
    return "high"


def predict(user_input) -> dict:
    X     = pd.DataFrame([user_input.model_dump()])[FEATURE_COLUMNS]
    score = float(MODEL.predict_proba(X)[0, 1])
    return {
        "risk_score":     round(score, 6),
        "risk_band":      _get_risk_band(score),
        "is_fraud":       score >= THRESHOLD,
        "threshold_used": THRESHOLD,
    }