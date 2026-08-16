"""Tests for analytics-grounded LLM services."""
import pytest

from tests.conftest import FIXTURE_DB_PATH
from src.llm.chat_service import build_messages
from src.llm.context_builder import build_analytics_context, classify_question


def test_route_question_is_routed_to_route_context():
    assert classify_question("Which routes generate the highest revenue?") == "route"


def test_daily_trend_question_is_routed_to_trend_context():
    assert classify_question("What do the latest daily trends suggest?") == "trend"


def test_messages_include_grounding_and_question():
    messages = build_messages(
        "Which routes perform best?",
        db_path=FIXTURE_DB_PATH,
    )
    assert messages[0]["role"] == "system"
    assert "Never invent" in messages[0]["content"]
    assert "ROUTE COMMERCIAL PERFORMANCE" in messages[1]["content"]
    assert messages[-1] == {
        "role": "user",
        "content": "Which routes perform best?",
    }


def test_context_contains_targeted_sections_for_route_question():
    context = build_analytics_context(
        FIXTURE_DB_PATH,
        question="Which routes generate the highest revenue?",
    )
    assert "ROUTE COMMERCIAL PERFORMANCE" in context
    assert "AIRPORT ACTIVITY" in context
    assert "FARE CLASS PERFORMANCE" not in context


def test_context_contains_daily_trends_for_trend_question():
    context = build_analytics_context(
        FIXTURE_DB_PATH,
        question="What do the latest daily trends suggest?",
    )
    assert "DAILY PERFORMANCE TRENDS" in context
