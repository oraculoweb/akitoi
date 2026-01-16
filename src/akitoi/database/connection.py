"""
Database connection and session management for Supabase PostgreSQL.
"""
import os
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

# Get database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/akitoi"
)

# Fix for various PostgreSQL URL formats
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Supabase-specific connection settings
# Supabase uses connection pooling (PgBouncer) in transaction mode
# which requires some special handling

# Check if we're using Supabase
is_supabase = "supabase" in DATABASE_URL.lower()

# Engine configuration
engine_kwargs = {
    "pool_pre_ping": True,  # Verify connections before using them
    "pool_recycle": 300,     # Recycle connections after 5 minutes
    "echo": os.getenv("ENVIRONMENT") == "development",  # Log SQL in dev
}

# For Supabase, we need to handle connection pooling differently
if is_supabase:
    # Supabase uses PgBouncer in transaction mode
    # We should use NullPool to avoid connection pooling issues
    engine_kwargs["poolclass"] = NullPool
    engine_kwargs["connect_args"] = {
        "options": "-c timezone=utc"  # Set timezone to UTC
    }
else:
    # For local PostgreSQL, use standard pooling
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10

# Create engine
engine = create_engine(DATABASE_URL, **engine_kwargs)

# Enable prepared statements for Supabase
if is_supabase:
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        """Set connection parameters for Supabase."""
        connection_record.info["prepare_threshold"] = 0

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.

    Use this in FastAPI endpoints:
        from fastapi import Depends
        from sqlalchemy.orm import Session

        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Profile).all()

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database by creating all tables.

    This is useful for development and testing.
    In production, use Alembic migrations instead.

    Usage:
        from src.akitoi.database.connection import init_db
        init_db()
    """
    from . import models  # Import models to register them
    Base.metadata.create_all(bind=engine)
