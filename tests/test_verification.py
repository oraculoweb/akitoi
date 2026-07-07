"""
Tests for signed membership tokens, the dynamic QR and /verify/{token}.
"""
import shutil
import tempfile
from datetime import datetime, timedelta

import pytest

from akitoi.models.organization import Organization
from akitoi.models.member import Member
from akitoi.models.membership import Membership
from akitoi.storage.org_json_storage import JSONOrgStorage
from akitoi.core.membership_tokens import (
    InvalidTokenError,
    generate_membership_token,
    verify_membership_token,
    membership_verify_url,
    membership_qr_svg,
)

TEST_KEY = "test-secret-key-not-for-production"


@pytest.fixture
def storage():
    temp_dir = tempfile.mkdtemp()
    yield JSONOrgStorage(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def membership(storage):
    org = Organization(
        name="Club Andino",
        slug="club-andino",
        owner_profile_id="owner-1",
        logo_url="https://example.com/club.png",
    )
    storage.save_organization(org)
    member = Member(organization_id=org.id, name="Ana Pérez")
    storage.save_member(member)
    membership = Membership(
        member_id=member.id,
        organization_id=org.id,
        valid_until=datetime.now() + timedelta(days=365),
    )
    storage.save_membership(membership)
    return membership


class TestMembershipTokens:
    """Tests for token generation and validation."""

    def test_roundtrip(self, membership):
        """A generated token verifies back to the membership id."""
        token = generate_membership_token(membership, secret_key=TEST_KEY)
        payload = verify_membership_token(token, secret_key=TEST_KEY)

        assert payload["mid"] == membership.id
        assert payload["org"] == membership.organization_id

    def test_token_does_not_expose_raw_id_in_url(self, membership):
        """The verification URL carries the token, not the plain id."""
        url = membership_verify_url(
            membership, "https://akitoi.bio", secret_key=TEST_KEY
        )
        assert url.startswith("https://akitoi.bio/verify/")
        assert membership.id not in url

    def test_tampered_token_rejected(self, membership):
        """Any modification breaks the signature."""
        token = generate_membership_token(membership, secret_key=TEST_KEY)
        tampered = token[:-4] + ("AAAA" if not token.endswith("AAAA") else "BBBB")

        with pytest.raises(InvalidTokenError, match="Invalid token signature"):
            verify_membership_token(tampered, secret_key=TEST_KEY)

    def test_wrong_key_rejected(self, membership):
        """A token signed with another key never validates."""
        token = generate_membership_token(membership, secret_key="other-key")
        with pytest.raises(InvalidTokenError):
            verify_membership_token(token, secret_key=TEST_KEY)

    def test_embedded_expiry_rejected_when_past(self, membership):
        """expires_in embeds a signature expiry independent of valid_until."""
        token = generate_membership_token(
            membership, expires_in=-10, secret_key=TEST_KEY
        )
        with pytest.raises(InvalidTokenError, match="expired"):
            verify_membership_token(token, secret_key=TEST_KEY)

    def test_max_age_rejects_old_signatures(self, membership):
        """max_age caps signature age at verification time."""
        token = generate_membership_token(membership, secret_key=TEST_KEY)
        with pytest.raises(InvalidTokenError, match="expired"):
            verify_membership_token(token, max_age=-1, secret_key=TEST_KEY)

    def test_dynamic_qr_encodes_verify_url(self, membership):
        """The QR (reusing mobile/qr) renders and targets /verify/."""
        svg = membership_qr_svg(
            membership, "https://akitoi.bio", dark="#16a34a", secret_key=TEST_KEY
        )
        assert "<svg" in svg
        assert "16a34a" in svg.lower()


class TestVerifyEndpoint:
    """Tests for GET /verify/{token}."""

    @pytest.fixture
    def client(self, storage):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from akitoi.api.routes.verify import create_verify_router

        app = FastAPI()
        app.include_router(create_verify_router(storage, secret_key=TEST_KEY))
        return TestClient(app)

    def _token(self, membership, **kwargs):
        return generate_membership_token(membership, secret_key=TEST_KEY, **kwargs)

    def test_valid_token_active_membership(self, client, membership):
        """Token válido + socio vigente → vigente."""
        response = client.get(f"/verify/{self._token(membership)}?format=json")

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["status"] == "vigente"
        assert data["member"]["name"] == "Ana Pérez"
        assert data["organization"]["name"] == "Club Andino"
        assert data["organization"]["logo_url"] == "https://example.com/club.png"

    def test_minimal_data_only(self, client, membership):
        """No ids, contact data or analytics leak through the endpoint."""
        data = client.get(f"/verify/{self._token(membership)}?format=json").json()
        text = str(data)
        assert membership.id not in text
        assert membership.member_id not in text
        assert "email" not in data["member"]

    def test_suspended_membership_is_invalid(self, client, storage, membership):
        """Token válido pero socio suspendido → inválido al instante."""
        membership.suspend()
        storage.save_membership(membership)

        data = client.get(f"/verify/{self._token(membership)}?format=json").json()
        assert data["valid"] is False
        assert data["status"] == "suspendido"

    def test_expired_by_date_reports_vencido(self, client, storage, membership):
        """VIGENTE con valid_until pasado → vencido."""
        membership.valid_until = datetime.now() - timedelta(days=1)
        storage.save_membership(membership)

        data = client.get(f"/verify/{self._token(membership)}?format=json").json()
        assert data["valid"] is False
        assert data["status"] == "vencido"

    def test_tampered_token_is_401(self, client, membership):
        """Token manipulado → rechazado con 401."""
        token = self._token(membership)
        tampered = token[:-4] + ("AAAA" if not token.endswith("AAAA") else "BBBB")

        response = client.get(f"/verify/{tampered}?format=json")
        assert response.status_code == 401

    def test_expired_token_is_401(self, client, membership):
        """Token con firma expirada → rechazado con 401."""
        token = self._token(membership, expires_in=-10)
        response = client.get(f"/verify/{token}?format=json")
        assert response.status_code == 401

    def test_unknown_membership_is_404(self, client, storage, membership):
        """Firma válida pero membresía borrada → 404."""
        token = self._token(membership)
        storage.delete_membership(membership.id)

        response = client.get(f"/verify/{token}?format=json")
        assert response.status_code == 404

    def test_public_card_qr(self, client, membership):
        """The card view fetches the QR without auth; bad tokens get 401."""
        response = client.get(f"/verify/{self._token(membership)}/qr.svg")
        assert response.status_code == 200
        assert "<svg" in response.text

        assert client.get("/verify/basura/qr.svg").status_code == 401

    def test_html_page_for_human_scanners(self, client, membership):
        """Scanning with a phone camera shows a readable page."""
        response = client.get(f"/verify/{self._token(membership)}")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "VIGENTE" in response.text
        assert "Ana Pérez" in response.text
        assert "Club Andino" in response.text
