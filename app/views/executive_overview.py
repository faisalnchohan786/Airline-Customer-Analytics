import streamlit as st

from src.analytics import (
    get_executive_kpis,
    get_daily_trends,
    get_route_performance,
    get_fare_class_performance,
)
from app.components.charts import line_chart, bar_chart, donut_chart
from app.components.formatting import compact_number, money
from app.components.style import page_header, insight


def render():
    page_header(
        "Executive Overview",
        "Executive view of commercial scale, daily customer activity, fare mix, and route concentration.",
    )

    kpis = get_executive_kpis()
    cols = st.columns(6)
    metrics = [
        ("Total Revenue", money(kpis["total_revenue"], compact=True)),
        ("Bookings", compact_number(kpis["total_bookings"])),
        ("Operated Flights", compact_number(kpis["total_completed_flights"])),
        ("Tickets", compact_number(kpis["total_tickets"])),
        ("Unique Customers", compact_number(kpis["unique_customers"])),
        ("Avg Fare Amount", money(kpis["avg_ticket_value"])),
    ]
    for col, (label, value) in zip(cols, metrics):
        col.metric(label, value)

    trends = get_daily_trends()
    routes = get_route_performance(10)
    fares = get_fare_class_performance()

    left, right = st.columns([1.65, 1])
    with left:
        st.plotly_chart(
            line_chart(
                trends,
                "booking_date",
                "total_revenue",
                "Daily Revenue",
                "Revenue ($)",
                frequency="daily",
            ),
            width="stretch",
        )
    with right:
        st.plotly_chart(
            donut_chart(
                fares,
                "seat_class",
                "total_revenue",
                "Revenue Contribution by Fare Class",
            ),
            width="stretch",
        )

    left, right = st.columns(2)
    with left:
        route_labels = (
            routes.assign(
                route=routes["departure_airport"] + " → " + routes["arrival_airport"]
            )
            .head(8)
            .sort_values("total_revenue")
        )
        st.plotly_chart(
            bar_chart(
                route_labels,
                "route",
                "total_revenue",
                "Top Routes by Revenue",
                orientation="h",
            ),
            width="stretch",
        )
    with right:
        st.plotly_chart(
            line_chart(
                trends,
                "booking_date",
                "unique_customers",
                "Daily Unique Customers",
                "Customers",
                frequency="daily",
            ),
            width="stretch",
        )

    latest_date = trends["booking_date"].max()
    top = routes.iloc[0]
    peak = trends.loc[trends["total_revenue"].idxmax()]
    st.caption(
        f"Data-quality note: the latest available date is {latest_date.strftime('%d %b %Y')}. "
        "If it represents a partial reporting period, avoid comparing it directly with complete days."
    )

    insight(
        f"<b>Decision signal:</b> {top['departure_airport']} → {top['arrival_airport']} "
        f"has the highest recorded route revenue in the current view. The highest-revenue "
        f"day was {peak['booking_date'].strftime('%d %b %Y')}. Use Route Analytics to compare "
        "revenue with load factor and flight frequency before assessing commercial performance; "
        "revenue alone does not establish profitability."
    )
