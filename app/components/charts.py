"""Plotly chart builders used across Streamlit pages."""
import pandas as pd
import plotly.express as px


def line_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    y_title: str = "",
    frequency: str = "daily",
):
    fig = px.line(df, x=x, y=y, markers=True, title=title)
    fig.update_layout(
        margin=dict(l=8, r=8, t=55, b=8),
        yaxis_title=y_title,
        xaxis_title="",
        hovermode="x unified",
    )
    if pd.api.types.is_datetime64_any_dtype(df[x]):
        if frequency == "daily":
            # Keep the underlying series daily, but deliberately show only a small
            # number of readable date labels. This prevents dense date-by-date
            # labels on portfolio charts while preserving daily observations.
            dates = pd.Series(pd.to_datetime(df[x])).dropna().drop_duplicates().sort_values()
            if len(dates) <= 10:
                tick_dates = dates.tolist()
            else:
                # Aim for roughly 7–9 labels and always include the latest date.
                step = max(1, int((len(dates) - 1) // 7))
                tick_dates = dates.iloc[::step].tolist()
                if dates.iloc[-1] not in tick_dates:
                    tick_dates.append(dates.iloc[-1])
            fig.update_xaxes(
                tickmode="array",
                tickvals=tick_dates,
                ticktext=[d.strftime("%d %b") for d in tick_dates],
                tickangle=0,
            )
        elif frequency == "weekly":
            fig.update_xaxes(dtick="D7", tickformat="%d %b")
        else:
            fig.update_xaxes(dtick="M1", tickformat="%b %Y")
    return fig


def bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    orientation: str = "v",
):
    if orientation == "h":
        fig = px.bar(df, x=y, y=x, orientation="h", title=title)
    else:
        fig = px.bar(df, x=x, y=y, title=title)
    fig.update_layout(
        margin=dict(l=8, r=8, t=55, b=8),
        xaxis_title="",
        yaxis_title="",
    )
    return fig


def donut_chart(df: pd.DataFrame, names: str, values: str, title: str):
    fig = px.pie(df, names=names, values=values, hole=0.62, title=title)
    fig.update_layout(
        margin=dict(l=8, r=8, t=55, b=8),
        legend_title_text="",
    )
    return fig


def scatter_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    size: str,
    hover_name: str,
    title: str,
):
    fig = px.scatter(
        df,
        x=x,
        y=y,
        size=size,
        hover_name=hover_name,
        title=title,
        size_max=42,
    )
    fig.update_layout(
        margin=dict(l=8, r=8, t=55, b=8),
        xaxis_title=x.replace("_", " ").title(),
        yaxis_title=y.replace("_", " ").title(),
    )
    return fig


def box_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    x_title: str = "",
    y_title: str = "",
):
    fig = px.box(df, x=x, y=y, points="outliers", title=title)
    fig.update_layout(
        margin=dict(l=8, r=8, t=55, b=8),
        xaxis_title=x_title,
        yaxis_title=y_title,
    )
    return fig
