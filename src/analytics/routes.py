"""Route and airport commercial analytics."""
from pathlib import Path

import pandas as pd

from src.database import DEFAULT_DB_PATH, run_query


def get_route_performance(limit: int = 30, db_path: Path | str = DEFAULT_DB_PATH) -> pd.DataFrame:
    limit = max(1, min(int(limit), 500))
    return run_query(
        f"""
        WITH seat_counts AS (
            SELECT aircraft_code, COUNT(*) AS total_seats
            FROM seats
            GROUP BY aircraft_code
        ),
        flight_revenue AS (
            SELECT
                f.flight_id,
                f.departure_airport,
                f.arrival_airport,
                sc.total_seats,
                COUNT(DISTINCT tf.ticket_no) AS tickets_sold,
                COALESCE(SUM(tf.amount), 0) AS total_revenue
            FROM flights f
            JOIN seat_counts sc ON f.aircraft_code = sc.aircraft_code
            LEFT JOIN ticket_flights tf ON f.flight_id = tf.flight_id
            WHERE f.status IN ('Departed', 'Arrived')
            GROUP BY
                f.flight_id,
                f.departure_airport,
                f.arrival_airport,
                sc.total_seats
        ),
        flight_passengers AS (
            SELECT
                flight_id,
                COUNT(DISTINCT ticket_no) AS passengers_flown
            FROM boarding_passes
            GROUP BY flight_id
        )
        SELECT
            fr.departure_airport,
            fr.arrival_airport,
            json_extract(dep.city, '$.en') AS departure_city,
            json_extract(arr.city, '$.en') AS arrival_city,
            COUNT(*) AS number_of_flights,
            SUM(fr.tickets_sold) AS tickets_sold,
            SUM(COALESCE(fp.passengers_flown, 0)) AS passengers_flown,
            CAST(SUM(fr.total_revenue) AS INTEGER) AS total_revenue,
            ROUND(
                SUM(fr.total_revenue) / NULLIF(SUM(fr.tickets_sold), 0),
                2
            ) AS avg_ticket_price,
            SUM(fr.total_seats) AS total_available_seats,
            ROUND(
                SUM(COALESCE(fp.passengers_flown, 0)) * 100.0
                / NULLIF(SUM(fr.total_seats), 0),
                2
            ) AS load_factor_percent,
            ROUND(
                SUM(fr.total_revenue) / NULLIF(COUNT(*), 0),
                0
            ) AS revenue_per_flight
        FROM flight_revenue fr
        JOIN airports_data dep ON fr.departure_airport = dep.airport_code
        JOIN airports_data arr ON fr.arrival_airport = arr.airport_code
        LEFT JOIN flight_passengers fp ON fr.flight_id = fp.flight_id
        GROUP BY
            fr.departure_airport,
            fr.arrival_airport,
            dep.city,
            arr.city
        ORDER BY total_revenue DESC
        LIMIT {limit}
        """,
        db_path,
    )


def get_hub_performance(limit: int = 20, db_path: Path | str = DEFAULT_DB_PATH) -> pd.DataFrame:
    limit = max(1, min(int(limit), 500))
    return run_query(
        f"""
        SELECT
            ap.airport_code,
            json_extract(ap.city, '$.en') AS city,
            (
                SELECT COUNT(DISTINCT flight_id)
                FROM flights
                WHERE departure_airport = ap.airport_code
            ) AS outbound_flights,
            (
                SELECT COUNT(DISTINCT flight_id)
                FROM flights
                WHERE arrival_airport = ap.airport_code
            ) AS inbound_flights,
            (
                SELECT COUNT(DISTINCT flight_id)
                FROM flights
                WHERE departure_airport = ap.airport_code
            ) +
            (
                SELECT COUNT(DISTINCT flight_id)
                FROM flights
                WHERE arrival_airport = ap.airport_code
            ) AS total_flight_movements,
            CAST(
                (
                    SELECT SUM(tf.amount)
                    FROM ticket_flights tf
                    JOIN flights f ON tf.flight_id = f.flight_id
                    WHERE f.departure_airport = ap.airport_code
                       OR f.arrival_airport = ap.airport_code
                ) AS INTEGER
            ) AS total_revenue
        FROM airports_data ap
        WHERE ap.airport_code IN (SELECT departure_airport FROM flights)
           OR ap.airport_code IN (SELECT arrival_airport FROM flights)
        ORDER BY total_flight_movements DESC
        LIMIT {limit}
        """,
        db_path,
    )
