"""
Akitoi - Professional Bio Hub Platform.

A web platform for creating personalized bio hubs with contact information,
customization, and analytics.
"""

from .models.profile import Profile
from .models.link import Link, LinkType
from .models.theme import Theme
from .models.organization import Organization
from .models.member import Member
from .models.membership import Membership, MembershipStatus
from .core.profile_manager import ProfileManager
from .core.organization_manager import OrganizationManager
from .core.url_shortener import URLShortener

__version__ = "0.1.0"
__author__ = "Akitoi Team"
__email__ = "team@akitoi.dev"

__all__ = [
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    # Models
    "Profile",
    "Link",
    "LinkType",
    "Theme",
    # Organizational layer (clubs)
    "Organization",
    "Member",
    "Membership",
    "MembershipStatus",
    # Core
    "ProfileManager",
    "OrganizationManager",
    "URLShortener",
    # Convenience functions
    "create_profile",
    "get_profile",
]


# Convenience functions using singleton ProfileManager
_default_manager = None


def _get_manager() -> ProfileManager:
    """Get or create default ProfileManager instance."""
    global _default_manager
    if _default_manager is None:
        _default_manager = ProfileManager()
    return _default_manager


def create_profile(
    name: str,
    slug: str = None,
    bio: str = "",
    **kwargs
) -> Profile:
    """
    Create a new profile.

    Args:
        name: Display name
        slug: Custom slug (auto-generated if not provided)
        bio: Biography text
        **kwargs: Additional profile options (profile_image_url, logo_url, theme)

    Returns:
        Created profile
    """
    return _get_manager().create_profile(name, slug, bio, **kwargs)


def get_profile(slug: str) -> Profile:
    """
    Get a profile by slug.

    Args:
        slug: Profile slug

    Returns:
        Profile if found, None otherwise
    """
    return _get_manager().get_profile_by_slug(slug)
