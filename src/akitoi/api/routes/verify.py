"""
Public membership verification endpoint (dynamic QR target).

GET /verify/{token}:
1. Validates the token signature (401 on tampered/expired tokens).
2. Resolves the Membership server-side and evaluates is_active().
3. Returns a human-readable verdict — vigente / suspendido / vencido —
   with MINIMAL data: member name, organization name and logo. No ids,
   no contact data, no analytics.

The free-tier static QR (.vcf / hub URL) is a different flow and is
not touched by this router.
"""
from datetime import datetime
from string import Template
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, Response

from ...core.membership_tokens import InvalidTokenError, verify_membership_token
from ...mobile.qr import qr_svg
from ...models.membership import Membership, MembershipStatus
from ...storage.org_base import OrgStorageBackend

_STATUS_LABELS = {
    "vigente": ("VIGENTE", "#16a34a", "✔ Membresía activa"),
    "suspendido": ("SUSPENDIDO", "#dc2626", "✖ Membresía suspendida"),
    "vencido": ("VENCIDO", "#d97706", "✖ Membresía vencida"),
}

_PAGE = Template("""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Verificación · $org_name</title>
<style>
*{box-sizing:border-box;margin:0}
body{font-family:system-ui,sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;background:#f8fafc;color:#1e293b}
main{text-align:center;padding:32px;max-width:380px;width:100%}
.logo{max-height:56px;margin:0 auto 14px;display:block}
.badge{display:inline-block;padding:14px 28px;border-radius:999px;color:#fff;font-size:1.3rem;font-weight:700;background:$color;margin:14px 0}
h1{font-size:1.15rem;opacity:.85}
.member{font-size:1.35rem;font-weight:700;margin-top:16px}
.detail{opacity:.7;font-size:.9rem;margin-top:6px}
footer{margin-top:30px;font-size:.72rem;opacity:.45}
</style>
</head>
<body>
<main>
$logo_html
<h1>$org_name</h1>
<div class="badge">$status_label</div>
<p class="member">$member_name</p>
<p class="detail">$verdict</p>
<p class="detail">Verificado: $checked_at</p>
<footer>Verificación Akitoi · este resultado se consulta en vivo</footer>
</main>
</body>
</html>
""")


def _effective_status(membership: Membership) -> str:
    """Status as the door should see it (stale VIGENTE counts as vencido)."""
    if membership.status == MembershipStatus.VIGENTE and not membership.is_active():
        return MembershipStatus.VENCIDO.value
    return membership.status.value


def create_verify_router(
    storage: OrgStorageBackend,
    secret_key: Optional[str] = None,
    token_max_age: Optional[int] = None,
) -> APIRouter:
    """
    Build the verification router around an organizational storage.

    Args:
        storage: Organizational storage backend
        secret_key: Override signing key (tests); defaults to SECRET_KEY
        token_max_age: Optional global cap on token signature age (seconds)
    """
    router = APIRouter()

    @router.get("/verify/{token}/qr.svg")
    async def verify_qr(token: str, request: Request):
        """
        Public QR of the verification URL (for the digital card view).

        Exposes nothing the token holder doesn't already have: it only
        re-encodes /verify/{token} as a scannable image, tinted with
        the club's theme color.
        """
        try:
            payload = verify_membership_token(
                token, max_age=token_max_age, secret_key=secret_key
            )
        except InvalidTokenError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token inválido: {exc}",
            )

        organization = storage.get_organization(payload.get("org", ""))
        dark = organization.theme.primary_color if organization else "#000000"
        verify_url = str(request.base_url).rstrip("/") + f"/verify/{token}"
        return Response(qr_svg(verify_url, dark=dark), media_type="image/svg+xml")

    @router.get("/verify/{token}")
    async def verify_membership(token: str, request: Request, format: str = "html"):
        """Verify a signed membership token (dynamic QR target)."""
        try:
            payload = verify_membership_token(
                token, max_age=token_max_age, secret_key=secret_key
            )
        except InvalidTokenError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token inválido: {exc}",
            )

        membership = storage.get_membership(payload["mid"])
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membresía no encontrada",
            )

        member = storage.get_member(membership.member_id)
        organization = storage.get_organization(membership.organization_id)

        status_value = _effective_status(membership)
        label, color, verdict = _STATUS_LABELS[status_value]
        checked_at = datetime.now()

        wants_json = format == "json" or "application/json" in request.headers.get(
            "accept", ""
        )
        if wants_json:
            return JSONResponse({
                "valid": membership.is_active(),
                "status": status_value,
                "member": {"name": member.name if member else "Socio"},
                "organization": {
                    "name": organization.name if organization else "",
                    "logo_url": organization.logo_url if organization else None,
                },
                "checked_at": checked_at.isoformat(),
            })

        logo_html = (
            f'<img class="logo" src="{organization.logo_url}" alt="Logo">'
            if organization and organization.logo_url
            else ""
        )
        return HTMLResponse(_PAGE.substitute(
            org_name=_escape(organization.name if organization else ""),
            member_name=_escape(member.name if member else "Socio"),
            status_label=label,
            color=color,
            verdict=verdict,
            checked_at=checked_at.strftime("%d/%m/%Y %H:%M"),
            logo_html=logo_html,
        ))

    return router


def _escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
