"""Executive KPI and temporal analytics."""
from pathlib import Path

import pandas as pd

from src.database import DEFAULT_DB_PATH, run_query


def get_executive_kpis(db_path: Path | str = DEFAULT_DB_PATH) -> dict:
    query = """
    SELECT
      (SELECT COUNT(*) FROM bookings) AS total_bookings,
      (SELECT COUNT(*) FROM flights WHERE status IN ('Departed', 'Arrived')) AS total_completed_flights,
      (SELECT COUNT(*) FROM flights) AS total_scheduled_flights,
      (SELECT COUNT(DISTINCT ticket_no) FROM tickets) AS total_tickets,
      (SELECT COUNT(DISTINCT passenger_id) FROM tickets) AS unique_customers,
      (SELECT ROUND(SUM(amount), 2) FROM ticket_flights) AS total_revenue,
      (SELECT ROUND(AVG(amount), 2) FROM ticket_flights) AS avg_ticket_value
    """
    result = run_query(query, db_path).iloc[0].to_dict()
    result["total_flights"] = result["total_completed_flights"]
    return result


def get_daily_trends(db_path: Path | str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """Return daily commercial and customer activity.

    The dashboard uses daily aggregation because the portfolio dataset covers a
    relatively short period. This preserves the available signal instead of
    compressing a small number of observations into weekly points.
    """
    trends = run_query(
        """
        SELECT
          date(SUBSTR(b.book_date, 1, 19)) AS booking_date,
          COUNT(DISTINCT b.book_ref) AS total_bookings,
          COUNT(DISTINCT tf.ticket_no) AS total_tickets,
          CAST(SUM(tf.amount) AS INTEGER) AS total_revenue,
          ROUND(AVG(tf.amount), 2) AS avg_ticket_price,
          COUNT(DISTINCT t.passenger_id) AS unique_customers
        FROM bookings b
        JOIN tickets t ON b.book_ref = t.book_ref
        JOIN ticket_flights tf ON t.ticket_no = tf.ticket_no
        GROUP BY booking_date
        ORDER BY booking_date
        """,
        db_path,
    )
    trends["booking_date"] = pd.to_datetime(trends["booking_date"])
    return trends


def get_monthly_trends(db_path: Path | str = DEFAULT_DB_PATH) -> pd.DataFrame:
    trends = run_query(
        """
        SELECT
          strftime('%Y-%m', SUBSTR(b.book_date, 1, 19)) AS booking_month,
          COUNT(DISTINCT b.book_ref) AS total_bookings,
          COUNT(DISTINCT tf.ticket_no) AS total_tickets,
          CAST(SUM(tf.amount) AS INTEGER) AS total_revenue,
          ROUND(AVG(tf.amount), 2) AS avg_ticket_price,
          COUNT(DISTINCT t.passenger_id) AS unique_customers
        FROM bookings b
        JOIN tickets t ON b.book_ref = t.book_ref
        JOIN ticket_flights tf ON t.ticket_no = tf.ticket_no
        GROUP BY booking_month
        ORDER BY booking_month
        """,
        db_path,
    )
    trends["booking_month"] = pd.to_datetime(trends["booking_month"], format="%Y-%m")
    return trends


def get_weekly_trends(db_path: Path | str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """Return weekly commercial and customer activity using Monday week starts."""
    trends = run_query(
        """
        SELECT
          date(SUBSTR(b.book_date, 1, 19), 'weekday 1', '-7 days') AS week_start,
          COUNT(DISTINCT b.book_ref) AS total_bookings,
          COUNT(DISTINCT tf.ticket_no) AS total_tickets,
          CAST(SUM(tf.amount) AS INTEGER) AS total_revenue,
          ROUND(AVG(tf.amount), 2) AS avg_ticket_price,
          COUNT(DISTINCT t.passenger_id) AS unique_customers
        FROM bookings b
        JOIN tickets t ON b.book_ref = t.book_ref
        JOIN ticket_flights tf ON t.ticket_no = tf.ticket_no
        GROUP BY week_start
        ORDER BY week_start
        """,
        db_path,
    )
    trends["week_start"] = pd.to_datetime(trends["week_start"])
    return trends
