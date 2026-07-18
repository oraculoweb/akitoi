"""
Signed membership tokens and the dynamic verification QR.

Free-tier QRs are static pointers (.vcf / hub URL) and stay untouched.
Club credentials are different: the QR encodes a SIGNED verification
URL — {BASE_URL}/verify/{token} — where the token:

- is signed with SECRET_KEY (itsdangerous URLSafeTimedSerializer,
  HMAC-SHA1 over an urlsafe payload): tampering breaks the signature;
- carries an opaque payload identifying the membership (a random
  UUIDv4 id — non-enumerable — never exposed as a plain path param);
- can embed its own short signature expiry ("exp"), independent from
  the membership's valid_until, so a leaked/screenshotted QR dies on
  its own even if the membership stays active.

Validity itself is NEVER inside the token: the /verify endpoint
resolves the membership server-side and asks is_active(), which is
what makes revocation instant (see models/membership.py).
"""
import time
from typing import Optional

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from ..config import get_secret_key
from ..models.membership import Membership
from ..mobile import qr as qr_generator

_SALT = "akitoi.membership.verify"


class InvalidTokenError(Exception):
    """Raised when a membership token is tampered, malformed or expired."""


def _serializer(secret_key: Optional[str] = None) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(secret_key or get_secret_key(), salt=_SALT)


def generate_membership_token(
    membership: Membership,
    expires_in: Optional[int] = None,
    secret_key: Optional[str] = None,
) -> str:
    """
    Generate a signed, URL-safe token for a membership.

    Args:
        membership: Membership to reference
        expires_in: Optional signature lifetime in seconds (independent
            from the membership's valid_until). None = no embedded expiry.
        secret_key: Override key (tests); defaults to SECRET_KEY

    Returns:
        Signed token string, safe to embed in a URL/QR
    """
    payload = {"mid": membership.id, "org": membership.organization_id}
    if expires_in is not None:
        payload["exp"] = int(time.time()) + expires_in
    return _serializer(secret_key).dumps(payload)


def verify_membership_token(
    token: str,
    max_age: Optional[int] = None,
    secret_key: Optional[str] = None,
) -> dict:
    """
    Validate a token's signature and expiry, returning its payload.

    Args:
        token: Token string from the verification URL
        max_age: Optional maximum signature age in seconds, enforced on
            top of any embedded "exp" claim
        secret_key: Override key (tests); defaults to SECRET_KEY

    Returns:
        Payload dict with "mid" (membership id) and "org"

    Raises:
        InvalidTokenError: On tampered, malformed or expired tokens
    """
    try:
        payload = _serializer(secret_key).loads(token, max_age=max_age)
    except SignatureExpired as exc:
        raise InvalidTokenError("Token signature expired") from exc
    except BadSignature as exc:
        raise InvalidTokenError("Invalid token signature") from exc

    if not isinstance(payload, dict) or "mid" not in payload:
        raise InvalidTokenError("Malformed token payload")

    exp = payload.get("exp")
    if exp is not None and time.time() > exp:
        raise InvalidTokenError("Token expired")

    return payload


def membership_verify_url(
    membership: Membership,
    base_url: str,
    expires_in: Optional[int] = None,
    secret_key: Optional[str] = None,
) -> str:
    """Build the public verification URL for a membership."""
    token = generate_membership_token(membership, expires_in, secret_key)
    return f"{base_url.rstrip('/')}/verify/{token}"


def membership_qr_svg(
    membership: Membership,
    base_url: str,
    dark: str = "#000000",
    expires_in: Optional[int] = None,
    secret_key: Optional[str] = None,
) -> str:
    """
    Dynamic membership QR as SVG.

    Reuses the existing generator in mobile/qr — only the payload
    changes: a signed verification URL instead of a .vcf/hub URL.
    """
    url = membership_verify_url(membership, base_url, expires_in, secret_key)
    return qr_generator.qr_svg(url, dark=dark)


def membership_qr_png(
    membership: Membership,
    base_url: str,
    dark: str = "#000000",
    expires_in: Optional[int] = None,
    secret_key: Optional[str] = None,
) -> bytes:
    """Dynamic membership QR as PNG (same reuse of mobile/qr)."""
    url = membership_verify_url(membership, base_url, expires_in, secret_key)
    return qr_generator.qr_png(url, dark=dark)
