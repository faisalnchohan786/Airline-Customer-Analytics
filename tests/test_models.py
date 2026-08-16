from src.models.clv import load_model_metadata, predict_clv
from src.models.segmentation import load_segmentation_assets


def test_model_metadata_has_metrics():
    meta = load_model_metadata()
    assert meta["best_clv_model"] == "XGBoost"
    assert "R2" in meta


def test_clv_prediction_is_non_negative():
    value = predict_clv({
        "booking_frequency": 5,
        "flight_frequency": 8,
        "business_class_flights": 2,
        "economy_class_flights": 5,
        "comfort_class_flights": 1,
        "cities_visited": 5,
        "since_last_booking_days": 30,
    })
    assert value >= 0


def test_segmentation_assets_are_loadable():
    model, scaler, features, names = load_segmentation_assets()
    assert model.n_clusters == 4
    assert scaler.n_features_in_ == len(features) == 4
    assert len(names) == 4
