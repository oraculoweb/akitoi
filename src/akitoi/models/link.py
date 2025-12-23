"""
Link model for profile contact links.
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum


class LinkType(str, Enum):
    """Types of links supported."""
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    WEBSITE = "website"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    GITHUB = "github"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    LLM_PROFILE = "llm_profile"
    AI_AGENT = "ai_agent"
    CUSTOM = "custom"


@dataclass
class Link:
    """
    Contact link in a profile.

    Attributes:
        title: Display title for the link
        url: URL or contact information
        link_type: Type of link (whatsapp, email, social, etc.)
        icon: Icon name or emoji
        is_active: Whether the link is visible
        position: Order position in the list
        clicks: Number of clicks on this link
        created_at: Creation timestamp
    """

    title: str
    url: str
    link_type: LinkType = LinkType.CUSTOM
    icon: Optional[str] = None
    is_active: bool = True
    position: int = 0
    clicks: int = 0
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Initialize link with defaults."""
        if self.icon is None:
            self.icon = self._get_default_icon()

    def _get_default_icon(self) -> str:
        """Get default icon based on link type."""
        icon_map = {
            LinkType.WHATSAPP: "💬",
            LinkType.EMAIL: "✉️",
            LinkType.WEBSITE: "🌐",
            LinkType.LINKEDIN: "💼",
            LinkType.TWITTER: "🐦",
            LinkType.INSTAGRAM: "📷",
            LinkType.FACEBOOK: "👥",
            LinkType.GITHUB: "💻",
            LinkType.YOUTUBE: "📺",
            LinkType.TIKTOK: "🎵",
            LinkType.LLM_PROFILE: "🤖",
            LinkType.AI_AGENT: "🧠",
            LinkType.CUSTOM: "🔗",
        }
        return icon_map.get(self.link_type, "🔗")

    def increment_clicks(self) -> None:
        """Increment click counter."""
        self.clicks += 1

    def to_dict(self) -> dict:
        """Convert link to dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "link_type": self.link_type.value,
            "icon": self.icon,
            "is_active": self.is_active,
            "position": self.position,
            "clicks": self.clicks,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Link":
        """Create link from dictionary."""
        return cls(
            title=data["title"],
            url=data["url"],
            link_type=LinkType(data.get("link_type", "custom")),
            icon=data.get("icon"),
            is_active=data.get("is_active", True),
            position=data.get("position", 0),
            clicks=data.get("clicks", 0),
            created_at=datetime.fromisoformat(data["created_at"])
                if "created_at" in data else datetime.now(),
        )
