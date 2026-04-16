import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Operational SQLite DB: write path for things the API owns (export logs, etc.)
# DuckDB is a separate, read-only analytics store managed entirely by dbt.
_DEFAULT_APP_DB = str(Path(__file__).resolve().parents[1] / "data" / "app.db")
APP_DB_URL = os.getenv("APP_DB_URL", f"sqlite:///{_DEFAULT_APP_DB}")

engine = create_engine(
    APP_DB_URL,
    connect_args={"check_same_thread": False},  # needed for SQLite + FastAPI threads
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_app_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yields a SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
