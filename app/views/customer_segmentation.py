import streamlit as st
import pandas as pd
import plotly.express as px

from src.analytics import get_customer_features
from src.models.segmentation import load_segmentation_assets, predict_segment
from app.components.style import page_header, insight
from app.components.formatting import money


def render():
    page_header(
        "Customer Segmentation",
        "Explore behavioural clusters and use the saved K-Means model for transparent segment inference.",
    )

    features = get_customer_features()

    try:
        # ================================================================
        # LOAD SAVED K-MEANS MODEL
        # ================================================================
        model, scaler, feature_names, segment_names = (
            load_segmentation_assets()
        )

        labels = model.predict(
            scaler.transform(
                features[feature_names].astype(float)
            )
        )

        labelled = features.copy()

        labelled["segment"] = (
            pd.Series(labels, index=features.index)
            .map(
                lambda x: segment_names.get(
                    int(x),
                    f"Segment {int(x)}",
                )
            )
        )

        # ================================================================
        # KPI CARDS
        # ================================================================
        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Customers",
            f"{len(features):,}",
        )

        c2.metric(
            "Median Observed Value",
            money(features["lifetime_value"].median()),
        )

        c3.metric(
            "Median Flights",
            f"{features['flight_frequency'].median():.0f}",
        )

        c4.metric(
            "Median Recency",
            f"{features['since_last_booking_days'].median():.0f} days",
        )

        # ================================================================
        # SEGMENT PROFILE
        # ================================================================
        st.subheader("Segment Profile")

        profile = (
            labelled.groupby("segment")
            .agg(
                Customers=("passenger_id", "count"),
                Customer_Share=(
                    "passenger_id",
                    lambda s: len(s) / len(labelled) * 100,
                ),
                Median_Value=("lifetime_value", "median"),
                Median_Flights=("flight_frequency", "median"),
                Median_Recency_Days=(
                    "since_last_booking_days",
                    "median",
                ),
            )
            .reset_index()
        )

        profile["Customer_Share"] = (
            profile["Customer_Share"].round(1)
        )

        # ================================================================
        # DISPLAY TABLE
        # ================================================================
        display_profile = profile.rename(
            columns={
                "segment": "Segment",
                "Customer_Share": "Customer Share",
                "Median_Value": "Median Value",
                "Median_Flights": "Median Flights",
                "Median_Recency_Days": "Median Recency (Days)",
            }
        )

        st.dataframe(
            display_profile,
            width="stretch",
            hide_index=True,
        )

        # ================================================================
        # SEGMENT BEHAVIOUR DISTRIBUTION
        # ================================================================
        st.subheader("Segment Behaviour Distribution")

        st.caption(
            "Customer share, observed value and recency are shown "
            "side-by-side for direct segment comparison."
        )

        share_plot = profile.sort_values(
            "Customer_Share",
            ascending=True,
        ).copy()

        value_plot = profile.sort_values(
            "Median_Value",
            ascending=True,
        ).copy()

        recency_plot = profile.sort_values(
            "Median_Recency_Days",
            ascending=True,
        ).copy()

        # ================================================================
        # CUSTOMER SHARE CHART
        # ================================================================
        fig_share = px.bar(
            share_plot,
            x="Customer_Share",
            y="segment",
            orientation="h",
        )

        fig_share.update_traces(
            text=share_plot["Customer_Share"],
            texttemplate="%{text:.1f}%",
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Customer Share: %{x:.1f}%"
                "<extra></extra>"
            ),
        )

        fig_share.update_layout(
            title=dict(
                text="Customer Share by Segment",
                x=0,
                xanchor="left",
                y=0.98,
                yanchor="top",
            ),
            margin=dict(
                l=8,
                r=25,
                t=55,
                b=8,
            ),
            height=320,
            xaxis_title="Customers (%)",
            yaxis_title="",
            xaxis_range=[
                0,
                max(
                    50,
                    float(
                        share_plot["Customer_Share"].max()
                    ) * 1.2,
                ),
            ],
        )

        # ================================================================
        # MEDIAN OBSERVED VALUE CHART
        # ================================================================
        fig_value = px.bar(
            value_plot,
            x="Median_Value",
            y="segment",
            orientation="h",
        )

        # Explicit labels to prevent incorrect Plotly formatting.
        value_labels = [
            f"${float(value) / 1000:.1f}K"
            for value in value_plot["Median_Value"]
        ]

        fig_value.update_traces(
            text=value_labels,
            texttemplate="%{text}",
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Median Observed Value: $%{x:,.0f}"
                "<extra></extra>"
            ),
        )

        fig_value.update_layout(
            title=dict(
                text="Median Observed Value by Segment",
                x=0,
                xanchor="left",
                y=0.98,
                yanchor="top",
            ),
            margin=dict(
                l=8,
                r=40,
                t=55,
                b=8,
            ),
            height=320,
            xaxis_title="Median Observed Value ($)",
            yaxis_title="",
        )

        # ================================================================
        # MEDIAN RECENCY CHART
        # ================================================================
        fig_recency = px.bar(
            recency_plot,
            x="Median_Recency_Days",
            y="segment",
            orientation="h",
        )

        fig_recency.update_traces(
            text=recency_plot["Median_Recency_Days"],
            texttemplate="%{text:.0f} days",
            textposition="inside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Median Recency: %{x:.0f} days"
                "<extra></extra>"
            ),
        )

        fig_recency.update_layout(
            title=dict(
                text="Median Recency by Segment",
                x=0,
                xanchor="left",
                y=0.98,
                yanchor="top",
            ),
            margin=dict(
                l=8,
                r=8,
                t=55,
                b=8,
            ),
            height=320,
            xaxis_title="Median Days Since Booking",
            yaxis_title="",
        )

        # ================================================================
        # THREE CHARTS IN ONE ROW
        # ================================================================
        col_share, col_value, col_recency = st.columns(3)

        with col_share:
            st.plotly_chart(
                fig_share,
                width="stretch",
                config={"displayModeBar": False},
            )

        with col_value:
            st.plotly_chart(
                fig_value,
                width="stretch",
                config={"displayModeBar": False},
            )

        with col_recency:
            st.plotly_chart(
                fig_recency,
                width="stretch",
                config={"displayModeBar": False},
            )

        # ================================================================
        # LIVE SEGMENT INFERENCE
        # ================================================================
        st.subheader("Live Segment Inference")

        st.caption(
            "The live form uses the exact four features required by "
            "the persisted K-Means model. Booking frequency is fixed "
            "at 1 because it has zero variance in the training data."
        )

        st.success(
            "K-Means model ready for live inference."
        )

        medians = features[feature_names].median()

        values = {}

        cols = st.columns(4)

        for idx, name in enumerate(feature_names):

            label = name.replace(
                "_",
                " ",
            ).title()

            if name == "booking_frequency":

                values[name] = 1.0

                cols[idx].number_input(
                    label,
                    min_value=1.0,
                    value=1.0,
                    step=1.0,
                    disabled=True,
                    help=(
                        "This feature has no variance in the "
                        "persisted training data."
                    ),
                )

            else:

                default = float(
                    medians[name]
                )

                step = (
                    1.0
                    if name != "avg_transaction_value"
                    else 100.0
                )

                values[name] = cols[idx].number_input(
                    label,
                    min_value=0.0,
                    value=default,
                    step=step,
                )

        # ================================================================
        # PREDICT SEGMENT
        # ================================================================
        if st.button(
            "Assign Customer Segment",
            type="primary",
        ):

            label = predict_segment(values)

            st.success(
                f"Predicted segment: **{label}**"
            )

            selected = features.copy()

            selected["segment"] = model.predict(
                scaler.transform(
                    features[feature_names].astype(float)
                )
            )

            segment_id = next(
                (
                    int(k)
                    for k, v in segment_names.items()
                    if v == label
                ),
                None,
            )

            if segment_id is not None:

                profile_row = features.iloc[
                    selected["segment"].to_numpy()
                    == segment_id
                ]

                if not profile_row.empty:

                    a, b, c = st.columns(3)

                    a.metric(
                        "Typical Observed Value",
                        money(
                            profile_row[
                                "lifetime_value"
                            ].median()
                        ),
                    )

                    b.metric(
                        "Typical Flight Frequency",
                        f"{profile_row['flight_frequency'].median():.0f}",
                    )

                    c.metric(
                        "Typical Recency",
                        f"{profile_row['since_last_booking_days'].median():.0f} days",
                    )

        # ================================================================
        # SEGMENT DEFINITIONS
        # ================================================================
        st.subheader("Segment Definitions")

        definitions = {
            "VIP Premium Customers": (
                "Highest-value behavioural cluster with "
                "substantially above-average monetary contribution."
            ),
            "High-Value Customers": (
                "Customers with elevated observed value "
                "and stronger commercial engagement."
            ),
            "Low-Value Active Customers": (
                "Customers showing activity but relatively "
                "lower observed monetary contribution."
            ),
            "At-Risk Customers": (
                "Customers characterised by weaker recent "
                "engagement relative to the other clusters."
            ),
        }

        definition_order = [
            "VIP Premium Customers",
            "High-Value Customers",
            "Low-Value Active Customers",
            "At-Risk Customers",
        ]

        for name in definition_order:
            if name in segment_names.values():
                st.markdown(
                    f"**{name}** — "
                    f"{definitions.get(name, 'Behavioural cluster identified by K-Means.')}"
                )

    except Exception as exc:

        st.error(
            "The saved segmentation model could not be loaded."
        )

        st.caption(
            str(exc)
        )

        st.info(
            "The analytical customer features remain available, "
            "but live inference requires compatible Joblib "
            "model artefacts."
        )

    # ================================================================
    # GOVERNANCE
    # ================================================================
    insight(
        "<b>Governance:</b> K-Means is unsupervised. Segment names "
        "are business interpretations of cluster profiles, not "
        "ground-truth labels or predictions of future customer behaviour."
    )