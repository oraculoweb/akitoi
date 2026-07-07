"""
vCard 3.0 generation.

A vCard is what lets a visitor save the profile straight into the
native contact book of any phone (iOS/Android) — either by
downloading the .vcf, scanning a QR that embeds it, or receiving it
over NFC.
"""
from .contact_card import ContactCard


def _escape(value: str) -> str:
    """Escape special characters per RFC 2426 / RFC 6350."""
    return (
        value.replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace(",", "\\,")
        .replace(";", "\\;")
    )


def contact_card_to_vcard(card: ContactCard) -> str:
    """
    Render a ContactCard as a vCard 3.0 string.

    vCard 3.0 is used (instead of 4.0) for maximum compatibility with
    both iOS and Android contact importers.

    Args:
        card: Public contact card

    Returns:
        vCard text with CRLF line endings
    """
    first, _, last = card.name.partition(" ")
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{_escape(last)};{_escape(first)};;;",
        f"FN:{_escape(card.name)}",
    ]

    if card.phone:
        lines.append(f"TEL;TYPE=CELL:{card.phone}")
    if card.email:
        lines.append(f"EMAIL;TYPE=INTERNET:{_escape(card.email)}")
    if card.website:
        lines.append(f"URL:{card.website}")
    if card.profile_url:
        lines.append(f"URL;TYPE=Akitoi:{card.profile_url}")
    for social_type, url in card.socials.items():
        lines.append(f"X-SOCIALPROFILE;TYPE={social_type}:{url}")
    if card.photo_url:
        lines.append(f"PHOTO;VALUE=URI:{card.photo_url}")
    elif card.logo_url:
        lines.append(f"LOGO;VALUE=URI:{card.logo_url}")
    if card.summary:
        lines.append(f"NOTE:{_escape(card.summary)}")

    lines.append("END:VCARD")
    return "\r\n".join(lines) + "\r\n"
