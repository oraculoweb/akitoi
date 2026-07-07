"""
Public contact card derived from a Profile.

Privacy model: the card only ever exposes *basic* contact data and
public social/web URLs. Analytics, unpublished links, internal ids
and any inactive link never leave the server.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict

from ..models.profile import Profile
from ..models.link import LinkType

SUMMARY_MAX_LENGTH = 160

# Link types considered public social/web presence
_SOCIAL_TYPES = {
    LinkType.LINKEDIN,
    LinkType.TWITTER,
    LinkType.INSTAGRAM,
    LinkType.FACEBOOK,
    LinkType.GITHUB,
    LinkType.YOUTUBE,
    LinkType.TIKTOK,
}


@dataclass
class ContactCard:
    """
    Basic, shareable contact data for a person or company.

    This is the ONLY data structure the mobile layer exposes publicly.
    """

    name: str
    slug: str
    summary: str = ""
    photo_url: Optional[str] = None
    logo_url: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    profile_url: Optional[str] = None
    socials: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize the public card (no analytics, no internals)."""
        return {
            "name": self.name,
            "slug": self.slug,
            "summary": self.summary,
            "photo_url": self.photo_url,
            "logo_url": self.logo_url,
            "phone": self.phone,
            "email": self.email,
            "website": self.website,
            "profile_url": self.profile_url,
            "socials": self.socials,
        }


def _summarize(bio: str, max_length: int = SUMMARY_MAX_LENGTH) -> str:
    """Collapse a bio into a short one-line summary."""
    text = " ".join(bio.split())
    if len(text) <= max_length:
        return text
    return text[: max_length - 1].rstrip() + "…"


def build_contact_card(profile: Profile, base_url: str = "") -> ContactCard:
    """
    Derive the public contact card from a profile.

    Only active links are considered; the first WhatsApp link becomes
    the phone number, the first email link the email address, and the
    first website link the website. Social links are exposed by type.

    Args:
        profile: Source profile
        base_url: Platform base URL used to build the hub link

    Returns:
        ContactCard with basic public data only
    """
    phone = email = website = None
    socials: Dict[str, str] = {}

    for link in profile.get_active_links():
        if link.link_type == LinkType.WHATSAPP and phone is None:
            phone = link.url if link.url.startswith("+") else None
        elif link.link_type == LinkType.EMAIL and email is None:
            email = link.url.replace("mailto:", "", 1)
        elif link.link_type == LinkType.WEBSITE and website is None:
            website = link.url
        elif link.link_type in _SOCIAL_TYPES:
            socials.setdefault(link.link_type.value, link.url)

    profile_url = f"{base_url.rstrip('/')}/{profile.slug}" if base_url else None

    return ContactCard(
        name=profile.name,
        slug=profile.slug,
        summary=_summarize(profile.bio),
        photo_url=profile.profile_image_url,
        logo_url=profile.logo_url,
        phone=phone,
        email=email,
        website=website,
        profile_url=profile_url,
        socials=socials,
    )
