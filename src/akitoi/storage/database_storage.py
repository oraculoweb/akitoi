"""
Database storage backend for Akitoi platform using Supabase PostgreSQL.

This storage backend uses SQLAlchemy to interact with Supabase.
"""
from typing import Optional, List
from datetime import datetime

from .base import StorageBackend
from ..models.profile import Profile
from ..models.link import Link, LinkType
from ..models.theme import Theme
from ..database import SessionLocal, ProfileDB, LinkDB
from ..database.utils import get_profile_by_slug as db_get_profile_by_slug


class DatabaseStorage(StorageBackend):
    """
    Database storage implementation using Supabase PostgreSQL.

    This class bridges the domain models (Profile, Link, Theme) with
    the database models (ProfileDB, LinkDB) from SQLAlchemy.
    """

    def __init__(self):
        """Initialize database storage."""
        pass

    def _profile_db_to_domain(self, profile_db: ProfileDB) -> Profile:
        """
        Convert ProfileDB (SQLAlchemy) to Profile (domain model).

        Args:
            profile_db: Database profile model

        Returns:
            Domain Profile model
        """
        # Convert theme dict to Theme object
        theme_data = profile_db.theme or {}
        theme = Theme(
            primary_color=theme_data.get("primary_color", "#007bff"),
            background_color=theme_data.get("background_color", "#ffffff"),
            text_color=theme_data.get("text_color", "#333333"),
            font_family=theme_data.get("font_family", "Inter, sans-serif")
        )

        # Convert links
        links = []
        for link_db in sorted(profile_db.links, key=lambda x: x.order):
            # Convert string type to LinkType enum
            try:
                link_type_enum = LinkType(link_db.type)
            except ValueError:
                # If not a valid enum value, use CUSTOM
                link_type_enum = LinkType.CUSTOM

            link = Link(
                title=link_db.label or "",
                url=link_db.url,
                link_type=link_type_enum,
                icon=link_db.icon
            )
            # Preserve database ID and stats
            link._id = link_db.id
            link._click_count = link_db.click_count
            links.append(link)

        # Create Profile object with all attributes from database
        profile = Profile(
            id=profile_db.id,
            name=profile_db.name,
            slug=profile_db.slug,
            bio=profile_db.bio or "",
            profile_image_url=profile_db.profile_image_url,
            logo_url=profile_db.logo_url,
            theme=theme,
            links=links,
            is_published=profile_db.is_published,
            views=profile_db.view_count,
            created_at=profile_db.created_at,
            updated_at=profile_db.updated_at
        )

        return profile

    def _profile_domain_to_db(self, profile: Profile, profile_db: Optional[ProfileDB] = None) -> ProfileDB:
        """
        Convert Profile (domain model) to ProfileDB (SQLAlchemy).

        Args:
            profile: Domain profile model
            profile_db: Existing ProfileDB to update (optional)

        Returns:
            Database ProfileDB model
        """
        if profile_db is None:
            profile_db = ProfileDB(
                id=profile.id,
                name=profile.name,
                slug=profile.slug,
                created_at=datetime.utcnow(),
            )

        # Update fields
        profile_db.name = profile.name
        profile_db.slug = profile.slug
        profile_db.bio = profile.bio
        profile_db.profile_image_url = profile.profile_image_url
        profile_db.logo_url = profile.logo_url
        profile_db.is_published = profile.is_published
        profile_db.view_count = profile.views  # Profile uses 'views' not 'view_count'
        profile_db.updated_at = datetime.utcnow()

        # Convert theme
        profile_db.theme = {
            "primary_color": profile.theme.primary_color,
            "background_color": profile.theme.background_color,
            "text_color": profile.theme.text_color,
            "font_family": profile.theme.font_family
        }

        return profile_db

    def save_profile(self, profile: Profile) -> None:
        """
        Save a profile to Supabase.

        Args:
            profile: Profile to save
        """
        db = SessionLocal()
        try:
            # Check if profile exists
            existing = db.query(ProfileDB).filter(ProfileDB.id == profile.id).first()

            if existing:
                # Update existing profile
                profile_db = self._profile_domain_to_db(profile, existing)

                # Update links
                # Delete existing links
                db.query(LinkDB).filter(LinkDB.profile_id == profile.id).delete()

                # Add new links
                for order, link in enumerate(profile.links, start=1):
                    link_db = LinkDB(
                        id=getattr(link, '_id', None) or link.id,
                        profile_id=profile.id,
                        type=link.link_type.value if hasattr(link.link_type, 'value') else str(link.link_type),
                        url=link.url,
                        label=link.title,
                        icon=link.icon,
                        order=order,
                        click_count=getattr(link, '_click_count', 0),
                        created_at=datetime.utcnow()
                    )
                    db.add(link_db)
            else:
                # Create new profile
                profile_db = self._profile_domain_to_db(profile)
                db.add(profile_db)

                # Add links
                for order, link in enumerate(profile.links, start=1):
                    link_db = LinkDB(
                        id=link.id,
                        profile_id=profile.id,
                        type=link.link_type.value if hasattr(link.link_type, 'value') else str(link.link_type),
                        url=link.url,
                        label=link.title,
                        icon=link.icon,
                        order=order,
                        click_count=0,
                        created_at=datetime.utcnow()
                    )
                    db.add(link_db)

            db.commit()
        finally:
            db.close()

    def get_profile(self, profile_id: str) -> Optional[Profile]:
        """
        Get a profile by ID from Supabase.

        Args:
            profile_id: Profile ID

        Returns:
            Profile if found, None otherwise
        """
        db = SessionLocal()
        try:
            profile_db = db.query(ProfileDB).filter(ProfileDB.id == profile_id).first()
            if profile_db:
                return self._profile_db_to_domain(profile_db)
            return None
        finally:
            db.close()

    def get_profile_by_slug(self, slug: str) -> Optional[Profile]:
        """
        Get a profile by slug from Supabase.

        Args:
            slug: Profile slug

        Returns:
            Profile if found, None otherwise
        """
        db = SessionLocal()
        try:
            profile_db = db_get_profile_by_slug(db, slug)
            if profile_db:
                return self._profile_db_to_domain(profile_db)
            return None
        finally:
            db.close()

    def delete_profile(self, profile_id: str) -> bool:
        """
        Delete a profile from Supabase.

        Args:
            profile_id: Profile ID

        Returns:
            True if deleted, False if not found
        """
        db = SessionLocal()
        try:
            profile_db = db.query(ProfileDB).filter(ProfileDB.id == profile_id).first()
            if profile_db:
                db.delete(profile_db)
                db.commit()
                return True
            return False
        finally:
            db.close()

    def list_profiles(self) -> List[Profile]:
        """
        List all profiles from Supabase.

        Returns:
            List of profiles
        """
        db = SessionLocal()
        try:
            profiles_db = db.query(ProfileDB).order_by(ProfileDB.created_at.desc()).all()
            return [self._profile_db_to_domain(p) for p in profiles_db]
        finally:
            db.close()

    def slug_exists(self, slug: str) -> bool:
        """
        Check if a slug exists in Supabase.

        Args:
            slug: Slug to check

        Returns:
            True if exists, False otherwise
        """
        db = SessionLocal()
        try:
            exists = db.query(ProfileDB).filter(ProfileDB.slug == slug).first() is not None
            return exists
        finally:
            db.close()
