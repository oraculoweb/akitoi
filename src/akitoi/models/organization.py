"""
Organization model for clubs and organizations.
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import uuid

from .theme import Theme


@dataclass
class Organization:
    """
    A club or organization that groups members.

    The organization reuses the platform's Theme for branding and is
    administered by an owner, referenced by the id of an existing
    individual Profile.

    Attributes:
        id: Unique organization identifier
        slug: URL-friendly identifier for the organization
        name: Display name of the club/organization
        logo_url: URL to the organization logo
        theme: Visual branding configuration (reuses Theme)
        owner_profile_id: Profile id of the administrator
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    name: str
    slug: str
    owner_profile_id: str
    logo_url: Optional[str] = None
    theme: Theme = field(default_factory=Theme)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate organization data."""
        if not self.name:
            raise ValueError("Name is required")
        if not self.slug:
            raise ValueError("Slug is required")
        if not self.owner_profile_id:
            raise ValueError("Owner profile id is required")

    def update_theme(self, theme: Theme) -> None:
        """
        Update organization branding.

        Args:
            theme: New theme configuration
        """
        self.theme = theme
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert organization to dictionary."""
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "logo_url": self.logo_url,
            "theme": self.theme.to_dict(),
            "owner_profile_id": self.owner_profile_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Organization":
        """Create organization from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            slug=data["slug"],
            name=data["name"],
            logo_url=data.get("logo_url"),
            theme=Theme.from_dict(data.get("theme", {})),
            owner_profile_id=data["owner_profile_id"],
            created_at=datetime.fromisoformat(data["created_at"])
                if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"])
                if "updated_at" in data else datetime.now(),
        )
