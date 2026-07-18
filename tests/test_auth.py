"""
Tests for Supabase JWT authentication and per-club authorization.
"""
import shutil
import tempfile
import time

import jwt
import pytest

from akitoi import OrganizationManager
from akitoi.storage.org_json_storage import JSONOrgStorage
from akitoi.api.auth import create_user_dependency

JWT_SECRET = "test-supabase-jwt-secret"
SIGN_KEY = "test-membership-signing-key"

ADMIN_A = "user-aaa-111"   # admin of Club Andino
ADMIN_B = "user-bbb-222"   # admin of ANOTHER club

CSV = (
    "nombre,email,telefono,rol,estado,valid_until\n"
    "Ana Pérez,ana@example.com,,socio,vigente,2027-12-31\n"
)


def make_token(
    user_id: str,
    secret: str = JWT_SECRET,
    audience: str = "authenticated",
    expires_in: int = 3600,
    email: str = "admin@example.com",
) -> str:
    """Mint a Supabase-shaped access token."""
    now = int(time.time())
    return jwt.encode(
        {
            "sub": user_id,
            "aud": audience,
            "email": email,
            "role": "authenticated",
            "iat": now,
            "exp": now + expires_in,
        },
        secret,
        algorithm="HS256",
    )


def bearer(user_id: str, **kwargs) -> dict:
    return {"Authorization": f"Bearer {make_token(user_id, **kwargs)}"}


@pytest.fixture
def manager():
    temp_dir = tempfile.mkdtemp()
    yield OrganizationManager(JSONOrgStorage(temp_dir))
    shutil.rmtree(temp_dir)


@pytest.fixture
def client(manager):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from akitoi.api.routes.organizations import create_org_router
    from akitoi.api.routes.verify import create_verify_router

    app = FastAPI()
    app.include_router(
        create_org_router(
            manager,
            "https://akitoi.bio",
            secret_key=SIGN_KEY,
            user_dependency=create_user_dependency(jwt_secret=JWT_SECRET),
        ),
        prefix="/api/v1/orgs",
    )
    app.include_router(create_verify_router(manager.storage, secret_key=SIGN_KEY))
    return TestClient(app)


@pytest.fixture
def org(client):
    """Club Andino, created (and thus owned) by ADMIN_A."""
    return client.post(
        "/api/v1/orgs",
        json={"name": "Club Andino", "owner_profile_id": "prof-1"},
        headers=bearer(ADMIN_A),
    ).json()


class TestAuthentication:
    """Part A: JWT validation -> 401."""

    def test_no_token_is_401(self, client, org):
        endpoints = [
            ("get", f"/api/v1/orgs/{org['id']}/members"),
            ("post", f"/api/v1/orgs/{org['id']}/roster/import"),
            ("get", f"/api/v1/orgs/{org['id']}/roster/export"),
            ("get", f"/api/v1/orgs/{org['id']}/roster/imports"),
            ("post", "/api/v1/orgs"),
            ("get", "/api/v1/orgs"),
        ]
        for method, url in endpoints:
            response = getattr(client, method)(url)
            assert response.status_code in (401, 403), (method, url)
            # HTTPBearer returns 403 for missing creds only if auto_error;
            # ours is 401 — assert strictly:
            assert response.status_code == 401, (method, url)

    def test_garbage_token_is_401(self, client, org):
        response = client.get(
            f"/api/v1/orgs/{org['id']}/members",
            headers={"Authorization": "Bearer not-a-jwt"},
        )
        assert response.status_code == 401

    def test_wrong_secret_is_401(self, client, org):
        response = client.get(
            f"/api/v1/orgs/{org['id']}/members",
            headers=bearer(ADMIN_A, secret="attacker-secret"),
        )
        assert response.status_code == 401

    def test_expired_token_is_401(self, client, org):
        response = client.get(
            f"/api/v1/orgs/{org['id']}/members",
            headers=bearer(ADMIN_A, expires_in=-60),
        )
        assert response.status_code == 401
        assert "expirado" in response.json()["detail"].lower()

    def test_wrong_audience_is_401(self, client, org):
        response = client.get(
            f"/api/v1/orgs/{org['id']}/members",
            headers=bearer(ADMIN_A, audience="anon"),
        )
        assert response.status_code == 401


class TestAuthorization:
    """Part B: per-club authorization -> 403."""

    def test_creator_is_auto_linked_as_owner(self, client, manager, org):
        admins = manager.list_admins(org["id"])
        assert len(admins) == 1
        assert admins[0].user_id == ADMIN_A
        assert admins[0].role == "owner"

    def test_authorized_admin_gets_200(self, client, org):
        response = client.get(
            f"/api/v1/orgs/{org['id']}/members", headers=bearer(ADMIN_A)
        )
        assert response.status_code == 200

    def test_admin_of_another_club_gets_403(self, client, org):
        """ADMIN_B owns their own club but must not touch Club Andino."""
        client.post(
            "/api/v1/orgs",
            json={"name": "Otro Club", "owner_profile_id": "prof-2"},
            headers=bearer(ADMIN_B),
        )

        for method, url, kwargs in [
            ("get", f"/api/v1/orgs/{org['id']}/members", {}),
            ("post", f"/api/v1/orgs/{org['id']}/roster/import",
             {"files": {"file": ("p.csv", CSV.encode(), "text/csv")}}),
            ("get", f"/api/v1/orgs/{org['id']}/roster/export", {}),
            ("delete", f"/api/v1/orgs/{org['id']}/members/whatever", {}),
        ]:
            response = getattr(client, method)(
                url, headers=bearer(ADMIN_B), **kwargs
            )
            assert response.status_code == 403, (method, url)

    def test_multiple_admins_per_club(self, client, org):
        """An owner can link a second admin, who then operates normally."""
        response = client.post(
            f"/api/v1/orgs/{org['id']}/admins",
            json={"user_id": ADMIN_B},
            headers=bearer(ADMIN_A),
        )
        assert response.status_code == 201

        response = client.get(
            f"/api/v1/orgs/{org['id']}/members", headers=bearer(ADMIN_B)
        )
        assert response.status_code == 200

    def test_user_can_admin_multiple_clubs(self, client, manager, org):
        client.post(
            "/api/v1/orgs",
            json={"name": "Segundo Club", "owner_profile_id": "prof-1"},
            headers=bearer(ADMIN_A),
        )
        my_orgs = client.get("/api/v1/orgs", headers=bearer(ADMIN_A)).json()
        assert {o["name"] for o in my_orgs} == {"Club Andino", "Segundo Club"}

    def test_removed_admin_loses_access(self, client, org):
        client.post(
            f"/api/v1/orgs/{org['id']}/admins",
            json={"user_id": ADMIN_B},
            headers=bearer(ADMIN_A),
        )
        client.delete(
            f"/api/v1/orgs/{org['id']}/admins/{ADMIN_B}",
            headers=bearer(ADMIN_A),
        )
        response = client.get(
            f"/api/v1/orgs/{org['id']}/members", headers=bearer(ADMIN_B)
        )
        assert response.status_code == 403


class TestProtectedSurface:
    """Part C: full management flow works authenticated; public stays public."""

    def test_full_management_flow_authenticated(self, client, org):
        headers = bearer(ADMIN_A)
        org_id = org["id"]

        upload = client.post(
            f"/api/v1/orgs/{org_id}/roster/import",
            files={"file": ("padron.csv", CSV.encode(), "text/csv")},
            headers=headers,
        )
        assert upload.status_code == 200
        assert upload.json()["created"] == 1

        members = client.get(
            f"/api/v1/orgs/{org_id}/members", headers=headers
        ).json()
        card = client.get(
            f"/api/v1/orgs/{org_id}/members/{members[0]['id']}/card",
            headers=headers,
        )
        assert card.status_code == 200

        export = client.get(
            f"/api/v1/orgs/{org_id}/roster/export", headers=headers
        )
        assert export.status_code == 200

    def test_verify_stays_public(self, client, manager, org):
        """The door scans /verify with NO login."""
        headers = bearer(ADMIN_A)
        client.post(
            f"/api/v1/orgs/{org['id']}/roster/import",
            files={"file": ("padron.csv", CSV.encode(), "text/csv")},
            headers=headers,
        )
        members = client.get(
            f"/api/v1/orgs/{org['id']}/members", headers=headers
        ).json()
        card = client.get(
            f"/api/v1/orgs/{org['id']}/members/{members[0]['id']}/card",
            headers=headers,
        ).json()
        token = card["verify_url"].rsplit("/", 1)[-1]

        # NO Authorization header
        response = client.get(f"/verify/{token}?format=json")
        assert response.status_code == 200
        assert response.json()["status"] == "vigente"

    def test_roster_template_stays_public(self, client):
        response = client.get("/api/v1/orgs/roster-template")
        assert response.status_code == 200
