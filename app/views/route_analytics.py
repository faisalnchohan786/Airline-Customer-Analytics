import streamlit as st

from src.analytics import get_route_performance, get_hub_performance
from app.components.charts import bar_chart, scatter_chart
from app.components.formatting import money
from app.components.style import page_header, insight


def render():
    page_header(
        "Route & Airport Analytics",
        "Compare network demand, revenue, load factor, flight frequency, and airport movements.",
    )

    route_limit = st.sidebar.slider("Routes to analyse", 10, 100, 30, 10)
    routes = get_route_performance(route_limit)
    hubs = get_hub_performance(20)
    routes = routes.assign(
        route=routes["departure_airport"] + " → " + routes["arrival_airport"]
    )

    revenue_cutoff = routes["total_revenue"].median()
    load_cutoff = routes["load_factor_percent"].median()

    routes["commercial_profile"] = "Review / lower commercial signal"
    routes.loc[
        (routes["total_revenue"] >= revenue_cutoff)
        & (routes["load_factor_percent"] >= load_cutoff),
        "commercial_profile",
    ] = "Core commercial performer"
    routes.loc[
        (routes["total_revenue"] >= revenue_cutoff)
        & (routes["load_factor_percent"] < load_cutoff),
        "commercial_profile",
    ] = "High-revenue / lower-load opportunity"
    routes.loc[
        (routes["total_revenue"] < revenue_cutoff)
        & (routes["load_factor_percent"] >= load_cutoff),
        "commercial_profile",
    ] = "High-load / lower-revenue opportunity"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Routes Shown", len(routes))
    c2.metric("Top Route Revenue", money(routes["total_revenue"].max()))
    c3.metric("Highest Load Factor", f"{routes['load_factor_percent'].max():.1f}%")
    c4.metric("Airport Flight Movements", f"{int(hubs['total_flight_movements'].max()):,}")

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            bar_chart(
                routes.head(12).sort_values("total_revenue"),
                "route",
                "total_revenue",
                "Top Routes by Revenue",
                orientation="h",
            ),
            width="stretch",
        )
    with right:
        st.plotly_chart(
            scatter_chart(
                routes,
                "load_factor_percent",
                "revenue_per_flight",
                "number_of_flights",
                "route",
                "Load Factor vs Revenue per Flight",
            ),
            width="stretch",
        )
        st.caption("Bubble size represents flight frequency.")

    plot = hubs.head(12).sort_values("total_flight_movements")
    st.plotly_chart(
        bar_chart(
            plot,
            "airport_code",
            "total_flight_movements",
            "Flight Movements by Airport",
            orientation="h",
        ),
        width="stretch",
    )

    st.subheader("Route Commercial Performance")
    display_columns = [
        "route",
        "departure_city",
        "arrival_city",
        "number_of_flights",
        "tickets_sold",
        "passengers_flown",
        "total_revenue",
        "avg_ticket_price",
        "load_factor_percent",
        "revenue_per_flight",
        "commercial_profile",
    ]
    st.dataframe(
        routes[display_columns],
        width="stretch",
        hide_index=True,
    )

    insight(
        "<b>Decision signal:</b> high revenue and high load factor measure different dimensions. "
        "Core commercial performers combine both relative signals, while high-revenue/low-load routes "
        "may warrant yield or capacity investigation. These are analytical signals, not profitability estimates."
    )
