"""Database utilities: SQLAlchemy engine, session and Base declarative class."""

from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Pass ``check_same_thread=False`` when using SQLite; for other backends this
# option is ignored. Users can override the database URL via the ``DATABASE_URL``
# environment variable.
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False, future=True, connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator:  # pragma: no cover
    """Yield a database session that is closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
