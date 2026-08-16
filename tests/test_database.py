from pathlib import Path

import pytest

from src.database import get_connection


def test_missing_database_raises_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        get_connection(tmp_path / "missing.sqlite")
