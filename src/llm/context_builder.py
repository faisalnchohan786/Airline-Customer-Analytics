"""Targeted analytics context construction for the Airline Analytics AI Assistant."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

from src.database import DEFAULT_DB_PATH
from src.analytics.customer import get_customer_features, get_top_customers, add_customer_priority
from src.analytics.fleet import get_aircraft_performance, get_flight_status
from src.analytics.overview import get_daily_trends, get_executive_kpis
from src.analytics.revenue import get_fare_class_performance
from src.analytics.routes import get_hub_performance, get_route_performance


INTENT_RULES = {
    "route": (
        "route", "routes", "airport", "airports", "origin", "destination",
        "hub", "network", "lane",
    ),
    "fare": (
        "fare", "fare class", "economy", "business class", "comfort", "ticket price",
        "ticket pricing", "yield", "ticket share", "revenue share",
    ),
    "fleet": (
        "aircraft", "fleet", "plane", "load factor", "available seat",
        "revenue per flight", "flight status", "cancelled", "delayed", "airframe",
    ),
    "customer": (
        "customer", "passenger", "clv", "lifetime value", "retention",
        "recency", "segment", "segmentation", "high-value", "vip", "at risk",
    ),
    "trend": (
        "trend", "trends", "daily", "weekly", "monthly", "month", "seasonal", "seasonality",
        "over time", "latest", "recent",
    ),
}


def classify_question(question: str) -> str:
    """Return the most relevant analytics domain."""
    text = question.lower()
    for intent, keywords in INTENT_RULES.items():
        if any(keyword in text for keyword in keywords):
            return intent
    return "executive"


def _records(df: pd.DataFrame, limit: int = 10) -> str:
    if df.empty:
        return "No records available."
    return df.head(limit).to_json(orient="records", date_format="iso")


@lru_cache(maxsize=8)
def _build_cached_context(db_path_str: str, intent: str) -> str:
    db_path = Path(db_path_str)
    kpis = get_executive_kpis(db_path)

    sections = [
        "AIRLINE ANALYTICS DATA CONTEXT",
        "All figures below are calculated from the local project database. "
        "Use these figures as the source of truth for dataset-specific claims.",
        "",
        "EXECUTIVE KPIs",
        str(kpis),
    ]

    if intent in {"route", "executive"}:
        routes = get_route_performance(limit=15, db_path=db_path)
        hubs = get_hub_performance(limit=10, db_path=db_path)
        sections.extend([
            "",
            "ROUTE COMMERCIAL PERFORMANCE",
            _records(routes, 15),
            "",
            "AIRPORT ACTIVITY",
            _records(hubs, 10),
        ])

    if intent in {"fare", "executive"}:
        fare = get_fare_class_performance(db_path)
        sections.extend([
            "",
            "FARE CLASS PERFORMANCE",
            _records(fare, 10),
            "",
            "Fare volume is measured as ticket-flight records because a single ticket can contain multiple flight legs.",
        ])

    if intent in {"fleet", "executive"}:
        fleet = get_aircraft_performance(db_path)
        status = get_flight_status(db_path)
        sections.extend([
            "",
            "AIRCRAFT PERFORMANCE",
            _records(fleet, 10),
            "",
            "FLIGHT STATUS",
            _records(status, 10),
        ])

    if intent in {"customer", "executive"}:
        features = add_customer_priority(get_customer_features(db_path))
        customers = get_top_customers(limit=10, db_path=db_path)
        customer_summary = {
            "customer_profiles": int(len(features)),
            "median_observed_customer_value": float(features["lifetime_value"].median()),
            "median_flight_frequency": float(features["flight_frequency"].median()),
            "median_recency_days": float(features["since_last_booking_days"].median()),
            "priority_counts": features["customer_priority"].value_counts().to_dict(),
        }
        sections.extend([
            "",
            "CUSTOMER VALUE AND PRIORITY SUMMARY",
            str(customer_summary),
            "",
            "TOP CUSTOMERS BY OBSERVED CUSTOMER VALUE",
            _records(customers, 10),
        ])

    if intent in {"trend", "executive"}:
        trends = get_daily_trends(db_path)
        latest_date = trends["booking_date"].max()
        sections.extend([
            "",
            "DAILY PERFORMANCE TRENDS",
            _records(trends.tail(16), 16),
            "",
            "DATA QUALITY NOTE",
            f"The latest available daily observation is {latest_date.strftime('%Y-%m-%d')}. "
            "It may represent a partial reporting period. Do not interpret it as a complete-day "
            "performance decline unless completeness is confirmed.",
        ])

    return "\n".join(sections).strip()


def build_analytics_context(
    db_path: Path | str = DEFAULT_DB_PATH,
    question: str = "",
) -> str:
    """Return targeted, cached analytics context for the question."""
    intent = classify_question(question)
    return _build_cached_context(str(Path(db_path).resolve()), intent)


def context_metadata(question: str) -> dict[str, str]:
    intent = classify_question(question)
    metadata = {
        "route": ("Route & Airport Analytics", "Revenue, flights, load factor and revenue per flight"),
        "fare": ("Revenue & Fare Class", "Revenue share, ticket-flight share and average fare"),
        "fleet": ("Fleet & Operations", "Load factor, revenue per flight, revenue per available seat and status"),
        "customer": ("Customer Intelligence", "Observed customer value, flight frequency, recency and priority"),
        "trend": ("Executive Overview", "Daily revenue, tickets, bookings and unique customers"),
        "executive": ("Executive Overview", "Headline revenue, bookings, flights, customers and commercial trends"),
    }
    source, metrics = metadata[intent]
    return {"intent": intent, "source": source, "metrics": metrics}
