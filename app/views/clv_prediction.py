import streamlit as st

from src.models.clv import predict_clv, load_model_metadata, clv_value_tier, load_feature_names
from app.components.style import page_header, insight
from app.components.formatting import money


def render():
    page_header(
        "Customer Lifetime Value — What-If Prediction",
        "Estimate customer value from observed behavioural and fare-class features using the saved XGBoost model.",
    )

    metadata = load_model_metadata()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Model", str(metadata.get("best_clv_model", "XGBoost")))
    m2.metric("R²", f"{float(metadata.get('R2', 0.275)):.3f}")
    m3.metric("MAE", money(metadata.get("MAE", 28072)))
    m4.metric("RMSE", money(metadata.get("RMSE", 41198)))

    st.caption(
        "Use this interface for directional what-if analysis. The model is not a production-grade "
        "financial forecast and should not be used for automated customer-treatment decisions."
    )

    st.markdown("#### Customer profile")
    c1, c2, c3 = st.columns(3)
    booking_frequency = c1.number_input("Booking frequency", min_value=0, value=4, step=1)
    flight_frequency = c2.number_input("Flight frequency", min_value=0, value=6, step=1)
    cities_visited = c3.number_input("Cities visited", min_value=0, value=4, step=1)
    business = c1.number_input("Business-class flights", min_value=0, value=1, step=1)
    economy = c2.number_input("Economy-class flights", min_value=0, value=5, step=1)
    comfort = c3.number_input("Comfort-class flights", min_value=0, value=0, step=1)
    recency = st.slider("Days since last booking", min_value=0, max_value=365, value=30)

    if st.button("Predict Customer Lifetime Value", type="primary", width="stretch"):
        values = {
            "booking_frequency": booking_frequency,
            "flight_frequency": flight_frequency,
            "business_class_flights": business,
            "economy_class_flights": economy,
            "comfort_class_flights": comfort,
            "cities_visited": cities_visited,
            "since_last_booking_days": recency,
        }
        try:
            prediction = predict_clv(values)
            st.markdown("#### Prediction result")
            a, b = st.columns([1, 2])
            a.metric("Predicted Customer Lifetime Value", money(prediction))
            b.metric("Customer Value Band", clv_value_tier(prediction))
            st.caption(
                "Customer Value Band is a presentation aid derived from the predicted value; "
                "it is not a trained classification model."
            )
        except Exception as exc:
            st.error(f"Prediction could not be generated: {exc}")

    insight(
        "<b>Model governance:</b> R² is approximately 0.275, so this is an experimental portfolio "
        "baseline. Predictions should be treated as directional what-if estimates rather than production "
        "financial forecasts."
    )
