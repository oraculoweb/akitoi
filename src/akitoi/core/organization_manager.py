"""
Organization management core logic (clubs).

Mirrors ProfileManager: a thin, storage-agnostic facade over the
swappable OrgStorageBackend for organizations, members and
memberships, plus card issuance (signed token + dynamic QR).
"""
from datetime import datetime
from typing import Optional, List, Tuple

from ..models.organization import Organization
from ..models.organization_admin import OrganizationAdmin
from ..models.member import Member
from ..models.membership import Membership, MembershipStatus
from ..models.theme import Theme
from ..storage.org_base import OrgStorageBackend
from ..storage.org_json_storage import JSONOrgStorage
from ..utils.slug_generator import generate_slug, generate_unique_slug
from ..utils.validators import validate_slug, sanitize_slug
from .membership_tokens import membership_verify_url, membership_qr_svg


class OrganizationManager:
    """Manages organizations, members and memberships (CRUD + cards)."""

    def __init__(self, storage: Optional[OrgStorageBackend] = None):
        """
        Initialize organization manager.

        Args:
            storage: Organizational storage backend (defaults to JSON)
        """
        self.storage = storage or JSONOrgStorage()

    # --- Organizations ---

    def create_organization(
        self,
        name: str,
        owner_profile_id: str,
        slug: Optional[str] = None,
        logo_url: Optional[str] = None,
        theme: Optional[Theme] = None,
    ) -> Organization:
        """
        Create a new organization.

        Args:
            name: Club display name
            owner_profile_id: Profile id of the administrator
            slug: Custom slug (auto-generated if not provided)
            logo_url: URL to the club logo
            theme: Branding theme

        Raises:
            ValueError: If slug is invalid or already exists
        """
        if slug:
            slug = sanitize_slug(slug)
            if not validate_slug(slug):
                raise ValueError(f"Invalid slug: {slug}")
            if self.storage.org_slug_exists(slug):
                raise ValueError(f"Slug already exists: {slug}")
        else:
            base_slug = generate_slug(name)
            slug = generate_unique_slug(base_slug, self.storage.org_slug_exists)

        organization = Organization(
            name=name,
            slug=slug,
            owner_profile_id=owner_profile_id,
            logo_url=logo_url,
            theme=theme or Theme(),
        )
        self.storage.save_organization(organization)
        return organization

    def get_organization(self, organization_id: str) -> Optional[Organization]:
        """Get an organization by id."""
        return self.storage.get_organization(organization_id)

    def get_organization_by_slug(self, slug: str) -> Optional[Organization]:
        """Get an organization by slug."""
        return self.storage.get_organization_by_slug(slug)

    def list_organizations(self) -> List[Organization]:
        """List all organizations."""
        return self.storage.list_organizations()

    def delete_organization(self, organization_id: str) -> bool:
        """Delete an organization."""
        return self.storage.delete_organization(organization_id)

    # --- Admins (authorization: Supabase user_id <-> organization) ---

    def add_admin(
        self, organization_id: str, user_id: str, role: str = "admin"
    ) -> OrganizationAdmin:
        """
        Link a Supabase user as admin of an organization (idempotent).

        A club can have several admins and a user can administer
        several clubs.
        """
        for link in self.storage.list_org_admins(organization_id):
            if link.user_id == user_id:
                return link
        admin = OrganizationAdmin(
            organization_id=organization_id, user_id=user_id, role=role
        )
        self.storage.save_org_admin(admin)
        return admin

    def remove_admin(self, organization_id: str, user_id: str) -> bool:
        """Unlink an admin from an organization."""
        return self.storage.delete_org_admin(organization_id, user_id)

    def is_admin(self, user_id: str, organization_id: str) -> bool:
        """Check whether a user administers an organization."""
        return self.storage.is_org_admin(user_id, organization_id)

    def list_admins(self, organization_id: str) -> List[OrganizationAdmin]:
        """List the admins of an organization."""
        return self.storage.list_org_admins(organization_id)

    def list_organizations_for_admin(self, user_id: str) -> List[Organization]:
        """List the organizations a user administers."""
        organizations = []
        for link in self.storage.list_admin_links(user_id):
            organization = self.storage.get_organization(link.organization_id)
            if organization:
                organizations.append(organization)
        return organizations

    # --- Members (alta / baja) ---

    def add_member(
        self,
        organization_id: str,
        name: str = "",
        email: Optional[str] = None,
        phone: Optional[str] = None,
        role: str = "socio",
        profile_id: Optional[str] = None,
        status: MembershipStatus = MembershipStatus.VIGENTE,
        valid_until: Optional[datetime] = None,
    ) -> Tuple[Member, Membership]:
        """
        Register a member (alta) with their membership in one step.

        Returns:
            (member, membership) tuple
        """
        member = Member(
            organization_id=organization_id,
            name=name,
            email=email,
            phone=phone,
            role=role,
            profile_id=profile_id,
        )
        membership = Membership(
            member_id=member.id,
            organization_id=organization_id,
            status=status,
            valid_until=valid_until,
        )
        self.storage.save_member(member)
        self.storage.save_membership(membership)
        return member, membership

    def get_member(self, member_id: str) -> Optional[Member]:
        """Get a member by id."""
        return self.storage.get_member(member_id)

    def find_member_by_email(
        self, organization_id: str, email: str
    ) -> Optional[Member]:
        """Find a member of an organization by email (case-insensitive)."""
        needle = email.strip().lower()
        for member in self.storage.list_members(organization_id):
            if member.email and member.email.strip().lower() == needle:
                return member
        return None

    def list_members(
        self, organization_id: str, include_inactive: bool = False
    ) -> List[Member]:
        """
        List members of an organization.

        Args:
            organization_id: Organization id
            include_inactive: Include soft-deleted members (audit views)
        """
        members = self.storage.list_members(organization_id)
        if not include_inactive:
            members = [m for m in members if m.is_active]
        return sorted(members, key=lambda m: m.name.lower())

    def deactivate_member(self, member_id: str) -> Optional[Member]:
        """
        Baja lógica (soft delete): the member record persists for audit
        but leaves active views, and their membership is expired so the
        card becomes invalid instantly. No physical deletion.
        """
        member = self.storage.get_member(member_id)
        if not member:
            return None
        member.deactivate()
        self.storage.save_member(member)

        membership = self.storage.get_membership_by_member(member_id)
        if membership:
            membership.expire()
            self.storage.save_membership(membership)
        return member

    # --- Membership state ---

    def get_membership(self, member_id: str) -> Optional[Membership]:
        """Get the membership of a member."""
        return self.storage.get_membership_by_member(member_id)

    def suspend_member(self, member_id: str) -> Optional[Membership]:
        """Suspend a member's card (instant, reversible)."""
        return self._flip(member_id, "suspend")

    def reactivate_member(
        self, member_id: str, valid_until: Optional[datetime] = None
    ) -> Optional[Membership]:
        """Reactivate a suspended/expired card; restores soft-deleted members."""
        member = self.storage.get_member(member_id)
        if member and not member.is_active:
            member.restore()
            self.storage.save_member(member)
        membership = self.storage.get_membership_by_member(member_id)
        if not membership:
            return None
        membership.reactivate(valid_until)
        self.storage.save_membership(membership)
        return membership

    def expire_member(self, member_id: str) -> Optional[Membership]:
        """Mark a member's card as expired."""
        return self._flip(member_id, "expire")

    def _flip(self, member_id: str, action: str) -> Optional[Membership]:
        membership = self.storage.get_membership_by_member(member_id)
        if not membership:
            return None
        getattr(membership, action)()
        self.storage.save_membership(membership)
        return membership

    # --- Card issuance (token + dynamic QR) ---

    def issue_card(
        self,
        member_id: str,
        base_url: str,
        expires_in: Optional[int] = None,
        secret_key: Optional[str] = None,
    ) -> Optional[dict]:
        """
        Issue the digital card for a member: signed verification URL
        plus the dynamic QR (SVG) that encodes it.

        Args:
            member_id: Member to issue the card for
            base_url: Public base URL of the platform
            expires_in: Optional signature lifetime in seconds
            secret_key: Override signing key (tests)

        Returns:
            {"member_id", "verify_url", "qr_svg"} or None if not found
        """
        member = self.storage.get_member(member_id)
        membership = self.storage.get_membership_by_member(member_id)
        if not member or not membership:
            return None

        organization = self.storage.get_organization(member.organization_id)
        dark = organization.theme.primary_color if organization else "#000000"

        return {
            "member_id": member.id,
            "member_name": member.name,
            "verify_url": membership_verify_url(
                membership, base_url, expires_in, secret_key
            ),
            "qr_svg": membership_qr_svg(
                membership, base_url, dark, expires_in, secret_key
            ),
        }
