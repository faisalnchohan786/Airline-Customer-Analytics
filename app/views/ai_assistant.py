"""Streamlit page for the grounded Airline Analytics AI Assistant."""
from __future__ import annotations

import re

import streamlit as st

from src.llm import OllamaUnavailableError, ask_airline_assistant, list_models
from src.llm.context_builder import context_metadata

SUGGESTED_QUESTIONS = [
    "Which routes generate the highest revenue, and what should management focus on?",
    "How does Business Class compare with Economy in revenue contribution?",
    "Which aircraft appear strongest commercially based on the available metrics?",
    "What do the latest daily trends suggest about airline performance?",
]


def _init_state() -> None:
    """Initialise persistent state used by the local AI chat page."""
    if "airline_chat_history" not in st.session_state:
        st.session_state.airline_chat_history = []


def _clean_model_markdown(text: str) -> str:
    """Normalise common malformed Markdown emitted by small local LLMs."""
    text = str(text).replace("\\r", "").replace("\\t", " ")
    text = text.replace("\\\\*", "*").replace("\\\\_", "_").replace("\\\\#", "#")
    # Convert Markdown asterisk bullets before removing stray emphasis markers.
    text = re.sub(r"(?m)^\\s*\\*\\s+", "- ", text)
    # The assistant is instructed to use headings and numbered lists; remove
    # remaining emphasis markers because malformed ** fragments look unprofessional.
    text = text.replace("**", "").replace("*", "")
    # Clean a few compact field names that can be produced by token-limited local models.
    replacements = {
        "totalbookings": "total bookings",
        "totaltickets": "total tickets",
        "averageticketprice": "average ticket price",
        "averageticketvalue": "average ticket value",
        "uniquecustomers": "unique customers",
    }
    for source, target in replacements.items():
        text = re.sub(rf"(?i)\\b{source}\\b", target, text)
    text = re.sub(r"[ \\t]{2,}", " ", text)
    text = re.sub(r"\\n{3,}", "\\n\\n", text)
    return text.strip()


def render() -> None:
    _init_state()

    st.title("Airline Analytics & AI Assistant")
    st.caption(
        "Ask management questions about routes, customers, revenue, fare classes, fleet and "
        "operational performance. Answers are grounded in calculated analytics from the local database."
    )

    left, right = st.columns([3, 1])

    with right:
        st.subheader("Local AI")
        try:
            models = list_models()
        except OllamaUnavailableError as exc:
            st.warning(str(exc))
            st.code("ollama serve")
            st.caption("Ollama is optional; start it only when using the AI Assistant.")
            return

        if not models:
            st.warning("Ollama is running, but no local models were detected.")
            st.code("ollama pull qwen3:8b")
            return

        preferred = next((m for m in models if "qwen" in m.lower()), models[0])
        selected_model = st.selectbox("Model", models, index=models.index(preferred))
        temperature = st.slider("Response creativity", 0.0, 0.8, 0.2, 0.1)

        if st.button("Clear conversation", width="stretch"):
            st.session_state.airline_chat_history = []
            st.rerun()

        st.divider()
        st.caption("Grounding")
        st.success("Targeted SQLite analytics context enabled")
        st.caption(
            "The assistant routes each question to the most relevant analytics domain and "
            "supplies only the corresponding calculated metrics."
        )

    with left:
        st.subheader("Suggested questions")
        cols = st.columns(2)
        selected_prompt = None
        for idx, question in enumerate(SUGGESTED_QUESTIONS):
            if cols[idx % 2].button(
                question,
                key=f"suggested_{idx}",
                width="stretch",
            ):
                selected_prompt = question

        st.divider()

        for message in st.session_state.airline_chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        typed_prompt = st.chat_input("Ask a business question about the airline dataset...")
        prompt = selected_prompt or typed_prompt
        if not prompt:
            return

        history_before_question = list(st.session_state.airline_chat_history)
        st.session_state.airline_chat_history.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                with st.spinner("Analysing airline performance..."):
                    answer = ask_airline_assistant(
                        question=prompt,
                        model=selected_model,
                        history=history_before_question,
                        temperature=temperature,
                    )
                # Local models can occasionally emit malformed emphasis markers.
                # Normalise them before rendering so the portfolio UI remains clean.
                answer = _clean_model_markdown(answer)
                st.markdown(answer)

                grounding = context_metadata(prompt)
                st.caption(
                    f"Grounding source: {grounding['source']} | Metrics: {grounding['metrics']}"
                )
            except OllamaUnavailableError as exc:
                answer = f"Local AI service unavailable: {exc}"
                st.error(answer)
            except Exception as exc:
                answer = "The assistant could not complete this question with the current local environment."
                st.error(answer)
                st.caption(str(exc))

        st.session_state.airline_chat_history.append({"role": "assistant", "content": answer})
