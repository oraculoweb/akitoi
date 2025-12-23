"""
Profile model for user bio hubs.
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
import uuid

from .link import Link
from .theme import Theme


@dataclass
class Profile:
    """
    User profile bio hub.

    Attributes:
        id: Unique profile identifier
        slug: URL-friendly identifier for the profile
        name: Display name (person or company)
        bio: Short biography or description
        profile_image_url: URL to profile picture
        logo_url: URL to company logo (optional)
        theme: Visual theme configuration
        links: List of contact links
        is_published: Whether the profile is public
        views: Total profile views
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    name: str
    slug: str
    bio: str = ""
    profile_image_url: Optional[str] = None
    logo_url: Optional[str] = None
    theme: Theme = field(default_factory=Theme)
    links: List[Link] = field(default_factory=list)
    is_published: bool = False
    views: int = 0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate profile data."""
        if not self.slug:
            raise ValueError("Slug is required")
        if not self.name:
            raise ValueError("Name is required")

    def add_link(self, link: Link) -> None:
        """
        Add a link to the profile.

        Args:
            link: Link to add
        """
        link.position = len(self.links)
        self.links.append(link)
        self.updated_at = datetime.now()

    def remove_link(self, link_index: int) -> None:
        """
        Remove a link by index.

        Args:
            link_index: Index of the link to remove
        """
        if 0 <= link_index < len(self.links):
            self.links.pop(link_index)
            self._reorder_links()
            self.updated_at = datetime.now()

    def reorder_links(self, new_order: List[int]) -> None:
        """
        Reorder links based on new position indices.

        Args:
            new_order: List of indices representing new order
        """
        if len(new_order) != len(self.links):
            raise ValueError("New order must contain all link indices")

        reordered = [self.links[i] for i in new_order]
        self.links = reordered
        self._reorder_links()
        self.updated_at = datetime.now()

    def _reorder_links(self) -> None:
        """Update position field for all links."""
        for i, link in enumerate(self.links):
            link.position = i

    def increment_views(self) -> None:
        """Increment profile view counter."""
        self.views += 1

    def get_active_links(self) -> List[Link]:
        """Get only active links sorted by position."""
        return sorted(
            [link for link in self.links if link.is_active],
            key=lambda x: x.position
        )

    def get_total_clicks(self) -> int:
        """Get total clicks across all links."""
        return sum(link.clicks for link in self.links)

    def update_theme(self, theme: Theme) -> None:
        """
        Update profile theme.

        Args:
            theme: New theme configuration
        """
        self.theme = theme
        self.updated_at = datetime.now()

    def publish(self) -> None:
        """Make profile public."""
        self.is_published = True
        self.updated_at = datetime.now()

    def unpublish(self) -> None:
        """Make profile private."""
        self.is_published = False
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert profile to dictionary."""
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "bio": self.bio,
            "profile_image_url": self.profile_image_url,
            "logo_url": self.logo_url,
            "theme": self.theme.to_dict(),
            "links": [link.to_dict() for link in self.links],
            "is_published": self.is_published,
            "views": self.views,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Profile":
        """Create profile from dictionary."""
        theme = Theme.from_dict(data.get("theme", {}))
        links = [Link.from_dict(link_data) for link_data in data.get("links", [])]

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            slug=data["slug"],
            name=data["name"],
            bio=data.get("bio", ""),
            profile_image_url=data.get("profile_image_url"),
            logo_url=data.get("logo_url"),
            theme=theme,
            links=links,
            is_published=data.get("is_published", False),
            views=data.get("views", 0),
            created_at=datetime.fromisoformat(data["created_at"])
                if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"])
                if "updated_at" in data else datetime.now(),
        )
