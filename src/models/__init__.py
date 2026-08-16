"""Machine-learning services for the Airline Intelligence Platform."""
from .clv import CLV_FEATURES, load_clv_model, predict_clv, load_model_metadata
from .segmentation import load_segmentation_assets, predict_segment, predict_segments

__all__ = [
    "CLV_FEATURES", "load_clv_model", "predict_clv", "load_model_metadata",
    "load_segmentation_assets", "predict_segment", "predict_segments",
]
