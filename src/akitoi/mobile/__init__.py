"""
Akitoi Mobile - Minimal mobile-first contact sharing layer.

Turns a Profile into something a phone understands natively:
- ContactCard: privacy-filtered public view of a profile
- vCard (.vcf): saves directly into the phone's address book
- QR: scannable codes (URL or full offline vCard) + wallpaper PNG
- NFC/NDEF: tap-to-share payloads for NFC tags
- ContactAssistant: intermediary so visitors reach you without
  exposing private data
"""

from .contact_card import ContactCard, build_contact_card
from .vcard import contact_card_to_vcard
from .assistant import ContactAssistant, ContactRequest

__all__ = [
    "ContactCard",
    "build_contact_card",
    "contact_card_to_vcard",
    "ContactAssistant",
    "ContactRequest",
]
