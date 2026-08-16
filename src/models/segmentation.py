"""Customer segmentation inference with portable Joblib loading."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Mapping

import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "kmeans_customer_segmentation.pkl"
SCALER_PATH = MODEL_DIR / "kmeans_scaler.pkl"
FEATURES_PATH = MODEL_DIR / "kmeans_feature_columns.pkl"
NAMES_PATH = MODEL_DIR / "segment_names.pkl"


@lru_cache(maxsize=1)
def load_segmentation_assets():
    """Load the Joblib-exported K-Means assets."""
    try:
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        features = list(joblib.load(FEATURES_PATH))
        names = dict(joblib.load(NAMES_PATH))
        return model, scaler, features, names
    except Exception as exc:
        raise RuntimeError(
            "The saved K-Means/scaler artefacts could not be loaded. "
            "Ensure the project dependencies match the model training environment "
            "and that the files under models/ are intact."
        ) from exc


def predict_segment(values: Mapping[str, float | int]) -> str:
    model, scaler, features, names = load_segmentation_assets()
    missing = [name for name in features if name not in values]
    if missing:
        raise ValueError(f"Missing segmentation features: {', '.join(missing)}")

    frame = pd.DataFrame(
        [{name: float(values[name]) for name in features}],
        columns=features,
    )
    label = int(model.predict(scaler.transform(frame))[0])
    return names.get(label, f"Segment {label}")


def predict_segments(frame: pd.DataFrame) -> pd.Series:
    """Assign segment labels to a customer feature DataFrame."""
    model, scaler, features, names = load_segmentation_assets()
    missing = [name for name in features if name not in frame.columns]
    if missing:
        raise ValueError(f"Missing segmentation features: {', '.join(missing)}")

    values = frame[features].astype(float)
    labels = model.predict(scaler.transform(values))
    return pd.Series(labels, index=frame.index).map(
        lambda label: names.get(int(label), f"Segment {int(label)}")
    )
