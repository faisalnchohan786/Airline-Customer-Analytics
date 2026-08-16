"""Streamlit application for the Airline Analytics & AI decision-intelligence platform."""
from pathlib import Path
import sys

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.components.style import apply_app_style
from app.views import (
    executive_overview,
    customer_analytics,
    route_analytics,
    revenue_analytics,
    fleet_analytics,
    customer_segmentation,
    clv_prediction,
    ai_assistant,
    about_project,
)
from src.database import DEFAULT_DB_PATH

st.set_page_config(
    page_title="Airline Analytics & AI",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_app_style()

PAGES = {
    "Executive Overview": executive_overview.render,
    "Customer Intelligence": customer_analytics.render,
    "Route & Airport Analytics": route_analytics.render,
    "Revenue & Fare Class": revenue_analytics.render,
    "Fleet & Operations": fleet_analytics.render,
    "Customer Segmentation": customer_segmentation.render,
    "CLV Prediction": clv_prediction.render,
    "AI Analytics Assistant": ai_assistant.render,
    "Project & Methodology": about_project.render,
}

if "current_page" not in st.session_state:
    st.session_state.current_page = "Executive Overview"


def _nav_button(label: str) -> None:
    is_active = st.session_state.current_page == label
    if st.sidebar.button(
        label,
        key=f"nav_{label}",
        width="stretch",
        type="primary" if is_active else "secondary",
    ):
        st.session_state.current_page = label
        st.rerun()


st.sidebar.markdown("## Airline Analytics & AI")
st.sidebar.caption("Decision Intelligence Platform")
st.sidebar.divider()

st.sidebar.markdown("**EXECUTIVE**")
_nav_button("Executive Overview")

st.sidebar.markdown("**CUSTOMER INTELLIGENCE**")
_nav_button("Customer Intelligence")
_nav_button("Customer Segmentation")
_nav_button("CLV Prediction")

st.sidebar.markdown("**COMMERCIAL & OPERATIONS**")
_nav_button("Route & Airport Analytics")
_nav_button("Revenue & Fare Class")
_nav_button("Fleet & Operations")

st.sidebar.markdown("**AI & GOVERNANCE**")
_nav_button("AI Analytics Assistant")
_nav_button("Project & Methodology")

st.sidebar.divider()
st.sidebar.caption("Portfolio Decision Intelligence Platform")

if not DEFAULT_DB_PATH.exists():
    st.error("Airline database not found.")
    st.code("data/travel.sqlite")
    st.info(
        "Place your local travel.sqlite file in the data/ folder, then restart the application. "
        "The database is intentionally excluded from GitHub because it exceeds GitHub's standard "
        "single-file limit."
    )
    st.stop()

try:
    PAGES[st.session_state.current_page]()
except FileNotFoundError as exc:
    st.error(str(exc))
except Exception as exc:
    st.error("This page could not be rendered with the current local environment.")
    st.exception(exc)
