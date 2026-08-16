"""Reusable business analytics for the Airline Analytics & AI Platform."""
from .overview import get_executive_kpis, get_daily_trends, get_monthly_trends, get_weekly_trends
from .customer import get_top_customers, get_customer_features, add_customer_priority
from .routes import get_route_performance, get_hub_performance
from .revenue import get_fare_class_performance
from .fleet import get_aircraft_performance, get_flight_status

__all__ = [
    "get_executive_kpis", "get_daily_trends", "get_monthly_trends", "get_weekly_trends",
    "get_top_customers", "get_customer_features", "add_customer_priority",
    "get_route_performance", "get_hub_performance", "get_fare_class_performance",
    "get_aircraft_performance", "get_flight_status",
]
