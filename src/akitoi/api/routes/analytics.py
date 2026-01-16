"""
Analytics endpoints for Akitoi platform.

These endpoints provide access to profile analytics data stored in Supabase.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...database import get_db
from ...database.utils import (
    get_profile_by_slug,
    get_profile_analytics,
    increment_profile_view_count,
    increment_link_click_count,
    create_analytics_event,
    get_trending_profiles
)

router = APIRouter()


# Pydantic schemas for API
class AnalyticsResponse(BaseModel):
    """Response schema for profile analytics."""
    total_views: int
    total_clicks: int
    views_by_day: list[dict]
    clicks_by_link: list[dict]


class TrendingProfileResponse(BaseModel):
    """Response schema for trending profiles."""
    id: str
    name: str
    slug: str
    bio: str
    view_count: int


class TrackEventRequest(BaseModel):
    """Request schema for tracking events."""
    event_type: str = Field(..., description="Type of event: 'view' or 'click'")
    link_id: Optional[str] = Field(None, description="Link ID for click events")
    metadata: Optional[dict] = Field(None, description="Additional event metadata")


@router.get("/{slug}/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    slug: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get analytics for a profile.

    Returns aggregated analytics data including:
    - Total views in the last N days
    - Total clicks in the last N days
    - Daily view breakdown
    - Clicks grouped by link type

    Args:
        slug: Profile slug
        days: Number of days to analyze (default: 30)
        db: Database session

    Returns:
        Analytics data

    Raises:
        404: Profile not found
    """
    # Get profile
    profile = get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with slug '{slug}' not found"
        )

    # Get analytics
    analytics = get_profile_analytics(db, profile.id, days=days)

    return AnalyticsResponse(**analytics)


@router.post("/{slug}/track")
async def track_event(
    slug: str,
    event: TrackEventRequest,
    db: Session = Depends(get_db)
):
    """
    Track an analytics event (view or click).

    This endpoint is used to record user interactions with profiles.

    Args:
        slug: Profile slug
        event: Event data (type, link_id, metadata)
        db: Database session

    Returns:
        Success message

    Raises:
        404: Profile not found
        400: Invalid event data
    """
    # Get profile
    profile = get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with slug '{slug}' not found"
        )

    # Validate event type
    if event.event_type not in ['view', 'click']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="event_type must be 'view' or 'click'"
        )

    # Create analytics event
    create_analytics_event(
        db=db,
        profile_id=profile.id,
        event_type=event.event_type,
        link_id=event.link_id,
        event_metadata=event.metadata
    )

    # Increment counters
    if event.event_type == 'view':
        increment_profile_view_count(db, profile.id)
    elif event.event_type == 'click' and event.link_id:
        increment_link_click_count(db, event.link_id)

    return {
        "success": True,
        "message": f"{event.event_type.capitalize()} event tracked successfully"
    }


@router.get("/trending", response_model=list[TrendingProfileResponse])
async def get_trending(
    days: int = 7,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get trending profiles based on recent activity.

    Returns profiles with the most views in the last N days.

    Args:
        days: Number of days to consider (default: 7)
        limit: Maximum number of profiles to return (default: 10)
        db: Database session

    Returns:
        List of trending profiles
    """
    trending_profiles = get_trending_profiles(db, days=days, limit=limit)

    return [
        TrendingProfileResponse(
            id=p.id,
            name=p.name,
            slug=p.slug,
            bio=p.bio or "",
            view_count=p.view_count
        )
        for p in trending_profiles
    ]
