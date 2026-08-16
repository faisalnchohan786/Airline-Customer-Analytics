import streamlit as st

from src.analytics import get_aircraft_performance, get_flight_status
from app.components.charts import bar_chart, scatter_chart
from app.components.formatting import money
from app.components.style import page_header, insight


def render():
    page_header(
        "Fleet & Operations",
        "Assess aircraft commercial efficiency, load factor, revenue intensity, and operational status.",
    )

    fleet = get_aircraft_performance()
    status = get_flight_status()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Aircraft Types", len(fleet))
    c2.metric("Highest Load Factor", f"{fleet['load_factor_percent'].max():.1f}%")
    c3.metric("Highest Revenue / Flight", money(fleet["revenue_per_flight"].max()))
    c4.metric("Recorded Statuses", len(status))

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            scatter_chart(
                fleet,
                "load_factor_percent",
                "revenue_per_available_seat",
                "total_flights",
                "aircraft_model",
                "Load Factor vs Revenue per Available Seat",
            ),
            width="stretch",
        )
        st.caption("Bubble size represents total flights.")

    with right:
        st.plotly_chart(
            bar_chart(
                status.sort_values("total_flights"),
                "status",
                "total_flights",
                "Flight Status Volume",
                orientation="h",
            ),
            width="stretch",
        )

    plot = fleet.sort_values("total_revenue")
    st.plotly_chart(
        bar_chart(
            plot,
            "aircraft_model",
            "total_revenue",
            "Total Revenue by Aircraft Model",
            orientation="h",
        ),
        width="stretch",
    )

    display = fleet[
        [
            "aircraft_model",
            "total_flights",
            "passengers_flown",
            "total_revenue",
            "load_factor_percent",
            "revenue_per_flight",
            "revenue_per_available_seat",
        ]
    ].copy()
    st.subheader("Aircraft Commercial Efficiency")
    st.dataframe(display, width="stretch", hide_index=True)

    insight(
        "<b>Fleet interpretation:</b> total revenue is influenced by flight frequency and aircraft capacity. "
        "Compare load factor, revenue per flight, and revenue per available seat together. "
        "These are commercial-efficiency metrics, not profitability measures."
    )
