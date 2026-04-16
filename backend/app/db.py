import os
from pathlib import Path
from typing import Generator

import duckdb
from fastapi import HTTPException

_DEFAULT_DB_PATH = str(Path(__file__).resolve().parents[1] / "data" / "invoice_ledger.duckdb")
DB_PATH = os.getenv("DUCKDB_PATH", _DEFAULT_DB_PATH)


def get_db() -> Generator[duckdb.DuckDBPyConnection, None, None]:
    """FastAPI dependency: yields a read-only DuckDB connection per request."""
    db_path = Path(DB_PATH).resolve()
    if not db_path.exists():
        raise HTTPException(
            status_code=503,
            detail="Database not initialised. Run `dbt seed && dbt run` inside backend/dbt/ first.",
        )
    # Keep this DuckDB connection read-only so the API cannot write to the analytics store.
    conn = duckdb.connect(str(db_path), read_only=True)
    try:
        yield conn
    finally:
        conn.close()
