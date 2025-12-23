"""
Base storage interface for Akitoi platform.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..models.profile import Profile


class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def save_profile(self, profile: Profile) -> None:
        """
        Save a profile.

        Args:
            profile: Profile to save
        """
        pass

    @abstractmethod
    def get_profile(self, profile_id: str) -> Optional[Profile]:
        """
        Get a profile by ID.

        Args:
            profile_id: Profile ID

        Returns:
            Profile if found, None otherwise
        """
        pass

    @abstractmethod
    def get_profile_by_slug(self, slug: str) -> Optional[Profile]:
        """
        Get a profile by slug.

        Args:
            slug: Profile slug

        Returns:
            Profile if found, None otherwise
        """
        pass

    @abstractmethod
    def delete_profile(self, profile_id: str) -> bool:
        """
        Delete a profile.

        Args:
            profile_id: Profile ID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def list_profiles(self) -> List[Profile]:
        """
        List all profiles.

        Returns:
            List of profiles
        """
        pass

    @abstractmethod
    def slug_exists(self, slug: str) -> bool:
        """
        Check if a slug already exists.

        Args:
            slug: Slug to check

        Returns:
            True if exists, False otherwise
        """
        pass
