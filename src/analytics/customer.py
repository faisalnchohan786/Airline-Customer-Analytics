"""Customer value, engagement, recency and prioritisation analytics."""
from pathlib import Path

import pandas as pd

from src.database import DEFAULT_DB_PATH, run_query


def get_top_customers(limit: int = 20, db_path: Path | str = DEFAULT_DB_PATH) -> pd.DataFrame:
    limit = max(1, min(int(limit), 1000))
    return run_query(
        f"""
        WITH customer_cities AS (
            SELECT DISTINCT
                t.passenger_id,
                json_extract(ap.city, '$.en') AS city
            FROM tickets t
            JOIN ticket_flights tf ON t.ticket_no = tf.ticket_no
            JOIN flights f ON tf.flight_id = f.flight_id
            JOIN airports_data ap ON ap.airport_code = f.departure_airport

            UNION

            SELECT DISTINCT
                t.passenger_id,
                json_extract(ap.city, '$.en') AS city
            FROM tickets t
            JOIN ticket_flights tf ON t.ticket_no = tf.ticket_no
            JOIN flights f ON tf.flight_id = f.flight_id
            JOIN airports_data ap ON ap.airport_code = f.arrival_airport
        ),
        city_counts AS (
            SELECT passenger_id, COUNT(DISTINCT city) AS cities_visited
            FROM customer_cities
            GROUP BY passenger_id
        ),
        reference_date AS (
            SELECT MAX(SUBSTR(book_date, 1, 19)) AS max_book_date
            FROM bookings
        )
        SELECT
            t.passenger_id,
            COUNT(DISTINCT t.ticket_no) AS total_tickets_purchased,
            COUNT(DISTINCT tf.flight_id) AS total_flights_taken,
            COUNT(DISTINCT b.book_ref) AS total_bookings,
            CAST(SUM(tf.amount) AS INTEGER) AS total_revenue,
            CAST(SUM(tf.amount) AS INTEGER) AS observed_customer_value,
            COUNT(DISTINCT b.book_ref) AS booking_frequency,
            COUNT(DISTINCT tf.flight_id) AS flight_frequency,
            ROUND(AVG(tf.amount), 2) AS avg_ticket_price,
            CAST(MAX(tf.amount) AS INTEGER) AS max_ticket_price,
            COALESCE(cc.cities_visited, 0) AS cities_visited,
            CAST(
                julianday((SELECT max_book_date FROM reference_date))
                - julianday(SUBSTR(MAX(b.book_date), 1, 19))
                AS INTEGER
            ) AS since_last_booking_days,
            ROUND(
                CAST(SUM(tf.amount) AS FLOAT)
                / NULLIF(COUNT(DISTINCT tf.flight_id), 0),
                2
            ) AS revenue_per_flight
        FROM tickets t
        JOIN bookings b ON t.book_ref = b.book_ref
        JOIN ticket_flights tf ON t.ticket_no = tf.ticket_no
        JOIN flights f ON tf.flight_id = f.flight_id
        LEFT JOIN city_counts cc ON t.passenger_id = cc.passenger_id
        GROUP BY t.passenger_id, cc.cities_visited
        ORDER BY observed_customer_value DESC
        LIMIT {limit}
        """,
        db_path,
    )


def get_customer_features(db_path: Path | str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """Build customer-level features using consistent departure/arrival city coverage."""
    features = run_query(
        """
        WITH reference_date AS (
            SELECT MAX(SUBSTR(book_date, 1, 19)) AS max_book_date
            FROM bookings
        ),
        customer_cities AS (
            SELECT DISTINCT
                t.passenger_id,
                json_extract(ap.city, '$.en') AS city
            FROM tickets t
            JOIN ticket_flights tf ON t.ticket_no = tf.ticket_no
            JOIN flights f ON tf.flight_id = f.flight_id
            JOIN airports_data ap ON ap.airport_code = f.departure_airport

            UNION

            SELECT DISTINCT
                t.passenger_id,
                json_extract(ap.city, '$.en') AS city
            FROM tickets t
            JOIN ticket_flights tf ON t.ticket_no = tf.ticket_no
            JOIN flights f ON tf.flight_id = f.flight_id
            JOIN airports_data ap ON ap.airport_code = f.arrival_airport
        ),
        city_counts AS (
            SELECT passenger_id, COUNT(DISTINCT city) AS cities_visited
            FROM customer_cities
            GROUP BY passenger_id
        )
        SELECT
            t.passenger_id,
            COUNT(DISTINCT b.book_ref) AS booking_frequency,
            COUNT(DISTINCT tf.flight_id) AS flight_frequency,
            CAST(SUM(tf.amount) AS INTEGER) AS lifetime_value,
            CAST(SUM(tf.amount) AS INTEGER) AS observed_customer_value,
            ROUND(
                CAST(SUM(tf.amount) AS FLOAT)
                / NULLIF(COUNT(DISTINCT tf.flight_id), 0),
                2
            ) AS revenue_per_flight,
            ROUND(AVG(tf.amount), 2) AS avg_transaction_value,
            ROUND(MAX(tf.amount), 2) AS max_transaction_value,
            ROUND(MIN(tf.amount), 2) AS min_transaction_value,
            CAST(
                julianday(SUBSTR(MAX(b.book_date), 1, 19))
                - julianday(SUBSTR(MIN(b.book_date), 1, 19))
                AS INTEGER
            ) AS customer_lifespan_days,
            MAX(b.book_date) AS last_booking_date,
            CAST(
                julianday((SELECT max_book_date FROM reference_date))
                - julianday(SUBSTR(MAX(b.book_date), 1, 19))
                AS INTEGER
            ) AS since_last_booking_days,
            COUNT(
                DISTINCT CASE
                    WHEN tf.fare_conditions = 'Business' THEN tf.ticket_no
                END
            ) AS business_class_flights,
            COUNT(
                DISTINCT CASE
                    WHEN tf.fare_conditions = 'Economy' THEN tf.ticket_no
                END
            ) AS economy_class_flights,
            COUNT(
                DISTINCT CASE
                    WHEN tf.fare_conditions = 'Comfort' THEN tf.ticket_no
                END
            ) AS comfort_class_flights,
            COALESCE(cc.cities_visited, 0) AS cities_visited
        FROM tickets t
        JOIN bookings b ON t.book_ref = b.book_ref
        JOIN ticket_flights tf ON t.ticket_no = tf.ticket_no
        JOIN flights f ON tf.flight_id = f.flight_id
        LEFT JOIN city_counts cc ON t.passenger_id = cc.passenger_id
        GROUP BY t.passenger_id, cc.cities_visited
        HAVING COUNT(DISTINCT b.book_ref) > 0
        ORDER BY lifetime_value DESC
        """,
        db_path,
    )
    return features


def add_customer_priority(features: pd.DataFrame) -> pd.DataFrame:
    """Assign transparent value/engagement/recency priority bands.

    This is a rule-based decision layer, separate from the unsupervised K-Means model.
    """
    if features.empty:
        return features.copy()

    result = features.copy()
    value_cutoff = result["lifetime_value"].quantile(0.75)
    frequency_cutoff = result["flight_frequency"].median()
    recency_cutoff = result["since_last_booking_days"].quantile(0.75)

    high_value = result["lifetime_value"] >= value_cutoff
    frequent = result["flight_frequency"] >= frequency_cutoff
    recent = result["since_last_booking_days"] <= recency_cutoff

    result["customer_priority"] = "Dormant / Lower Priority"
    result.loc[recent & ~high_value, "customer_priority"] = "Active"
    result.loc[high_value & recent & ~frequent, "customer_priority"] = "Emerging High Value"
    result.loc[high_value & frequent & recent, "customer_priority"] = "VIP Active"
    result.loc[high_value & ~recent, "customer_priority"] = "VIP At Risk"

    result.attrs["value_cutoff"] = float(value_cutoff)
    result.attrs["frequency_cutoff"] = float(frequency_cutoff)
    result.attrs["recency_cutoff"] = float(recency_cutoff)
    return result
