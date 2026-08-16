import plotly.express as px
import streamlit as st

from src.analytics import get_customer_features, add_customer_priority
from app.components.charts import box_chart
from app.components.formatting import money, compact_number
from app.components.style import page_header, insight


def render():
    page_header(
        "Customer Intelligence",
        "Prioritise customers using observed value, repeat-flight engagement, and recency.",
    )

    features = add_customer_priority(get_customer_features())

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Unique Customers", compact_number(len(features)))
    c2.metric("Max Observed Value", money(features["lifetime_value"].max()))
    c3.metric("Median Observed Value", money(features["lifetime_value"].median()))
    c4.metric("Median Flight Frequency", f"{features['flight_frequency'].median():.0f}")
    c5.metric(
        "Median Days Since Booking",
        f"{features['since_last_booking_days'].median():.0f} days",
    )

    st.subheader("Customer Priority")
    st.caption(
        "Priority is a transparent rule-based layer using the 75th percentile of observed "
        "customer value, median flight frequency, and the 75th percentile of days since last booking."
    )

    priority_counts = (
        features["customer_priority"]
        .value_counts()
        .rename_axis("priority")
        .reset_index(name="customers")
    )
    priority_counts["share_percent"] = (
        priority_counts["customers"] / len(features) * 100
    ).round(1)

    cols = st.columns(min(5, len(priority_counts)))
    for col, (_, row) in zip(cols, priority_counts.iterrows()):
        col.metric(
            str(row["priority"]),
            f"{int(row['customers']):,}",
        )
        col.caption(f"{row['share_percent']:.1f}% of customers")

    left, right = st.columns(2)

    with left:
        top = features.head(10).copy()
        top["customer_id"] = [
            f"C{idx:06d}" for idx in range(1, len(top) + 1)
        ]
        top = top.sort_values("lifetime_value")
        fig = px.bar(
            top,
            x="lifetime_value",
            y="customer_id",
            orientation="h",
            title="Top Customers by Observed Customer Value",
            hover_data={
                "customer_id": True,
                "lifetime_value": ":,.0f",
                "flight_frequency": True,
                "since_last_booking_days": True,
                "customer_priority": True,
            },
        )
        fig.update_layout(
            margin=dict(l=8, r=8, t=55, b=8),
            xaxis_title="Observed Customer Value ($)",
            yaxis_title="Customer",
        )
        st.plotly_chart(fig, width="stretch")

    with right:
        box_data = features[
            ["flight_frequency", "lifetime_value"]
        ].copy()
        box_data["flight_frequency"] = box_data["flight_frequency"].astype(int).clip(upper=10)
        st.plotly_chart(
            box_chart(
                box_data,
                "flight_frequency",
                "lifetime_value",
                "Customer Lifetime Value by Flight Frequency",
                "Flight Frequency (10 = 10+ flights)",
                "Observed Customer Value ($)",
            ),
            width="stretch",
        )

    st.caption(
        "Customer IDs in the visual are display identifiers created for presentation. "
        "They are ranked by observed customer value; raw source passenger identifiers remain internal."
    )

    st.subheader("Customer Detail")
    display = features.copy()
    display["customer_id"] = [f"C{idx:06d}" for idx in range(1, len(display) + 1)]
    display_columns = [
        "customer_id",
        "lifetime_value",
        "flight_frequency",
        "booking_frequency",
        "since_last_booking_days",
        "avg_transaction_value",
        "cities_visited",
        "business_class_flights",
        "economy_class_flights",
        "comfort_class_flights",
        "customer_priority",
        "last_booking_date",
        "revenue_per_flight",
    ]
    st.dataframe(display[display_columns].head(250), width="stretch", hide_index=True)

    insight(
        "<b>Decision signal:</b> high observed value does not automatically mean a customer is "
        "currently engaged. Use value, repeat-flight behaviour, and recency together to identify "
        "VIP active customers, VIP customers at risk, emerging high-value customers, and lower-priority customers."
    )
