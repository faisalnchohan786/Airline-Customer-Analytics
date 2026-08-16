"""Shared test configuration and a small deterministic airline fixture."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

FIXTURE_DB_PATH = ROOT / "tests" / "fixtures" / "test_airline.sqlite"
