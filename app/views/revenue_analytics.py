import plotly.express as px
import streamlit as st

from src.analytics import get_fare_class_performance, get_daily_trends
from app.components.charts import bar_chart, donut_chart, line_chart
from app.components.formatting import money
from app.components.style import page_header, insight


def render():
    page_header(
        "Revenue & Fare Class",
        "Compare fare-class revenue contribution, ticket-flight volume, yield, and daily pricing behaviour.",
    )

    fares = get_fare_class_performance()
    trends = get_daily_trends()
    leader = fares.iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Leading Revenue Class", leader["seat_class"])
    c2.metric("Leading Class Revenue", money(leader["total_revenue"], compact=True))
    c3.metric("Highest Avg Fare", money(fares["avg_ticket_price"].max()))
    c4.metric("Fare Classes", len(fares))

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            donut_chart(fares, "seat_class", "total_revenue", "Revenue Contribution"),
            width="stretch",
        )
    with right:
        st.plotly_chart(
            bar_chart(
                fares,
                "seat_class",
                "avg_ticket_price",
                "Average Ticket-Flight Price",
            ),
            width="stretch",
        )

    share = fares[
        ["seat_class", "percent_of_ticket_flight_legs", "percent_of_total_revenue"]
    ].melt(
        id_vars="seat_class",
        var_name="metric",
        value_name="share_percent",
    )
    share["metric"] = share["metric"].map(
        {
            "percent_of_ticket_flight_legs": "Ticket-Flight Share",
            "percent_of_total_revenue": "Revenue Share",
        }
    )
    fig = px.bar(
        share,
        x="seat_class",
        y="share_percent",
        color="metric",
        barmode="group",
        title="Revenue Share vs Ticket-Flight Share",
        text_auto=".1f",
    )
    fig.update_layout(
        margin=dict(l=8, r=8, t=55, b=8),
        xaxis_title="Fare Class",
        yaxis_title="Share (%)",
        legend_title_text="",
    )
    st.plotly_chart(fig, width="stretch")

    st.caption(
        "Ticket-Flight Share is calculated from ticket-flight records. A single ticket can "
        "contain multiple flight legs and therefore cannot always be assigned to one fare class."
    )

    st.plotly_chart(
        line_chart(
            trends,
            "booking_date",
            "avg_ticket_price",
            "Daily Average Ticket-Flight Price",
            "Average Fare ($)",
            frequency="daily",
        ),
        width="stretch",
    )

    st.dataframe(fares, width="stretch", hide_index=True)

    insight(
        "<b>Commercial use:</b> compare revenue share with ticket-flight share. "
        "A fare class can carry fewer flight legs while contributing disproportionately "
        "to revenue because of higher average yield."
    )
