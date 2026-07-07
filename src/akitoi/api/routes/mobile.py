"""
Mobile-first public endpoints: hub page, vCard, QR, NFC and assistant.

Privacy rules enforced here:
- Only PUBLISHED profiles are served (404 otherwise).
- Everything returned derives from ContactCard (basic data only).
"""
import base64
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from pydantic import BaseModel, Field

from ...core.profile_manager import ProfileManager
from ...mobile.contact_card import build_contact_card
from ...mobile.vcard import contact_card_to_vcard
from ...mobile.qr import qr_svg, wallpaper_png
from ...mobile.nfc import profile_ndef
from ...mobile.assistant import ContactAssistant
from ...mobile.page import render_profile_page


class ContactMessageIn(BaseModel):
    """Visitor message for the contact assistant."""

    sender_name: str = Field(..., min_length=1, max_length=80)
    sender_contact: str = Field(..., min_length=3, max_length=120)
    message: str = Field(..., min_length=1, max_length=500)
    company: str = ""  # honeypot: bots fill it, humans never see it


def create_mobile_router(
    manager: ProfileManager,
    base_url: str = "https://akitoi.bio",
    assistant: Optional[ContactAssistant] = None,
) -> APIRouter:
    """
    Build the mobile router around an existing ProfileManager so the
    mobile layer shares storage with the rest of the API.
    """
    router = APIRouter()
    assistant = assistant or ContactAssistant()
    base = base_url.rstrip("/")

    def _get_published(slug: str):
        profile = manager.get_profile_by_slug(slug)
        if not profile or not profile.is_published:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile not found: {slug}",
            )
        return profile

    @router.get("/m/{slug}", response_class=HTMLResponse)
    async def mobile_page(slug: str):
        """Public mobile hub page (records a view)."""
        profile = _get_published(slug)
        manager.record_view(slug)
        card = build_contact_card(profile, base)
        return render_profile_page(profile, card.summary, f"/m/{slug}")

    @router.get("/m/{slug}/card")
    async def public_card(slug: str):
        """Public contact card as JSON (basic data only)."""
        profile = _get_published(slug)
        return build_contact_card(profile, base).to_dict()

    @router.get("/m/{slug}/vcard")
    async def vcard(slug: str):
        """vCard download — saves the contact into the phone's address book."""
        profile = _get_published(slug)
        card = build_contact_card(profile, base)
        return PlainTextResponse(
            contact_card_to_vcard(card),
            media_type="text/vcard; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{slug}.vcf"'},
        )

    @router.get("/m/{slug}/qr.svg")
    async def qr_image(slug: str, content: str = "url"):
        """
        QR code as SVG. content=url points to the hub;
        content=vcard embeds the full contact for offline scanning.
        """
        profile = _get_published(slug)
        card = build_contact_card(profile, base)
        data = (
            contact_card_to_vcard(card)
            if content == "vcard"
            else card.profile_url or f"{base}/{slug}"
        )
        svg = qr_svg(data, dark=profile.theme.primary_color)
        return Response(svg, media_type="image/svg+xml")

    @router.get("/m/{slug}/wallpaper.png")
    async def qr_wallpaper(slug: str, content: str = "vcard"):
        """High-res QR PNG for a lock-screen wallpaper (offline vCard by default)."""
        profile = _get_published(slug)
        card = build_contact_card(profile, base)
        data = (
            contact_card_to_vcard(card)
            if content == "vcard"
            else card.profile_url or f"{base}/{slug}"
        )
        png = wallpaper_png(
            data,
            dark=profile.theme.primary_color,
            light=profile.theme.background_color,
        )
        return Response(png, media_type="image/png")

    @router.get("/m/{slug}/nfc")
    async def nfc_payload(slug: str, include_vcard: bool = True):
        """
        NDEF payload for writing NFC tags — tap-to-share the profile.
        Returns hex and base64 so any NFC writer app can burn it.
        """
        profile = _get_published(slug)
        card = build_contact_card(profile, base)
        vcard_text = contact_card_to_vcard(card) if include_vcard else None
        message = profile_ndef(card.profile_url or f"{base}/{slug}", vcard_text)
        return {
            "slug": slug,
            "records": ["uri"] + (["vcard"] if include_vcard else []),
            "size_bytes": len(message),
            "ndef_hex": message.hex(),
            "ndef_base64": base64.b64encode(message).decode("ascii"),
            "how_to": (
                "Escribe este payload NDEF en un tag NTAG213/215/216 con "
                "cualquier app de escritura NFC. Al acercar un teléfono, "
                "abrirá el hub o importará el contacto."
            ),
        }

    @router.post("/m/{slug}/contact", status_code=status.HTTP_201_CREATED)
    async def contact_via_assistant(slug: str, body: ContactMessageIn):
        """Leave a message with the contact assistant (intermediary)."""
        profile = _get_published(slug)
        if body.company:  # honeypot tripped -> pretend success, store nothing
            return {"status": "received"}
        try:
            request = assistant.receive_request(
                profile, body.sender_name, body.sender_contact, body.message
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            )
        return {"status": "received", "request_id": request.id}

    return router
