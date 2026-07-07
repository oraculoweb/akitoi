"""
Club administration endpoints: organizations, members, roster
bulk import/export and card issuance.

SECURITY MODEL
- Every management endpoint requires a valid Supabase JWT
  (Authorization: Bearer <token>) -> 401 otherwise.
- Authorization is per club via OrganizationAdmin links: a user only
  manages organizations they are linked to -> 403 otherwise. The
  creator of an organization is linked automatically as "owner".
- PUBLIC (no auth): GET /roster-template (static template) — and, in
  other routers, GET /verify/{token} (door scanning) plus the whole
  free tier / .vcf flow, which stay open by design.

The admin's natural workflow is file-first:
1. GET  /roster-template          -> download the CSV template
2. POST /{org_id}/roster/import   -> upload the filled roster (CSV/XLSX)
3. manage day to day (suspend/reactivate individual members, or just
   re-upload the file with states changed - mass revocation)
4. GET  /{org_id}/roster/export   -> download the up-to-date report
"""
from datetime import datetime
from typing import Callable, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import Response
from pydantic import BaseModel, Field

from ..auth import AuthUser, create_user_dependency
from ...core.organization_manager import OrganizationManager
from ...core.roster import (
    ROSTER_TEMPLATE_CSV,
    export_roster_csv,
    export_roster_xlsx,
    import_roster,
    member_estado,
    parse_roster_file,
)


class OrganizationCreate(BaseModel):
    """Schema for creating an organization."""

    name: str = Field(..., min_length=1, max_length=100)
    owner_profile_id: str = Field(..., min_length=1)
    slug: Optional[str] = Field(None, min_length=3, max_length=50)
    logo_url: Optional[str] = None


class MemberCreate(BaseModel):
    """Schema for registering a single member (alta individual)."""

    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str = "socio"
    valid_until: Optional[datetime] = None


class AdminLink(BaseModel):
    """Schema for linking another admin to a club."""

    user_id: str = Field(..., min_length=1)
    role: str = "admin"


def _member_response(manager: OrganizationManager, member) -> dict:
    membership = manager.get_membership(member.id)
    return {
        "id": member.id,
        "name": member.name,
        "email": member.email,
        "phone": member.phone,
        "role": member.role,
        "estado": member_estado(member, membership),
        "valid_until": membership.valid_until.isoformat()
            if membership and membership.valid_until else None,
        "is_active": member.is_active,
    }


def create_org_router(
    manager: OrganizationManager,
    base_url: str = "https://akitoi.bio",
    secret_key: Optional[str] = None,
    user_dependency: Optional[Callable] = None,
) -> APIRouter:
    """
    Build the club administration router.

    Args:
        manager: Organization manager (shared org storage)
        base_url: Public base URL for verification links
        secret_key: Override membership-token signing key (tests)
        user_dependency: Override the Supabase JWT dependency (tests);
            defaults to validating against SUPABASE_JWT_SECRET
    """
    router = APIRouter()
    current_user = user_dependency or create_user_dependency()

    def _get_org(organization_id: str):
        organization = manager.get_organization(organization_id)
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organización no encontrada: {organization_id}",
            )
        return organization

    async def require_admin(
        organization_id: str, user: AuthUser = Depends(current_user)
    ) -> AuthUser:
        """401 without a valid token; 403 for admins of OTHER clubs."""
        _get_org(organization_id)
        if not manager.is_admin(user.user_id, organization_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No administras esta organización",
            )
        return user

    # --- PUBLIC: roster template (must precede /{organization_id}) ---

    @router.get("/roster-template")
    async def roster_template():
        """Download the roster CSV template (public, static)."""
        return Response(
            ROSTER_TEMPLATE_CSV.encode("utf-8-sig"),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="padron-plantilla.csv"'
            },
        )

    # --- Organizations ---

    @router.post("", status_code=status.HTTP_201_CREATED)
    async def create_organization(
        data: OrganizationCreate, user: AuthUser = Depends(current_user)
    ):
        """Create a club; the authenticated creator becomes its owner."""
        try:
            organization = manager.create_organization(
                name=data.name,
                owner_profile_id=data.owner_profile_id,
                slug=data.slug,
                logo_url=data.logo_url,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            )
        manager.add_admin(organization.id, user.user_id, role="owner")
        return organization.to_dict()

    @router.get("")
    async def list_my_organizations(user: AuthUser = Depends(current_user)):
        """List the clubs the authenticated user administers."""
        return [
            org.to_dict()
            for org in manager.list_organizations_for_admin(user.user_id)
        ]

    @router.get("/{organization_id}")
    async def get_organization(
        organization_id: str, user: AuthUser = Depends(require_admin)
    ):
        """Get a club (admins only)."""
        return _get_org(organization_id).to_dict()

    # --- Admins (varios admins por club) ---

    @router.get("/{organization_id}/admins")
    async def list_admins(
        organization_id: str, user: AuthUser = Depends(require_admin)
    ):
        """List the admins of a club."""
        return [a.to_dict() for a in manager.list_admins(organization_id)]

    @router.post(
        "/{organization_id}/admins", status_code=status.HTTP_201_CREATED
    )
    async def add_admin(
        organization_id: str,
        data: AdminLink,
        user: AuthUser = Depends(require_admin),
    ):
        """Link another Supabase user as admin of this club."""
        return manager.add_admin(
            organization_id, data.user_id, role=data.role
        ).to_dict()

    @router.delete("/{organization_id}/admins/{user_id}")
    async def remove_admin(
        organization_id: str,
        user_id: str,
        user: AuthUser = Depends(require_admin),
    ):
        """Unlink an admin from this club."""
        if not manager.remove_admin(organization_id, user_id):
            raise HTTPException(status_code=404, detail="Admin no encontrado")
        return {"organization_id": organization_id, "user_id": user_id,
                "removed": True}

    # --- Members ---

    @router.get("/{organization_id}/members")
    async def list_members(
        organization_id: str,
        include_inactive: bool = False,
        user: AuthUser = Depends(require_admin),
    ):
        """List members (active by default; bajas with include_inactive)."""
        return [
            _member_response(manager, member)
            for member in manager.list_members(organization_id, include_inactive)
        ]

    @router.post(
        "/{organization_id}/members", status_code=status.HTTP_201_CREATED
    )
    async def add_member(
        organization_id: str,
        data: MemberCreate,
        user: AuthUser = Depends(require_admin),
    ):
        """Alta individual de un socio."""
        member, _ = manager.add_member(
            organization_id=organization_id,
            name=data.name,
            email=data.email,
            phone=data.phone,
            role=data.role,
            valid_until=data.valid_until,
        )
        return _member_response(manager, member)

    @router.post("/{organization_id}/members/{member_id}/suspend")
    async def suspend_member(
        organization_id: str,
        member_id: str,
        user: AuthUser = Depends(require_admin),
    ):
        """Suspender el carnet (revocación instantánea, reversible)."""
        membership = manager.suspend_member(member_id)
        if not membership:
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        return {"member_id": member_id, "estado": membership.status.value}

    @router.post("/{organization_id}/members/{member_id}/reactivate")
    async def reactivate_member(
        organization_id: str,
        member_id: str,
        user: AuthUser = Depends(require_admin),
    ):
        """Reactivar el carnet."""
        membership = manager.reactivate_member(member_id)
        if not membership:
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        return {"member_id": member_id, "estado": membership.status.value}

    @router.delete("/{organization_id}/members/{member_id}")
    async def deactivate_member(
        organization_id: str,
        member_id: str,
        user: AuthUser = Depends(require_admin),
    ):
        """Baja lógica (soft delete): persiste para auditoría, carnet inválido."""
        member = manager.deactivate_member(member_id)
        if not member:
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        return {"member_id": member_id, "estado": "baja", "deleted": False}

    @router.get("/{organization_id}/members/{member_id}/card")
    async def issue_card(
        organization_id: str,
        member_id: str,
        user: AuthUser = Depends(require_admin),
    ):
        """Emitir el carnet digital: URL de verificación firmada + QR."""
        card = manager.issue_card(member_id, base_url, secret_key=secret_key)
        if not card:
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        return card

    # --- Roster: import, log, export ---

    @router.post("/{organization_id}/roster/import")
    async def import_roster_file(
        organization_id: str,
        file: UploadFile = File(...),
        user: AuthUser = Depends(require_admin),
    ):
        """
        Upload the roster (CSV/XLSX). Upsert by email; malformed rows
        are reported without aborting the rest (partial import).
        """
        content = await file.read()
        try:
            rows = parse_roster_file(file.filename or "padron.csv", content)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            )

        log = import_roster(
            manager.storage, organization_id, rows, filename=file.filename
        )
        return log.to_dict()

    @router.get("/{organization_id}/roster/imports")
    async def list_import_logs(
        organization_id: str, user: AuthUser = Depends(require_admin)
    ):
        """Queryable import history (newest first)."""
        return manager.storage.list_import_logs(organization_id)

    @router.get("/{organization_id}/roster/export")
    async def export_roster(
        organization_id: str,
        format: str = "csv",
        user: AuthUser = Depends(require_admin),
    ):
        """Download the current roster with effective states (csv|xlsx)."""
        organization = _get_org(organization_id)
        stamp = datetime.now().strftime("%Y%m%d")

        if format == "xlsx":
            data = export_roster_xlsx(manager.storage, organization_id)
            media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"padron-{organization.slug}-{stamp}.xlsx"
        else:
            data = export_roster_csv(manager.storage, organization_id)
            media = "text/csv; charset=utf-8"
            filename = f"padron-{organization.slug}-{stamp}.csv"

        return Response(
            data,
            media_type=media,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            },
        )

    return router
