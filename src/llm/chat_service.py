"""Grounded business-chat orchestration for the Airline Analytics AI Assistant."""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

from src.database import DEFAULT_DB_PATH
from src.llm.context_builder import build_analytics_context

from src.llm.ollama_client import chat

SYSTEM_INSTRUCTIONS = """You are the Airline Analytics AI Assistant for a portfolio decision-intelligence application.

Use ONLY the supplied calculated analytics context for factual claims about this airline dataset.

Rules:
- Never invent revenue, passenger, route, customer, aircraft, booking, ticket, or performance figures.
- Match the answer to the user's requested analytical domain. Do not substitute aircraft or customer metrics for a route question.
- If the context contains a section for the requested domain, use that section directly.
- For route questions, use ROUTE COMMERCIAL PERFORMANCE. Do not claim that route-level revenue is unavailable when that section contains route revenue.
- Do not infer profitability because the dataset does not contain operating costs. Use terms such as revenue, yield, load factor, occupancy, or commercial performance instead.
- Distinguish observed facts from management recommendations.
- Recommendations must be explicitly labelled and tied to metrics present in the context.
- Do not infer route distance, short-haul/long-haul classification, causality, customer intent, or operational causes unless the supplied context explicitly supports it.
- If the context cannot establish the requested answer, say so clearly rather than guessing.
- Keep the response concise and decision-oriented.
- Never treat revenue as profit. The dataset has no operating-cost measure.
- When evidence is insufficient for a recommendation, say what additional metric would be needed.
- Do not use bold or italic Markdown. Use plain text headings, short paragraphs, and numbered lists.
- Treat the latest available daily observation as potentially partial unless the context explicitly confirms it is a complete reporting day.

Preferred response structure:
### Answer
Direct answer with the most relevant figures.

### Management focus
Two or three evidence-based actions or considerations, only where appropriate.

### Evidence
Briefly state which analytics were used.
"""


def build_messages(
    question: str,
    history: Sequence[dict[str, str]] | None = None,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> list[dict[str, str]]:
    clean_question = question.strip()
    if not clean_question:
        raise ValueError("Question cannot be empty.")

    context = build_analytics_context(db_path=db_path, question=clean_question)
    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_INSTRUCTIONS},
        {"role": "system", "content": context},
    ]

    if history:
        for item in list(history)[-6:]:
            role = item.get("role")
            content = (item.get("content") or "").strip()
            if role in {"user", "assistant"} and content:
                messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": clean_question})
    return messages


def ask_airline_assistant(
    question: str,
    model: str,
    history: Sequence[dict[str, str]] | None = None,
    db_path: Path | str = DEFAULT_DB_PATH,
    temperature: float = 0.2,
) -> str:
    messages = build_messages(question, history=history, db_path=db_path)
    return chat(model=model, messages=messages, temperature=temperature)
