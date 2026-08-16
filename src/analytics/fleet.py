"""Aircraft and operational performance analytics."""
from pathlib import Path
import pandas as pd
from src.database import DEFAULT_DB_PATH, run_query

def get_aircraft_performance(db_path: Path | str = DEFAULT_DB_PATH) -> pd.DataFrame:
    return run_query("""
    WITH seat_counts AS (SELECT aircraft_code,COUNT(*) seats_per_aircraft FROM seats GROUP BY aircraft_code),
    flight_revenue AS (SELECT f.flight_id,f.aircraft_code,COUNT(DISTINCT tf.ticket_no) tickets_sold,
      SUM(tf.amount) flight_revenue FROM flights f LEFT JOIN ticket_flights tf ON f.flight_id=tf.flight_id
      WHERE f.status IN ('Departed','Arrived') GROUP BY f.flight_id,f.aircraft_code),
    flight_passengers AS (SELECT f.flight_id,COUNT(DISTINCT bp.ticket_no) passengers_flown FROM flights f
      LEFT JOIN boarding_passes bp ON f.flight_id=bp.flight_id WHERE f.status IN ('Departed','Arrived') GROUP BY f.flight_id)
    SELECT a.aircraft_code,json_extract(a.model,'$.en') aircraft_model,a.range maximum_range_km,
      COUNT(DISTINCT fr.flight_id) total_flights,SUM(fr.tickets_sold) total_tickets_sold,
      SUM(COALESCE(fp.passengers_flown,0)) passengers_flown,CAST(SUM(fr.flight_revenue) AS INTEGER) total_revenue,
      ROUND(SUM(fr.flight_revenue)/NULLIF(SUM(fr.tickets_sold),0),2) average_ticket_price,sc.seats_per_aircraft,
      COUNT(DISTINCT fr.flight_id)*sc.seats_per_aircraft total_available_seats,
      ROUND(SUM(COALESCE(fp.passengers_flown,0))*100.0/NULLIF(COUNT(DISTINCT fr.flight_id)*sc.seats_per_aircraft,0),2) load_factor_percent,
      ROUND(SUM(fr.flight_revenue)/NULLIF(COUNT(DISTINCT fr.flight_id),0),2) revenue_per_flight,
      ROUND(SUM(fr.flight_revenue)/NULLIF(COUNT(DISTINCT fr.flight_id)*sc.seats_per_aircraft,0),2) revenue_per_available_seat
    FROM aircrafts_data a JOIN seat_counts sc ON a.aircraft_code=sc.aircraft_code
    JOIN flight_revenue fr ON a.aircraft_code=fr.aircraft_code LEFT JOIN flight_passengers fp ON fr.flight_id=fp.flight_id
    GROUP BY a.aircraft_code,a.model,a.range,sc.seats_per_aircraft ORDER BY total_revenue DESC
    """, db_path)

def get_flight_status(db_path: Path | str = DEFAULT_DB_PATH) -> pd.DataFrame:
    return run_query("""
    SELECT f.status,COUNT(DISTINCT f.flight_id) total_flights,COUNT(DISTINCT tf.ticket_no) tickets_sold,
      CAST(SUM(tf.amount) AS INTEGER) total_revenue,ROUND(AVG(tf.amount),2) avg_ticket_price,
      ROUND(COUNT(DISTINCT f.flight_id)*100.0/(SELECT COUNT(DISTINCT flight_id) FROM flights),2) percent_of_total_flights
    FROM flights f LEFT JOIN ticket_flights tf ON f.flight_id=tf.flight_id GROUP BY f.status ORDER BY total_flights DESC
    """, db_path)
