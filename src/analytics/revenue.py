"""Fare-class revenue analytics."""
from pathlib import Path

import pandas as pd

from src.database import DEFAULT_DB_PATH, run_query


def get_fare_class_performance(db_path: Path | str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """Return fare-condition performance.

    A ticket can contain multiple flight legs and therefore multiple fare conditions.
    For a reconciled mix, the volume share is calculated over ticket-flight records,
    not unique tickets. The UI labels this explicitly as Ticket-Flight Share.
    """
    return run_query(
        """
        WITH totals AS (
            SELECT
                COUNT(*) AS total_ticket_flight_legs,
                SUM(amount) AS total_revenue
            FROM ticket_flights
        )
        SELECT
            tf.fare_conditions AS seat_class,
            COUNT(*) AS ticket_flight_legs,
            COUNT(DISTINCT tf.ticket_no) AS unique_tickets,
            CAST(SUM(tf.amount) AS INTEGER) AS total_revenue,
            ROUND(AVG(tf.amount), 2) AS avg_ticket_price,
            CAST(MAX(tf.amount) AS INTEGER) AS max_ticket_price,
            CAST(MIN(tf.amount) AS INTEGER) AS min_ticket_price,
            COUNT(DISTINCT tf.flight_id) AS flights_covered,
            ROUND(
                COUNT(*) * 100.0 / NULLIF((SELECT total_ticket_flight_legs FROM totals), 0),
                2
            ) AS percent_of_ticket_flight_legs,
            ROUND(
                SUM(tf.amount) * 100.0 / NULLIF((SELECT total_revenue FROM totals), 0),
                2
            ) AS percent_of_total_revenue
        FROM ticket_flights tf
        GROUP BY tf.fare_conditions
        ORDER BY total_revenue DESC
        """,
        db_path,
    )
