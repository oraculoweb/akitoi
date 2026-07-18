"""
OrganizationAdmin: links a Supabase Auth user to an organization.

Authorization model of the clubs MVP: a club can have several admins
and a user can administer several clubs (N:M). The user_id is the
Supabase Auth id (`sub` claim of the verified JWT) — identity itself
lives in Supabase, never duplicated here.
"""
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class OrganizationAdmin:
    """
    Management link between a Supabase user and an organization.

    Attributes:
        id: Unique link identifier
        organization_id: Organization being administered
        user_id: Supabase Auth user id (JWT `sub` claim)
        role: Admin role (e.g. "owner", "admin")
        created_at: When the link was created
    """

    organization_id: str
    user_id: str
    role: str = "admin"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate admin link data."""
        if not self.organization_id:
            raise ValueError("Organization id is required")
        if not self.user_id:
            raise ValueError("User id is required")

    def to_dict(self) -> dict:
        """Convert admin link to dictionary."""
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "user_id": self.user_id,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OrganizationAdmin":
        """Create admin link from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            organization_id=data["organization_id"],
            user_id=data["user_id"],
            role=data.get("role", "admin"),
            created_at=datetime.fromisoformat(data["created_at"])
                if "created_at" in data else datetime.now(),
        )
