"""
Database utility functions for Supabase operations.

This module provides helper functions for common database operations,
query optimization, and Supabase-specific utilities.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from .models import ProfileDB, LinkDB, AnalyticsEventDB


def get_profile_by_slug(db: Session, slug: str) -> Optional[ProfileDB]:
    """
    Retrieve a profile by its unique slug.

    Args:
        db: Database session
        slug: Profile slug (URL-friendly identifier)

    Returns:
        ProfileDB instance if found, None otherwise
    """
    return db.query(ProfileDB).filter(ProfileDB.slug == slug).first()


def get_profile_by_id(db: Session, profile_id: str) -> Optional[ProfileDB]:
    """
    Retrieve a profile by its ID.

    Args:
        db: Database session
        profile_id: Profile UUID

    Returns:
        ProfileDB instance if found, None otherwise
    """
    return db.query(ProfileDB).filter(ProfileDB.id == profile_id).first()


def get_published_profiles(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[ProfileDB]:
    """
    Retrieve published profiles with pagination.

    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return

    Returns:
        List of published ProfileDB instances
    """
    return (
        db.query(ProfileDB)
        .filter(ProfileDB.is_published == True)
        .order_by(ProfileDB.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def increment_profile_view_count(db: Session, profile_id: str) -> bool:
    """
    Atomically increment the view count for a profile.

    This uses a database-level update to avoid race conditions.

    Args:
        db: Database session
        profile_id: Profile UUID

    Returns:
        True if successful, False otherwise
    """
    try:
        db.query(ProfileDB).filter(ProfileDB.id == profile_id).update(
            {ProfileDB.view_count: ProfileDB.view_count + 1},
            synchronize_session=False
        )
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def increment_link_click_count(db: Session, link_id: str) -> bool:
    """
    Atomically increment the click count for a link.

    This uses a database-level update to avoid race conditions.

    Args:
        db: Database session
        link_id: Link UUID

    Returns:
        True if successful, False otherwise
    """
    try:
        db.query(LinkDB).filter(LinkDB.id == link_id).update(
            {LinkDB.click_count: LinkDB.click_count + 1},
            synchronize_session=False
        )
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def get_profile_links(
    db: Session,
    profile_id: str,
    ordered: bool = True
) -> List[LinkDB]:
    """
    Retrieve all links for a profile.

    Args:
        db: Database session
        profile_id: Profile UUID
        ordered: Whether to order by the 'order' field

    Returns:
        List of LinkDB instances
    """
    query = db.query(LinkDB).filter(LinkDB.profile_id == profile_id)

    if ordered:
        query = query.order_by(LinkDB.order.asc())

    return query.all()


def create_analytics_event(
    db: Session,
    profile_id: str,
    event_type: str,
    link_id: Optional[str] = None,
    event_metadata: Optional[Dict[str, Any]] = None
) -> AnalyticsEventDB:
    """
    Create a new analytics event.

    Args:
        db: Database session
        profile_id: Profile UUID
        event_type: Type of event (e.g., 'view', 'click')
        link_id: Optional link UUID for click events
        event_metadata: Optional metadata dictionary (referrer, user_agent, etc.)

    Returns:
        Created AnalyticsEventDB instance
    """
    event = AnalyticsEventDB(
        profile_id=profile_id,
        event_type=event_type,
        link_id=link_id,
        event_metadata=event_metadata
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_profile_analytics(
    db: Session,
    profile_id: str,
    days: int = 30
) -> Dict[str, Any]:
    """
    Get analytics summary for a profile over the last N days.

    Args:
        db: Database session
        profile_id: Profile UUID
        days: Number of days to analyze (default: 30)

    Returns:
        Dictionary with analytics data including:
        - total_views: Total profile views
        - total_clicks: Total link clicks
        - views_by_day: List of daily view counts
        - clicks_by_link: Clicks grouped by link type
    """
    start_date = datetime.utcnow() - timedelta(days=days)

    # Get total views
    total_views = (
        db.query(func.count(AnalyticsEventDB.id))
        .filter(
            and_(
                AnalyticsEventDB.profile_id == profile_id,
                AnalyticsEventDB.event_type == 'view',
                AnalyticsEventDB.created_at >= start_date
            )
        )
        .scalar() or 0
    )

    # Get total clicks
    total_clicks = (
        db.query(func.count(AnalyticsEventDB.id))
        .filter(
            and_(
                AnalyticsEventDB.profile_id == profile_id,
                AnalyticsEventDB.event_type == 'click',
                AnalyticsEventDB.created_at >= start_date
            )
        )
        .scalar() or 0
    )

    # Get views by day
    views_by_day = (
        db.query(
            func.date_trunc('day', AnalyticsEventDB.created_at).label('day'),
            func.count(AnalyticsEventDB.id).label('count')
        )
        .filter(
            and_(
                AnalyticsEventDB.profile_id == profile_id,
                AnalyticsEventDB.event_type == 'view',
                AnalyticsEventDB.created_at >= start_date
            )
        )
        .group_by('day')
        .order_by('day')
        .all()
    )

    # Get clicks by link
    clicks_by_link = (
        db.query(
            LinkDB.type.label('link_type'),
            LinkDB.label.label('link_label'),
            func.count(AnalyticsEventDB.id).label('click_count')
        )
        .join(AnalyticsEventDB, LinkDB.id == AnalyticsEventDB.link_id)
        .filter(
            and_(
                AnalyticsEventDB.profile_id == profile_id,
                AnalyticsEventDB.event_type == 'click',
                AnalyticsEventDB.created_at >= start_date
            )
        )
        .group_by(LinkDB.type, LinkDB.label)
        .all()
    )

    return {
        'total_views': total_views,
        'total_clicks': total_clicks,
        'views_by_day': [
            {'date': str(day), 'count': count}
            for day, count in views_by_day
        ],
        'clicks_by_link': [
            {
                'type': link_type,
                'label': link_label,
                'count': click_count
            }
            for link_type, link_label, click_count in clicks_by_link
        ]
    }


def search_profiles(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 20
) -> List[ProfileDB]:
    """
    Search for profiles by name or slug.

    Args:
        db: Database session
        query: Search query string
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of matching ProfileDB instances
    """
    search_pattern = f"%{query}%"

    return (
        db.query(ProfileDB)
        .filter(
            and_(
                ProfileDB.is_published == True,
                or_(
                    ProfileDB.name.ilike(search_pattern),
                    ProfileDB.slug.ilike(search_pattern),
                    ProfileDB.bio.ilike(search_pattern)
                )
            )
        )
        .order_by(ProfileDB.view_count.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_trending_profiles(
    db: Session,
    days: int = 7,
    limit: int = 10
) -> List[ProfileDB]:
    """
    Get trending profiles based on recent view activity.

    Args:
        db: Database session
        days: Number of days to consider for trending calculation
        limit: Maximum number of profiles to return

    Returns:
        List of trending ProfileDB instances
    """
    start_date = datetime.utcnow() - timedelta(days=days)

    # Get profiles with most views in the last N days
    trending = (
        db.query(
            ProfileDB,
            func.count(AnalyticsEventDB.id).label('recent_views')
        )
        .join(AnalyticsEventDB, ProfileDB.id == AnalyticsEventDB.profile_id)
        .filter(
            and_(
                ProfileDB.is_published == True,
                AnalyticsEventDB.event_type == 'view',
                AnalyticsEventDB.created_at >= start_date
            )
        )
        .group_by(ProfileDB.id)
        .order_by(func.count(AnalyticsEventDB.id).desc())
        .limit(limit)
        .all()
    )

    return [profile for profile, _ in trending]


def cleanup_old_analytics(
    db: Session,
    days: int = 365
) -> int:
    """
    Delete analytics events older than specified days.

    This is useful for data retention policies and keeping
    the analytics table manageable.

    Args:
        db: Database session
        days: Number of days to keep (default: 365)

    Returns:
        Number of deleted records
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    deleted_count = (
        db.query(AnalyticsEventDB)
        .filter(AnalyticsEventDB.created_at < cutoff_date)
        .delete(synchronize_session=False)
    )

    db.commit()
    return deleted_count
