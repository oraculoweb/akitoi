"""
Tests for OrganizationManager and roster bulk import/export.
"""
import io
import shutil
import tempfile
from datetime import datetime, timedelta

import pytest

from akitoi import OrganizationManager
from akitoi.models.membership import MembershipStatus
from akitoi.storage.org_json_storage import JSONOrgStorage
from akitoi.core.roster import (
    ROSTER_TEMPLATE_CSV,
    export_roster_csv,
    export_roster_xlsx,
    import_roster,
    parse_roster_file,
)

TEST_KEY = "test-secret-key-not-for-production"

CSV_HEADER = "nombre,email,telefono,rol,estado,valid_until\n"


@pytest.fixture
def manager():
    temp_dir = tempfile.mkdtemp()
    yield OrganizationManager(JSONOrgStorage(temp_dir))
    shutil.rmtree(temp_dir)


@pytest.fixture
def org(manager):
    return manager.create_organization(
        name="Club Andino", owner_profile_id="owner-1"
    )


def _import_csv(manager, org, csv_text, filename="padron.csv"):
    rows = parse_roster_file(filename, csv_text.encode("utf-8"))
    return import_roster(manager.storage, org.id, rows, filename=filename)


class TestOrganizationManager:
    """Tests for the manager facade."""

    def test_create_organization_auto_slug(self, manager):
        org = manager.create_organization(
            name="Club Náutico del Sur", owner_profile_id="owner-1"
        )
        assert org.slug == "club-nutico-del-sur" or org.slug.startswith("club-n")
        assert manager.get_organization_by_slug(org.slug).id == org.id

    def test_duplicate_slug_rejected(self, manager, org):
        with pytest.raises(ValueError, match="already exists"):
            manager.create_organization(
                name="Otro", owner_profile_id="o2", slug=org.slug
            )

    def test_add_member_creates_membership(self, manager, org):
        member, membership = manager.add_member(
            org.id, name="Ana", email="ana@example.com"
        )
        assert membership.member_id == member.id
        assert membership.is_active() is True
        assert manager.get_membership(member.id).id == membership.id

    def test_suspend_and_reactivate(self, manager, org):
        member, _ = manager.add_member(org.id, name="Ana")

        assert manager.suspend_member(member.id).status == MembershipStatus.SUSPENDIDO
        assert manager.get_membership(member.id).is_active() is False

        assert manager.reactivate_member(member.id).status == MembershipStatus.VIGENTE
        assert manager.get_membership(member.id).is_active() is True

    def test_deactivate_member_is_soft_delete(self, manager, org):
        """Baja lógica: record persists, card dies, leaves active list."""
        member, _ = manager.add_member(org.id, name="Ana", email="ana@example.com")

        manager.deactivate_member(member.id)

        stored = manager.get_member(member.id)
        assert stored is not None  # NOT physically deleted
        assert stored.is_active is False
        assert stored.deactivated_at is not None
        assert manager.get_membership(member.id).is_active() is False
        assert manager.list_members(org.id) == []
        assert len(manager.list_members(org.id, include_inactive=True)) == 1

    def test_issue_card(self, manager, org):
        member, _ = manager.add_member(org.id, name="Ana")
        card = manager.issue_card(
            member.id, "https://akitoi.bio", secret_key=TEST_KEY
        )
        assert card["verify_url"].startswith("https://akitoi.bio/verify/")
        assert "<svg" in card["qr_svg"]
        assert member.id not in card["verify_url"]


class TestRosterImport:
    """Tests for bulk import (upsert by email)."""

    def test_import_new_roster(self, manager, org):
        log = _import_csv(manager, org, CSV_HEADER +
            "Ana Pérez,ana@example.com,+51911222333,socio,vigente,2027-12-31\n"
            "Luis Gómez,luis@example.com,,directivo,suspendido,\n"
            "Rosa Díaz,rosa@example.com,,socio,baja,\n")

        assert log.created == 2
        assert log.deactivated == 1
        assert log.error_count == 0

        members = manager.list_members(org.id)
        assert [m.name for m in members] == ["Ana Pérez", "Luis Gómez"]

        ana = manager.find_member_by_email(org.id, "ana@example.com")
        assert manager.get_membership(ana.id).is_active() is True
        luis = manager.find_member_by_email(org.id, "luis@example.com")
        assert manager.get_membership(luis.id).status == MembershipStatus.SUSPENDIDO

    def test_reimport_mass_revocation(self, manager, org):
        """Re-uploading with a state flipped suspends the card instantly."""
        _import_csv(manager, org, CSV_HEADER +
            "Ana Pérez,ana@example.com,,socio,vigente,2027-12-31\n")
        ana = manager.find_member_by_email(org.id, "ana@example.com")
        assert manager.get_membership(ana.id).is_active() is True

        log = _import_csv(manager, org, CSV_HEADER +
            "Ana Pérez,ana@example.com,,socio,suspendido,2027-12-31\n")

        assert log.updated == 1
        assert log.created == 0
        membership = manager.get_membership(ana.id)
        assert membership.status == MembershipStatus.SUSPENDIDO
        assert membership.is_active() is False
        # Still ONE member, not a duplicate
        assert len(manager.list_members(org.id)) == 1

    def test_invalid_rows_do_not_abort_import(self, manager, org):
        """Partial import: bad rows reported, good rows imported."""
        log = _import_csv(manager, org, CSV_HEADER +
            "Ana Pérez,ana@example.com,,socio,vigente,\n"
            ",sin-nombre@example.com,,socio,vigente,\n"          # no name
            "Mal Email,not-an-email,,socio,vigente,\n"           # bad email
            "Mal Estado,estado@example.com,,socio,activo,\n"     # bad estado
            "Mal Fecha,fecha@example.com,,socio,vigente,31-12\n" # bad date
            "Luis Gómez,luis@example.com,,socio,vigente,\n")

        assert log.created == 2  # Ana + Luis
        assert log.error_count == 4
        rows_with_errors = [e["row"] for e in log.errors]
        assert rows_with_errors == [3, 4, 5, 6]

    def test_baja_via_reimport_is_soft_delete(self, manager, org):
        """estado=baja in a reimport soft-deletes: audit record survives."""
        _import_csv(manager, org, CSV_HEADER +
            "Ana Pérez,ana@example.com,,socio,vigente,\n")
        ana = manager.find_member_by_email(org.id, "ana@example.com")

        log = _import_csv(manager, org, CSV_HEADER +
            "Ana Pérez,ana@example.com,,socio,baja,\n")

        assert log.deactivated == 1
        stored = manager.get_member(ana.id)
        assert stored is not None            # physical record persists
        assert stored.is_active is False
        assert manager.get_membership(ana.id).is_active() is False
        assert manager.list_members(org.id) == []

    def test_reimport_vigente_restores_baja(self, manager, org):
        """Re-alta: a baja member back to vigente in the file is restored."""
        _import_csv(manager, org, CSV_HEADER +
            "Ana Pérez,ana@example.com,,socio,baja,\n")
        log = _import_csv(manager, org, CSV_HEADER +
            "Ana Pérez,ana@example.com,,socio,vigente,2027-12-31\n")

        assert log.updated == 1
        ana = manager.find_member_by_email(org.id, "ana@example.com")
        assert ana.is_active is True
        assert manager.get_membership(ana.id).is_active() is True

    def test_import_log_is_persisted_and_queryable(self, manager, org):
        _import_csv(manager, org, CSV_HEADER +
            "Ana,ana@example.com,,socio,vigente,\n")
        _import_csv(manager, org, CSV_HEADER +
            "Ana,ana@example.com,,socio,suspendido,\n")

        logs = manager.storage.list_import_logs(org.id)
        assert len(logs) == 2
        assert logs[0]["updated"] == 1   # newest first
        assert logs[1]["created"] == 1
        assert "imported_at" in logs[0]

    def test_missing_columns_rejected(self, manager, org):
        with pytest.raises(ValueError, match="Columnas faltantes"):
            parse_roster_file("padron.csv", b"nombre,email\nAna,a@b.com\n")

    def test_template_parses_cleanly(self, manager, org):
        """The published template imports without errors."""
        log = _import_csv(manager, org, ROSTER_TEMPLATE_CSV)
        assert log.error_count == 0
        assert log.created == 2 and log.deactivated == 1

    def test_xlsx_roundtrip(self, manager, org):
        """XLSX import works through openpyxl."""
        from openpyxl import Workbook

        workbook = Workbook()
        sheet = workbook.active
        sheet.append(["nombre", "email", "telefono", "rol", "estado", "valid_until"])
        sheet.append(["Ana Pérez", "ana@example.com", "+519", "socio", "vigente",
                      datetime(2027, 12, 31)])
        buffer = io.BytesIO()
        workbook.save(buffer)

        rows = parse_roster_file("padron.xlsx", buffer.getvalue())
        log = import_roster(manager.storage, org.id, rows)

        assert log.created == 1
        ana = manager.find_member_by_email(org.id, "ana@example.com")
        assert manager.get_membership(ana.id).valid_until.year == 2027


class TestRosterExport:
    """Tests for the roster report."""

    def test_export_csv_reflects_current_state(self, manager, org):
        _import_csv(manager, org, CSV_HEADER +
            "Ana Pérez,ana@example.com,,socio,vigente,2027-12-31\n"
            "Luis Gómez,luis@example.com,,socio,vigente,\n")
        luis = manager.find_member_by_email(org.id, "luis@example.com")
        manager.suspend_member(luis.id)

        text = export_roster_csv(manager.storage, org.id).decode("utf-8-sig")

        assert "nombre,email,telefono,rol,estado,valid_until,actualizado" in text
        assert "Ana Pérez,ana@example.com,,socio,vigente,2027-12-31" in text
        assert "Luis Gómez,luis@example.com,,socio,suspendido" in text

    def test_export_includes_bajas_for_audit(self, manager, org):
        _import_csv(manager, org, CSV_HEADER +
            "Rosa Díaz,rosa@example.com,,socio,baja,\n")
        text = export_roster_csv(manager.storage, org.id).decode("utf-8-sig")
        assert "Rosa Díaz,rosa@example.com,,socio,baja" in text

    def test_export_xlsx(self, manager, org):
        _import_csv(manager, org, CSV_HEADER +
            "Ana,ana@example.com,,socio,vigente,\n")
        data = export_roster_xlsx(manager.storage, org.id)
        assert data[:4] == b"PK\x03\x04"  # xlsx is a zip container


class TestOrgAPI:
    """Tests for the club administration endpoints."""

    @pytest.fixture
    def client(self, manager):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from akitoi.api.routes.organizations import create_org_router
        from akitoi.api.routes.verify import create_verify_router

        app = FastAPI()
        app.include_router(
            create_org_router(manager, "https://akitoi.bio", secret_key=TEST_KEY),
            prefix="/api/v1/orgs",
        )
        app.include_router(create_verify_router(manager.storage, secret_key=TEST_KEY))
        return TestClient(app)

    @pytest.fixture
    def api_org(self, client):
        return client.post("/api/v1/orgs", json={
            "name": "Club Andino", "owner_profile_id": "owner-1",
        }).json()

    def test_full_cycle_upload_revoke_export(self, client, api_org):
        """Upload roster -> mass suspension by reimport -> export report."""
        org_id = api_org["id"]

        # 1) Upload initial roster
        upload = client.post(
            f"/api/v1/orgs/{org_id}/roster/import",
            files={"file": ("padron.csv", (CSV_HEADER +
                "Ana Pérez,ana@example.com,,socio,vigente,2027-12-31\n"
            ).encode(), "text/csv")},
        )
        assert upload.status_code == 200
        assert upload.json()["created"] == 1

        # 2) Card verifies as vigente
        members = client.get(f"/api/v1/orgs/{org_id}/members").json()
        card = client.get(
            f"/api/v1/orgs/{org_id}/members/{members[0]['id']}/card"
        ).json()
        token = card["verify_url"].rsplit("/", 1)[-1]
        assert client.get(f"/verify/{token}?format=json").json()["status"] == "vigente"

        # 3) Reimport with the member suspended -> same card now invalid
        client.post(
            f"/api/v1/orgs/{org_id}/roster/import",
            files={"file": ("padron.csv", (CSV_HEADER +
                "Ana Pérez,ana@example.com,,socio,suspendido,2027-12-31\n"
            ).encode(), "text/csv")},
        )
        verdict = client.get(f"/verify/{token}?format=json").json()
        assert verdict["valid"] is False
        assert verdict["status"] == "suspendido"

        # 4) Export reflects the new state
        export = client.get(f"/api/v1/orgs/{org_id}/roster/export")
        assert export.status_code == 200
        assert "suspendido" in export.text

        # 5) Import log recorded both uploads
        logs = client.get(f"/api/v1/orgs/{org_id}/roster/imports").json()
        assert len(logs) == 2

    def test_roster_template_download(self, client):
        response = client.get("/api/v1/orgs/roster-template")
        assert response.status_code == 200
        assert "nombre,email,telefono,rol,estado,valid_until" in response.text

    def test_soft_delete_endpoint(self, client, api_org):
        org_id = api_org["id"]
        member = client.post(f"/api/v1/orgs/{org_id}/members", json={
            "name": "Ana", "email": "ana@example.com",
        }).json()

        response = client.delete(f"/api/v1/orgs/{org_id}/members/{member['id']}")
        assert response.json() == {
            "member_id": member["id"], "estado": "baja", "deleted": False,
        }
        # Gone from active view, present in audit view
        assert client.get(f"/api/v1/orgs/{org_id}/members").json() == []
        audit = client.get(
            f"/api/v1/orgs/{org_id}/members?include_inactive=true"
        ).json()
        assert audit[0]["estado"] == "baja"

    def test_bad_file_format_rejected(self, client, api_org):
        response = client.post(
            f"/api/v1/orgs/{api_org['id']}/roster/import",
            files={"file": ("padron.txt", b"whatever", "text/plain")},
        )
        assert response.status_code == 400
