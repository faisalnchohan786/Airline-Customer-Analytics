"""Portfolio-facing project methodology page."""
import streamlit as st


def render() -> None:
    st.title("Project & Methodology")
    st.caption("How the Airline Analytics & AI Platform turns airline data into decision support.")

    st.markdown("## Business objective")
    st.write(
        "Analyse airline bookings, tickets, flights, routes, aircraft and customer behaviour, "
        "then extend descriptive analytics with customer segmentation, CLV prediction and a grounded local AI assistant."
    )

    st.markdown("## Analytical workflow")
    st.code(
        "SQLite airline data\n"
        "    -> SQL/Pandas analytics\n"
        "    -> Business KPIs\n"
        "    -> Customer priority + K-Means segmentation\n"
        "    -> CLV prediction\n"
        "    -> Targeted analytics grounding\n"
        "    -> Local Ollama assistant\n"
        "    -> Streamlit decision support",
        language="text",
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Analytics layer", "SQL + Pandas")
    c2.metric("Predictive model", "XGBoost CLV")
    c3.metric("AI delivery", "Local Ollama")

    st.markdown("## Customer intelligence")
    st.write(
        "Customer priority uses a transparent rule-based layer based on observed customer value, "
        "flight frequency, and recency. This is intentionally separate from the unsupervised K-Means "
        "segmentation model so the business prioritisation logic remains explainable."
    )

    st.markdown("## Machine-learning approach")
    st.write(
        "The CLV experiment compares Linear Regression, Random Forest and XGBoost. The saved best model is XGBoost. "
        "Its current R² is approximately 0.275, so the model is presented as an experimental portfolio baseline "
        "rather than a production-grade predictor."
    )

    st.markdown("## AI grounding")
    st.write(
        "The AI Assistant classifies the business question and supplies only the relevant calculated analytics "
        "section to the local LLM. Route questions use route commercial performance; fare questions use fare-class "
        "metrics; fleet questions use aircraft metrics; customer questions use value, frequency and recency; "
        "and trend questions use daily performance data."
    )

    st.markdown("## Data and modelling limitations")
    st.markdown(
        "- Revenue is not equivalent to profitability because operating costs are not available.\n"
        "- The CLV model has modest explanatory power (R² approximately 0.275).\n"
        "- K-Means segment names are business interpretations of unsupervised clusters.\n"
        "- Customer priority bands are transparent analytical rules, not predictive labels.\n"
        "- Local Ollama is optional and is not required for the analytical dashboards.\n"
        "- The SQLite database is excluded from GitHub because of repository file-size limits."
    )

    st.markdown("## Engineering principles")
    st.markdown(
        "- Reusable analytics and ML services are separated from the UI.\n"
        "- Relative project paths are used instead of machine-specific paths.\n"
        "- Joblib is used consistently for persisted machine-learning artefacts.\n"
        "- The AI layer is grounded in calculated analytics rather than unrestricted LLM knowledge.\n"
        "- Automated tests cover database, analytics, model and LLM-grounding services."
    )

    st.markdown("## Technology stack")
    st.write(
        "Python | SQL | SQLite | Pandas | Plotly | Streamlit | Scikit-learn | XGBoost | Ollama | Pytest | GitHub Actions"
    )
