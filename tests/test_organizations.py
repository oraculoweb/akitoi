"""
Tests for the organizational layer: Organization, Member, Membership
and their JSON storage backend.
"""
import shutil
import tempfile
from datetime import datetime, timedelta

import pytest

from akitoi.models.organization import Organization
from akitoi.models.member import Member
from akitoi.models.membership import Membership, MembershipStatus
from akitoi.models.theme import Theme
from akitoi.storage.org_json_storage import JSONOrgStorage


class TestOrganization:
    """Tests for Organization model."""

    def test_create_organization_basic(self):
        """Test creating a basic organization."""
        org = Organization(
            name="Club Andino",
            slug="club-andino",
            owner_profile_id="owner-123",
        )

        assert org.name == "Club Andino"
        assert org.slug == "club-andino"
        assert org.owner_profile_id == "owner-123"
        assert org.id is not None
        assert org.theme.primary_color == "#007bff"  # default Theme

    def test_organization_requires_name_slug_and_owner(self):
        """Test required field validation."""
        with pytest.raises(ValueError):
            Organization(name="", slug="test", owner_profile_id="o1")
        with pytest.raises(ValueError):
            Organization(name="Test", slug="", owner_profile_id="o1")
        with pytest.raises(ValueError):
            Organization(name="Test", slug="test", owner_profile_id="")

    def test_update_theme(self):
        """Test updating organization branding."""
        org = Organization(name="Test", slug="test", owner_profile_id="o1")
        org.update_theme(Theme(primary_color="#ff0000"))
        assert org.theme.primary_color == "#ff0000"

    def test_organization_dict_roundtrip(self):
        """Test to_dict/from_dict roundtrip."""
        org = Organization(
            name="Club Andino",
            slug="club-andino",
            owner_profile_id="owner-123",
            logo_url="https://example.com/logo.png",
            theme=Theme(primary_color="#ff0000"),
        )

        restored = Organization.from_dict(org.to_dict())

        assert restored.id == org.id
        assert restored.name == org.name
        assert restored.slug == org.slug
        assert restored.owner_profile_id == "owner-123"
        assert restored.logo_url == "https://example.com/logo.png"
        assert restored.theme.primary_color == "#ff0000"


class TestMember:
    """Tests for Member model."""

    def test_create_member_basic(self):
        """Test creating a member without a linked profile."""
        member = Member(
            organization_id="org-1",
            name="Ana Pérez",
            email="ana@example.com",
            role="socio",
        )

        assert member.organization_id == "org-1"
        assert member.name == "Ana Pérez"
        assert member.role == "socio"
        assert member.profile_id is None

    def test_member_with_linked_profile_needs_no_name(self):
        """A member linked to a Profile reuses it instead of duplicating."""
        member = Member(organization_id="org-1", profile_id="profile-9")
        assert member.profile_id == "profile-9"
        assert member.name == ""

    def test_member_without_profile_requires_name(self):
        """Test that unlinked members must carry a name."""
        with pytest.raises(ValueError, match="Name is required"):
            Member(organization_id="org-1")

    def test_member_requires_organization(self):
        """Test that organization_id is mandatory."""
        with pytest.raises(ValueError):
            Member(organization_id="", name="Ana")

    def test_link_profile(self):
        """Test linking an existing profile to a member."""
        member = Member(organization_id="org-1", name="Ana")
        member.link_profile("profile-9")
        assert member.profile_id == "profile-9"

    def test_member_dict_roundtrip(self):
        """Test to_dict/from_dict roundtrip."""
        member = Member(
            organization_id="org-1",
            name="Ana Pérez",
            email="ana@example.com",
            phone="+51911222333",
            role="directivo",
        )

        restored = Member.from_dict(member.to_dict())

        assert restored.id == member.id
        assert restored.role == "directivo"
        assert restored.phone == "+51911222333"


class TestMembership:
    """Tests for Membership model (validity core)."""

    def test_new_membership_is_vigente_and_active(self):
        """Test that a new membership starts active."""
        membership = Membership(member_id="m1", organization_id="org-1")

        assert membership.status == MembershipStatus.VIGENTE
        assert membership.is_active() is True

    def test_suspend_kills_validity_instantly(self):
        """Flipping status revokes validity immediately."""
        membership = Membership(
            member_id="m1",
            organization_id="org-1",
            valid_until=datetime.now() + timedelta(days=365),
        )
        assert membership.is_active() is True

        membership.suspend()

        assert membership.status == MembershipStatus.SUSPENDIDO
        assert membership.is_active() is False  # even with a future valid_until

    def test_expire_kills_validity_instantly(self):
        """Test manual expiration."""
        membership = Membership(member_id="m1", organization_id="org-1")
        membership.expire()
        assert membership.status == MembershipStatus.VENCIDO
        assert membership.is_active() is False

    def test_past_valid_until_makes_inactive(self):
        """A VIGENTE membership past its date is not active."""
        membership = Membership(
            member_id="m1",
            organization_id="org-1",
            valid_until=datetime.now() - timedelta(days=1),
        )
        assert membership.status == MembershipStatus.VIGENTE
        assert membership.is_active() is False

    def test_no_valid_until_means_no_expiration(self):
        """valid_until=None never expires by date."""
        membership = Membership(member_id="m1", organization_id="org-1")
        far_future = datetime.now() + timedelta(days=3650)
        assert membership.is_active(at=far_future) is True

    def test_reactivate_after_suspension(self):
        """Test reactivating a suspended membership."""
        membership = Membership(member_id="m1", organization_id="org-1")
        membership.suspend()
        membership.reactivate()
        assert membership.is_active() is True

    def test_renew_sets_new_expiration(self):
        """Test renewing an expired membership."""
        membership = Membership(
            member_id="m1",
            organization_id="org-1",
            valid_until=datetime.now() - timedelta(days=1),
        )
        membership.expire()

        new_date = datetime.now() + timedelta(days=365)
        membership.renew(new_date)

        assert membership.status == MembershipStatus.VIGENTE
        assert membership.valid_until == new_date
        assert membership.is_active() is True

    def test_check_expiration_flips_stale_membership(self):
        """check_expiration persists VENCIDO on stale VIGENTE records."""
        membership = Membership(
            member_id="m1",
            organization_id="org-1",
            valid_until=datetime.now() - timedelta(days=1),
        )

        assert membership.check_expiration() is True
        assert membership.status == MembershipStatus.VENCIDO
        # Second call is a no-op
        assert membership.check_expiration() is False

    def test_membership_requires_member_and_organization(self):
        """Test required field validation."""
        with pytest.raises(ValueError):
            Membership(member_id="", organization_id="org-1")
        with pytest.raises(ValueError):
            Membership(member_id="m1", organization_id="")

    def test_status_accepts_string_value(self):
        """Status can be given as its string value (e.g. from JSON)."""
        membership = Membership(
            member_id="m1", organization_id="org-1", status="suspendido"
        )
        assert membership.status == MembershipStatus.SUSPENDIDO

    def test_membership_dict_roundtrip(self):
        """Test to_dict/from_dict roundtrip including dates."""
        valid_until = datetime.now() + timedelta(days=30)
        membership = Membership(
            member_id="m1",
            organization_id="org-1",
            valid_until=valid_until,
        )
        membership.suspend()

        restored = Membership.from_dict(membership.to_dict())

        assert restored.id == membership.id
        assert restored.status == MembershipStatus.SUSPENDIDO
        assert restored.valid_until == valid_until


class TestJSONOrgStorage:
    """Tests for the JSON organizational storage backend."""

    @pytest.fixture
    def storage(self):
        temp_dir = tempfile.mkdtemp()
        yield JSONOrgStorage(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def org(self, storage):
        org = Organization(
            name="Club Andino", slug="club-andino", owner_profile_id="owner-1"
        )
        storage.save_organization(org)
        return org

    def test_organization_crud(self, storage, org):
        """Test organization save/get/delete cycle."""
        assert storage.get_organization(org.id).slug == "club-andino"
        assert storage.get_organization_by_slug("club-andino").id == org.id
        assert storage.org_slug_exists("club-andino") is True
        assert storage.org_slug_exists("otro") is False

        assert storage.delete_organization(org.id) is True
        assert storage.get_organization(org.id) is None
        assert storage.org_slug_exists("club-andino") is False

    def test_list_organizations(self, storage, org):
        """Test listing organizations."""
        storage.save_organization(
            Organization(name="Otro Club", slug="otro-club", owner_profile_id="o2")
        )
        slugs = {o.slug for o in storage.list_organizations()}
        assert slugs == {"club-andino", "otro-club"}

    def test_member_crud_scoped_to_organization(self, storage, org):
        """Members are listed per organization."""
        member = Member(organization_id=org.id, name="Ana")
        other = Member(organization_id="other-org", name="Luis")
        storage.save_member(member)
        storage.save_member(other)

        assert storage.get_member(member.id).name == "Ana"
        members = storage.list_members(org.id)
        assert [m.name for m in members] == ["Ana"]

        assert storage.delete_member(member.id) is True
        assert storage.get_member(member.id) is None
        assert storage.delete_member("nope") is False

    def test_membership_crud_and_lookup_by_member(self, storage, org):
        """Test membership persistence and member lookup."""
        member = Member(organization_id=org.id, name="Ana")
        storage.save_member(member)

        membership = Membership(member_id=member.id, organization_id=org.id)
        storage.save_membership(membership)

        assert storage.get_membership(membership.id).member_id == member.id
        assert storage.get_membership_by_member(member.id).id == membership.id
        assert len(storage.list_memberships(org.id)) == 1

        assert storage.delete_membership(membership.id) is True
        assert storage.get_membership_by_member(member.id) is None

    def test_status_change_persists(self, storage, org):
        """Instant revocation survives a save/load roundtrip."""
        member = Member(organization_id=org.id, name="Ana")
        storage.save_member(member)
        membership = Membership(member_id=member.id, organization_id=org.id)
        storage.save_membership(membership)

        # Revoke: flip status and persist
        membership.suspend()
        storage.save_membership(membership)

        reloaded = storage.get_membership_by_member(member.id)
        assert reloaded.status == MembershipStatus.SUSPENDIDO
        assert reloaded.is_active() is False
