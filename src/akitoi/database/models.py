"""
SQLAlchemy database models for Akitoi platform.

These models are optimized for Supabase PostgreSQL with proper indexes,
constraints, and relationship configurations.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text, JSON,
    ForeignKey, Index, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .connection import Base


class ProfileDB(Base):
    """
    Database model for user profiles.

    A profile represents a user's bio hub with contact information,
    social links, and customization options.

    Indexes:
        - slug (unique): For fast profile lookup by URL slug
        - is_published, created_at: For filtering published profiles
    """
    __tablename__ = "profiles"
    __table_args__ = (
        Index('idx_profiles_published_created', 'is_published', 'created_at'),
        Index('idx_profiles_view_count', 'view_count'),
        CheckConstraint('view_count >= 0', name='check_view_count_positive'),
    )

    # Primary key
    id = Column(String(36), primary_key=True, index=True)

    # Profile information
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, index=True, nullable=False)
    bio = Column(Text, default="")
    profile_image_url = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)

    # Theme customization (stored as JSONB in Supabase)
    theme = Column(JSON, nullable=False, default={
        "primary_color": "#007bff",
        "background_color": "#ffffff",
        "text_color": "#333333",
        "font_family": "Inter, sans-serif"
    })

    # Status
    is_published = Column(Boolean, default=False, nullable=False, index=True)

    # Analytics counters (denormalized for performance)
    view_count = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    links = relationship("LinkDB", back_populates="profile", cascade="all, delete-orphan")
    analytics_events = relationship("AnalyticsEventDB", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ProfileDB(id={self.id}, slug={self.slug}, name={self.name})>"


class LinkDB(Base):
    """
    Database model for profile links.

    Each link represents a contact method or social media profile
    associated with a user's bio hub.

    Indexes:
        - profile_id, order: For fast ordered link retrieval by profile
        - profile_id, type: For filtering links by type
    """
    __tablename__ = "links"
    __table_args__ = (
        Index('idx_links_profile_order', 'profile_id', 'order'),
        Index('idx_links_profile_type', 'profile_id', 'type'),
        CheckConstraint('click_count >= 0', name='check_click_count_positive'),
        CheckConstraint('order >= 0', name='check_order_positive'),
    )

    # Primary key
    id = Column(String(36), primary_key=True, index=True)

    # Foreign key
    profile_id = Column(
        String(36),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Link details
    type = Column(String(50), nullable=False)  # email, phone, whatsapp, linkedin, etc.
    url = Column(String(500), nullable=False)
    label = Column(String(100), nullable=True)
    icon = Column(String(100), nullable=True)

    # Display order
    order = Column(Integer, default=0, nullable=False)

    # Analytics counter (denormalized for performance)
    click_count = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    profile = relationship("ProfileDB", back_populates="links")

    def __repr__(self):
        return f"<LinkDB(id={self.id}, type={self.type}, profile_id={self.profile_id})>"


class AnalyticsEventDB(Base):
    """
    Database model for analytics events.

    This table stores individual events (views, clicks) for detailed analytics
    and time-series data. Events are immutable once created.

    Indexes:
        - profile_id, created_at: For time-series queries by profile
        - event_type, created_at: For filtering by event type over time
        - link_id: For link-specific analytics
    """
    __tablename__ = "analytics_events"
    __table_args__ = (
        Index('idx_analytics_profile_time', 'profile_id', 'created_at'),
        Index('idx_analytics_event_type_time', 'event_type', 'created_at'),
        Index('idx_analytics_link', 'link_id'),
    )

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    profile_id = Column(
        String(36),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    link_id = Column(
        String(36),
        ForeignKey("links.id", ondelete="SET NULL"),
        nullable=True
    )

    # Event details
    event_type = Column(String(50), nullable=False, index=True)  # view, click

    # Optional event metadata (stored as JSONB in Supabase)
    # Can include: referrer, user_agent, ip_hash, country, device_type, etc.
    event_metadata = Column(JSON, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    def __repr__(self):
        return f"<AnalyticsEventDB(id={self.id}, type={self.event_type}, profile_id={self.profile_id})>"
