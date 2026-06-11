from enum import Enum
from pydantic import BaseModel, Field


class RiskBand(str, Enum):
    low    = "low"
    medium = "medium"
    high   = "high"


class PredictionResponse(BaseModel):
    risk_score: float = Field(
        ...,
        description="Raw fraud probability from the model (0.0 – 1.0).",
        examples=[0.9978]
    )
    risk_band: RiskBand = Field(
        ...,
        description="Categorical risk tier: low (0–0.3), medium (0.3–0.7), high (0.7–1.0).",
        examples=["high"]
    )
    is_fraud: bool = Field(
        ...,
        description="True if risk_score exceeds the trained threshold (0.994579).",
        examples=[True]
    )
    threshold_used: float = Field(
        ...,
        description="Decision threshold applied — sourced from config.json, set via F1 maximisation on the test set.",
        examples=[0.994579]
    )