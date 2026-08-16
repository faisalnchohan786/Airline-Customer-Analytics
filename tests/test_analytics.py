from tests.conftest import FIXTURE_DB_PATH
from src.analytics import (
    get_executive_kpis,
    get_daily_trends,
    get_monthly_trends,
    get_weekly_trends,
    get_fare_class_performance,
    get_route_performance,
    get_customer_features,
    add_customer_priority,
)

import pytest


def test_executive_kpis_have_expected_fields():
    kpis = get_executive_kpis(FIXTURE_DB_PATH)
    expected = {
        "total_bookings",
        "total_completed_flights",
        "total_tickets",
        "unique_customers",
        "total_revenue",
        "avg_ticket_value",
    }
    assert expected <= set(kpis)
    assert kpis["total_completed_flights"] > 0


def test_daily_trends_use_daily_dates():
    trends = get_daily_trends(FIXTURE_DB_PATH)
    assert not trends.empty
    assert str(trends["booking_date"].dtype).startswith("datetime64")
    assert trends["booking_date"].is_monotonic_increasing


def test_monthly_trends_use_month_start_dates():
    trends = get_monthly_trends(FIXTURE_DB_PATH)
    assert not trends.empty
    assert str(trends["booking_month"].dtype).startswith("datetime64")


def test_weekly_trends_use_week_start_dates():
    trends = get_weekly_trends(FIXTURE_DB_PATH)
    assert not trends.empty
    assert str(trends["week_start"].dtype).startswith("datetime64")
    assert trends["week_start"].dt.weekday.eq(0).all()


def test_fare_class_shares_reconcile():
    df = get_fare_class_performance(FIXTURE_DB_PATH)
    assert not df.empty
    assert {
        "seat_class",
        "total_revenue",
        "avg_ticket_price",
        "percent_of_ticket_flight_legs",
        "percent_of_total_revenue",
    } <= set(df.columns)
    assert df["percent_of_ticket_flight_legs"].sum() == pytest.approx(100, abs=0.2)
    assert df["percent_of_total_revenue"].sum() == pytest.approx(100, abs=0.2)


def test_route_performance_is_aggregated_at_route_level():
    df = get_route_performance(db_path=FIXTURE_DB_PATH)
    assert not df.empty
    assert {
        "departure_airport",
        "arrival_airport",
        "total_revenue",
        "load_factor_percent",
        "revenue_per_flight",
    } <= set(df.columns)


def test_customer_priority_is_transparent():
    features = get_customer_features(FIXTURE_DB_PATH)
    labelled = add_customer_priority(features)
    assert "customer_priority" in labelled.columns
    assert labelled["customer_priority"].notna().all()
    assert {"VIP Active", "VIP At Risk", "Emerging High Value", "Active", "Dormant / Lower Priority"} >= set(
        labelled["customer_priority"].unique()
    )
