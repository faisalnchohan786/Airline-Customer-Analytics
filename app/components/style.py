"""Application-wide presentation styling."""
import streamlit as st


def apply_app_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --aviation-bg: #0B0F14;
            --aviation-panel: #111820;
            --aviation-blue: #7CC4F4;
            --aviation-red: #E35D6A;
            --aviation-green: #5CC8A1;
        }
        .block-container {padding-top: 1.8rem; padding-bottom: 3rem; max-width: 1500px;}
        [data-testid="stSidebar"] {border-right: 1px solid rgba(124,196,244,.14);}
        [data-testid="stSidebar"] .stButton button {
            border-radius: 8px;
            min-height: 2.25rem;
            justify-content: flex-start;
            font-size: .88rem;
        }
        [data-testid="stSidebar"] .stButton {margin-bottom: .15rem;}
        [data-testid="stSidebar"] hr {margin: .65rem 0;}
        .app-eyebrow {font-size:.78rem; letter-spacing:.11em; font-weight:700; opacity:.62; text-transform:uppercase;}
        .app-title {font-size:2.25rem; font-weight:750; line-height:1.08; margin:.25rem 0 .35rem 0;}
        .app-subtitle {font-size:1rem; opacity:.72; margin-bottom:1.15rem; max-width:900px;}
        .section-title {font-size:1.2rem; font-weight:700; margin-top:.35rem; margin-bottom:.25rem;}
        .insight-box {border:1px solid rgba(124,196,244,.20); border-left:3px solid var(--aviation-blue); border-radius:12px; padding:14px 16px; margin-top:8px;}
        .model-note {font-size:.88rem; opacity:.72;}
        div[data-testid="stMetric"] {border:1px solid rgba(124,196,244,.16); padding:14px 16px; border-radius:12px;}
        [data-testid="stSidebar"] .stButton button[kind="primary"] {
            border-color: rgba(124,196,244,.55);
            color: #0B0F14;
            background: #7CC4F4;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str, eyebrow: str = "Airline Analytics & AI") -> None:
    st.markdown(f'<div class="app-eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="app-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="app-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def insight(text: str) -> None:
    st.markdown(f'<div class="insight-box">{text}</div>', unsafe_allow_html=True)
