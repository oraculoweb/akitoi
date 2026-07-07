"""
Member model: a person that belongs to an organization.
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import uuid


@dataclass
class Member:
    """
    A member (socio) of an organization.

    When the member already has an individual Akitoi Profile, link it
    via profile_id and treat that Profile as the source of truth for
    identity and contact data — the local name/email/phone fields are
    only for members WITHOUT a platform profile (or as a cached
    display fallback). Do not duplicate Profile data here.

    Attributes:
        id: Unique member identifier
        organization_id: Organization this member belongs to
        profile_id: Optional link to an existing individual Profile
        name: Display name (required when profile_id is not set)
        email: Contact email (optional; Profile wins when linked)
        phone: Contact phone (optional; Profile wins when linked)
        role: Role inside the club (e.g. "socio", "directivo", "staff")
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    organization_id: str
    name: str = ""
    profile_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str = "socio"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate member data."""
        if not self.organization_id:
            raise ValueError("Organization id is required")
        if not self.profile_id and not self.name:
            raise ValueError("Name is required when member has no linked profile")
        if not self.role:
            raise ValueError("Role is required")

    def link_profile(self, profile_id: str) -> None:
        """
        Link this member to an existing individual Profile.

        Args:
            profile_id: Id of the Profile to link
        """
        self.profile_id = profile_id
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert member to dictionary."""
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "profile_id": self.profile_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Member":
        """Create member from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            organization_id=data["organization_id"],
            profile_id=data.get("profile_id"),
            name=data.get("name", ""),
            email=data.get("email"),
            phone=data.get("phone"),
            role=data.get("role", "socio"),
            created_at=datetime.fromisoformat(data["created_at"])
                if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"])
                if "updated_at" in data else datetime.now(),
        )
