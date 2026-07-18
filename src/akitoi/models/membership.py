"""
Membership model: the validity state of a member in an organization.

This is the heart of the clubs MVP: whoever checks a membership
(a door scanner, a QR validation endpoint, a staff phone) asks ONE
question — "is it active right now?" — and the answer derives from
two server-side facts: status and valid_until. Flipping status is an
instant, centralized revocation: no card to reprint, no app update.
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class MembershipStatus(str, Enum):
    """Lifecycle states of a membership."""
    VIGENTE = "vigente"
    SUSPENDIDO = "suspendido"
    VENCIDO = "vencido"


@dataclass
class Membership:
    """
    Validity state of a Member inside an Organization.

    A membership is ACTIVE only when status is VIGENTE *and*
    valid_until (if set) has not passed. Any status change takes
    effect immediately for every future validity check.

    Attributes:
        id: Unique membership identifier
        member_id: Member this membership belongs to
        organization_id: Organization that issued the membership
        status: Current state (vigente | suspendido | vencido)
        valid_until: Expiration date (None = no expiration)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    member_id: str
    organization_id: str
    status: MembershipStatus = MembershipStatus.VIGENTE
    valid_until: Optional[datetime] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate membership data."""
        if not self.member_id:
            raise ValueError("Member id is required")
        if not self.organization_id:
            raise ValueError("Organization id is required")
        if isinstance(self.status, str):
            self.status = MembershipStatus(self.status)

    def is_active(self, at: Optional[datetime] = None) -> bool:
        """
        Single source of truth for validity checks.

        Args:
            at: Moment to evaluate (defaults to now)

        Returns:
            True only if status is VIGENTE and not expired
        """
        moment = at or datetime.now()
        if self.status != MembershipStatus.VIGENTE:
            return False
        if self.valid_until is not None and moment > self.valid_until:
            return False
        return True

    def suspend(self) -> None:
        """Suspend the membership (instant revocation, reversible)."""
        self.status = MembershipStatus.SUSPENDIDO
        self.updated_at = datetime.now()

    def expire(self) -> None:
        """Mark the membership as expired (instant revocation)."""
        self.status = MembershipStatus.VENCIDO
        self.updated_at = datetime.now()

    def reactivate(self, valid_until: Optional[datetime] = None) -> None:
        """
        Reactivate the membership, optionally with a new expiration.

        Args:
            valid_until: New expiration date (keeps current if None)
        """
        self.status = MembershipStatus.VIGENTE
        if valid_until is not None:
            self.valid_until = valid_until
        self.updated_at = datetime.now()

    def renew(self, valid_until: datetime) -> None:
        """
        Renew the membership with a new expiration date.

        Args:
            valid_until: New expiration date
        """
        self.status = MembershipStatus.VIGENTE
        self.valid_until = valid_until
        self.updated_at = datetime.now()

    def check_expiration(self, at: Optional[datetime] = None) -> bool:
        """
        Flip a stale VIGENTE membership to VENCIDO if past valid_until.

        Args:
            at: Moment to evaluate (defaults to now)

        Returns:
            True if the membership was expired by this call
        """
        moment = at or datetime.now()
        if (
            self.status == MembershipStatus.VIGENTE
            and self.valid_until is not None
            and moment > self.valid_until
        ):
            self.status = MembershipStatus.VENCIDO
            self.updated_at = datetime.now()
            return True
        return False

    def to_dict(self) -> dict:
        """Convert membership to dictionary."""
        return {
            "id": self.id,
            "member_id": self.member_id,
            "organization_id": self.organization_id,
            "status": self.status.value,
            "valid_until": self.valid_until.isoformat()
                if self.valid_until else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Membership":
        """Create membership from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            member_id=data["member_id"],
            organization_id=data["organization_id"],
            status=MembershipStatus(data.get("status", "vigente")),
            valid_until=datetime.fromisoformat(data["valid_until"])
                if data.get("valid_until") else None,
            created_at=datetime.fromisoformat(data["created_at"])
                if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"])
                if "updated_at" in data else datetime.now(),
        )
