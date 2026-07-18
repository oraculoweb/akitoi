"""
Base storage interface for the organizational layer (clubs).

Mirrors storage/base.py (StorageBackend for profiles) so the same
swap-in pattern applies: JSON for local dev/MVP, a database
implementation later. The database backend will be added together
with its Alembic migration; any implementation only needs to honor
this contract.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..models.organization import Organization
from ..models.organization_admin import OrganizationAdmin
from ..models.member import Member
from ..models.membership import Membership


class OrgStorageBackend(ABC):
    """Abstract base class for organizational storage backends."""

    # --- Organizations ---

    @abstractmethod
    def save_organization(self, organization: Organization) -> None:
        """Save an organization."""
        pass

    @abstractmethod
    def get_organization(self, organization_id: str) -> Optional[Organization]:
        """Get an organization by id."""
        pass

    @abstractmethod
    def get_organization_by_slug(self, slug: str) -> Optional[Organization]:
        """Get an organization by slug."""
        pass

    @abstractmethod
    def delete_organization(self, organization_id: str) -> bool:
        """Delete an organization. Returns True if deleted."""
        pass

    @abstractmethod
    def list_organizations(self) -> List[Organization]:
        """List all organizations."""
        pass

    @abstractmethod
    def org_slug_exists(self, slug: str) -> bool:
        """Check whether an organization slug already exists."""
        pass

    # --- Members ---

    @abstractmethod
    def save_member(self, member: Member) -> None:
        """Save a member."""
        pass

    @abstractmethod
    def get_member(self, member_id: str) -> Optional[Member]:
        """Get a member by id."""
        pass

    @abstractmethod
    def delete_member(self, member_id: str) -> bool:
        """Delete a member. Returns True if deleted."""
        pass

    @abstractmethod
    def list_members(self, organization_id: str) -> List[Member]:
        """List all members of an organization."""
        pass

    # --- Memberships ---

    @abstractmethod
    def save_membership(self, membership: Membership) -> None:
        """Save a membership."""
        pass

    @abstractmethod
    def get_membership(self, membership_id: str) -> Optional[Membership]:
        """Get a membership by id."""
        pass

    @abstractmethod
    def get_membership_by_member(self, member_id: str) -> Optional[Membership]:
        """Get the membership of a member (one active record per member)."""
        pass

    @abstractmethod
    def delete_membership(self, membership_id: str) -> bool:
        """Delete a membership. Returns True if deleted."""
        pass

    @abstractmethod
    def list_memberships(self, organization_id: str) -> List[Membership]:
        """List all memberships of an organization."""
        pass

    # --- Organization admins (authorization links) ---

    @abstractmethod
    def save_org_admin(self, admin: OrganizationAdmin) -> None:
        """Persist a user_id <-> organization_id management link."""
        pass

    @abstractmethod
    def delete_org_admin(self, organization_id: str, user_id: str) -> bool:
        """Remove a management link. Returns True if it existed."""
        pass

    @abstractmethod
    def list_org_admins(self, organization_id: str) -> List[OrganizationAdmin]:
        """List the admins of an organization."""
        pass

    @abstractmethod
    def list_admin_links(self, user_id: str) -> List[OrganizationAdmin]:
        """List every organization link of a user."""
        pass

    @abstractmethod
    def is_org_admin(self, user_id: str, organization_id: str) -> bool:
        """Check whether a user administers an organization."""
        pass

    # --- Import logs (roster audit trail) ---

    @abstractmethod
    def save_import_log(self, log: dict) -> None:
        """Persist one roster import record (see core/roster.ImportLog)."""
        pass

    @abstractmethod
    def list_import_logs(self, organization_id: str) -> List[dict]:
        """List roster import records of an organization, newest first."""
        pass
