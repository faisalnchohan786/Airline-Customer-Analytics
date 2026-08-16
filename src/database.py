"""SQLite access helpers for the Airline Analytics & AI project."""

from pathlib import Path
import sqlite3

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "travel.sqlite"


def get_connection(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Return a SQLite connection after validating the database path."""
    path = Path(db_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Airline database not found at {path}. "
            "Place travel.sqlite inside the project's data/ directory."
        )
    return sqlite3.connect(path)


def run_query(query: str, db_path: Path | str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """Execute a read query and return the result as a DataFrame."""
    with get_connection(db_path) as connection:
        return pd.read_sql_query(query, connection)
