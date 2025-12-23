"""
Profile management core logic for Akitoi platform.
"""
from typing import Optional, List

from ..models.profile import Profile
from ..models.link import Link
from ..models.theme import Theme
from ..storage.base import StorageBackend
from ..storage.json_storage import JSONStorage
from ..utils.slug_generator import generate_slug, generate_unique_slug
from ..utils.validators import validate_slug, sanitize_slug


class ProfileManager:
    """
    Manages profile operations (CRUD).

    This is the main interface for working with profiles.
    """

    def __init__(self, storage: Optional[StorageBackend] = None):
        """
        Initialize profile manager.

        Args:
            storage: Storage backend to use (defaults to JSONStorage)
        """
        self.storage = storage or JSONStorage()

    def create_profile(
        self,
        name: str,
        slug: Optional[str] = None,
        bio: str = "",
        profile_image_url: Optional[str] = None,
        logo_url: Optional[str] = None,
        theme: Optional[Theme] = None,
    ) -> Profile:
        """
        Create a new profile.

        Args:
            name: Display name
            slug: Custom slug (auto-generated if not provided)
            bio: Biography text
            profile_image_url: URL to profile image
            logo_url: URL to logo
            theme: Visual theme

        Returns:
            Created profile

        Raises:
            ValueError: If slug is invalid or already exists
        """
        # Generate or validate slug
        if slug:
            slug = sanitize_slug(slug)
            if not validate_slug(slug):
                raise ValueError(f"Invalid slug: {slug}")
            if self.storage.slug_exists(slug):
                raise ValueError(f"Slug already exists: {slug}")
        else:
            base_slug = generate_slug(name)
            slug = generate_unique_slug(base_slug, self.storage.slug_exists)

        # Create profile
        profile = Profile(
            name=name,
            slug=slug,
            bio=bio,
            profile_image_url=profile_image_url,
            logo_url=logo_url,
            theme=theme or Theme(),
        )

        # Save to storage
        self.storage.save_profile(profile)

        return profile

    def get_profile(self, profile_id: str) -> Optional[Profile]:
        """
        Get a profile by ID.

        Args:
            profile_id: Profile ID

        Returns:
            Profile if found, None otherwise
        """
        return self.storage.get_profile(profile_id)

    def get_profile_by_slug(self, slug: str) -> Optional[Profile]:
        """
        Get a profile by slug.

        Args:
            slug: Profile slug

        Returns:
            Profile if found, None otherwise
        """
        return self.storage.get_profile_by_slug(slug)

    def update_profile(
        self,
        profile_id: str,
        name: Optional[str] = None,
        bio: Optional[str] = None,
        profile_image_url: Optional[str] = None,
        logo_url: Optional[str] = None,
    ) -> Optional[Profile]:
        """
        Update profile information.

        Args:
            profile_id: Profile ID
            name: New name
            bio: New bio
            profile_image_url: New profile image URL
            logo_url: New logo URL

        Returns:
            Updated profile if found, None otherwise
        """
        profile = self.storage.get_profile(profile_id)
        if not profile:
            return None

        if name is not None:
            profile.name = name
        if bio is not None:
            profile.bio = bio
        if profile_image_url is not None:
            profile.profile_image_url = profile_image_url
        if logo_url is not None:
            profile.logo_url = logo_url

        self.storage.save_profile(profile)
        return profile

    def update_theme(
        self,
        profile_id: str,
        theme: Theme
    ) -> Optional[Profile]:
        """
        Update profile theme.

        Args:
            profile_id: Profile ID
            theme: New theme

        Returns:
            Updated profile if found, None otherwise
        """
        profile = self.storage.get_profile(profile_id)
        if not profile:
            return None

        profile.update_theme(theme)
        self.storage.save_profile(profile)
        return profile

    def delete_profile(self, profile_id: str) -> bool:
        """
        Delete a profile.

        Args:
            profile_id: Profile ID

        Returns:
            True if deleted, False if not found
        """
        return self.storage.delete_profile(profile_id)

    def list_profiles(self) -> List[Profile]:
        """
        List all profiles.

        Returns:
            List of profiles
        """
        return self.storage.list_profiles()

    def publish_profile(self, profile_id: str) -> Optional[Profile]:
        """
        Publish a profile (make it public).

        Args:
            profile_id: Profile ID

        Returns:
            Updated profile if found, None otherwise
        """
        profile = self.storage.get_profile(profile_id)
        if not profile:
            return None

        profile.publish()
        self.storage.save_profile(profile)
        return profile

    def unpublish_profile(self, profile_id: str) -> Optional[Profile]:
        """
        Unpublish a profile (make it private).

        Args:
            profile_id: Profile ID

        Returns:
            Updated profile if found, None otherwise
        """
        profile = self.storage.get_profile(profile_id)
        if not profile:
            return None

        profile.unpublish()
        self.storage.save_profile(profile)
        return profile

    def add_link(
        self,
        profile_id: str,
        link: Link
    ) -> Optional[Profile]:
        """
        Add a link to a profile.

        Args:
            profile_id: Profile ID
            link: Link to add

        Returns:
            Updated profile if found, None otherwise
        """
        profile = self.storage.get_profile(profile_id)
        if not profile:
            return None

        profile.add_link(link)
        self.storage.save_profile(profile)
        return profile

    def remove_link(
        self,
        profile_id: str,
        link_index: int
    ) -> Optional[Profile]:
        """
        Remove a link from a profile.

        Args:
            profile_id: Profile ID
            link_index: Index of link to remove

        Returns:
            Updated profile if found, None otherwise
        """
        profile = self.storage.get_profile(profile_id)
        if not profile:
            return None

        profile.remove_link(link_index)
        self.storage.save_profile(profile)
        return profile

    def record_view(self, slug: str) -> Optional[Profile]:
        """
        Record a profile view.

        Args:
            slug: Profile slug

        Returns:
            Updated profile if found, None otherwise
        """
        profile = self.storage.get_profile_by_slug(slug)
        if not profile:
            return None

        profile.increment_views()
        self.storage.save_profile(profile)
        return profile

    def record_link_click(
        self,
        slug: str,
        link_index: int
    ) -> Optional[Profile]:
        """
        Record a link click.

        Args:
            slug: Profile slug
            link_index: Index of clicked link

        Returns:
            Updated profile if found, None otherwise
        """
        profile = self.storage.get_profile_by_slug(slug)
        if not profile or link_index >= len(profile.links):
            return None

        profile.links[link_index].increment_clicks()
        self.storage.save_profile(profile)
        return profile
