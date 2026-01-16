"""
Database module for Akitoi platform.

This module provides database connection, models, and utilities
for working with Supabase PostgreSQL.

Usage:
    from src.akitoi.database import get_db, ProfileDB
    from src.akitoi.database.utils import get_profile_by_slug

    # In FastAPI endpoint
    @app.get("/profiles/{slug}")
    def get_profile(slug: str, db: Session = Depends(get_db)):
        profile = get_profile_by_slug(db, slug)
        return profile
"""
from .connection import engine, SessionLocal, Base, get_db, init_db
from .models import ProfileDB, LinkDB, AnalyticsEventDB

__all__ = [
    # Connection
    "engine",
    "SessionLocal",
    "Base",
    "get_db",
    "init_db",
    # Models
    "ProfileDB",
    "LinkDB",
    "AnalyticsEventDB",
]
