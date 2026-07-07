"""
NFC / NDEF payload generation — the "more modern than QR" wireless path.

An NDEF (NFC Data Exchange Format) message written to an inexpensive
NTAG sticker (or emulated by a phone with HCE) lets someone share
their Akitoi hub with a single tap: the receiving phone opens the hub
URL or imports the vCard directly, no camera or app required.

This module builds spec-compliant NDEF messages as raw bytes; the
API exposes them hex/base64-encoded so any tag-writer app or hardware
encoder can burn them onto a tag.

Reference: NFC Forum NDEF 1.0 + RTD-URI 1.0.
"""
from typing import List, Optional, Tuple

# RTD-URI abbreviation table (subset): code byte -> URI prefix
URI_PREFIXES: List[Tuple[int, str]] = [
    (0x02, "https://www."),
    (0x04, "https://"),
    (0x01, "http://www."),
    (0x03, "http://"),
]

TNF_WELL_KNOWN = 0x01
TNF_MIME = 0x02

_FLAG_MB = 0x80  # Message Begin
_FLAG_ME = 0x40  # Message End
_FLAG_SR = 0x10  # Short Record


def encode_uri_payload(url: str) -> bytes:
    """Encode a URL as an RTD-URI payload (prefix byte + remainder)."""
    for code, prefix in URI_PREFIXES:
        if url.startswith(prefix):
            return bytes([code]) + url[len(prefix):].encode("utf-8")
    return b"\x00" + url.encode("utf-8")


def ndef_record(
    tnf: int,
    record_type: bytes,
    payload: bytes,
    message_begin: bool = True,
    message_end: bool = True,
) -> bytes:
    """
    Build a single NDEF record.

    Uses the short-record form when the payload fits in one byte,
    otherwise the 4-byte length form.
    """
    flags = tnf & 0x07
    if message_begin:
        flags |= _FLAG_MB
    if message_end:
        flags |= _FLAG_ME

    if len(payload) < 256:
        flags |= _FLAG_SR
        length = bytes([len(payload)])
    else:
        length = len(payload).to_bytes(4, "big")

    return bytes([flags, len(record_type)]) + length + record_type + payload


def ndef_message(records: List[Tuple[int, bytes, bytes]]) -> bytes:
    """
    Build a full NDEF message from (tnf, type, payload) tuples,
    setting the MB flag on the first record and ME on the last.
    """
    if not records:
        raise ValueError("NDEF message requires at least one record")

    last = len(records) - 1
    return b"".join(
        ndef_record(tnf, rtype, payload, message_begin=(i == 0), message_end=(i == last))
        for i, (tnf, rtype, payload) in enumerate(records)
    )


def profile_ndef(profile_url: str, vcard: Optional[str] = None) -> bytes:
    """
    NDEF message for an Akitoi profile.

    Always carries a URI record with the hub URL; optionally appends
    the full vCard as a text/vcard MIME record so NFC-capable phones
    can import the contact without any network round trip.

    Args:
        profile_url: Public hub URL
        vcard: Optional vCard 3.0 text

    Returns:
        Raw NDEF message bytes, ready to write to a tag
    """
    records: List[Tuple[int, bytes, bytes]] = [
        (TNF_WELL_KNOWN, b"U", encode_uri_payload(profile_url)),
    ]
    if vcard:
        records.append((TNF_MIME, b"text/vcard", vcard.encode("utf-8")))
    return ndef_message(records)
