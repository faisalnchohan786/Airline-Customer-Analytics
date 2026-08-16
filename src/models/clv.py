"""Customer Lifetime Value prediction service."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Mapping

import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = PROJECT_ROOT / "models"
CLV_MODEL_PATH = MODEL_DIR / "clv_prediction_model.pkl"
METADATA_PATH = MODEL_DIR / "model_metadata.pkl"
FEATURES_PATH = MODEL_DIR / "clv_feature_columns.pkl"

DEFAULT_CLV_FEATURES = [
    "booking_frequency",
    "flight_frequency",
    "business_class_flights",
    "economy_class_flights",
    "comfort_class_flights",
    "cities_visited",
    "since_last_booking_days",
]


CLV_FEATURES = DEFAULT_CLV_FEATURES.copy()

@lru_cache(maxsize=1)
def load_feature_names() -> list[str]:
    if FEATURES_PATH.exists():
        return list(joblib.load(FEATURES_PATH))
    return DEFAULT_CLV_FEATURES.copy()


@lru_cache(maxsize=1)
def load_clv_model():
    """Load the persisted CLV regression model exported with Joblib."""
    if not CLV_MODEL_PATH.exists():
        raise FileNotFoundError(f"CLV model not found: {CLV_MODEL_PATH}")
    return joblib.load(CLV_MODEL_PATH)


@lru_cache(maxsize=1)
def load_model_metadata() -> dict:
    """Load model metrics and training metadata."""
    if not METADATA_PATH.exists():
        return {}
    return dict(joblib.load(METADATA_PATH))


def _validate_features(features: Mapping[str, float | int]) -> pd.DataFrame:
    names = load_feature_names()
    missing = [name for name in names if name not in features]
    if missing:
        raise ValueError(f"Missing CLV features: {', '.join(missing)}")

    row = {}
    for name in names:
        value = float(features[name])
        if value < 0:
            raise ValueError(f"{name} cannot be negative")
        row[name] = value
    return pd.DataFrame([row], columns=names)


def predict_clv(features: Mapping[str, float | int]) -> float:
    """Return predicted customer lifetime value for one customer profile."""
    frame = _validate_features(features)
    prediction = float(load_clv_model().predict(frame)[0])
    return max(0.0, prediction)


def clv_value_tier(value: float) -> str:
    """Provide a presentation band without claiming a trained classification label."""
    if value >= 200_000:
        return "Very High"
    if value >= 100_000:
        return "High"
    if value >= 50_000:
        return "Moderate"
    return "Lower"
