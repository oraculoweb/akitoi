"""
Validation utilities for Akitoi platform.
"""
import re
from typing import Optional


def validate_slug(slug: str) -> bool:
    """
    Validate that slug contains only alphanumeric characters and hyphens.

    Args:
        slug: The slug to validate

    Returns:
        True if valid, False otherwise
    """
    if not slug:
        return False

    # Slug must be 3-50 characters, lowercase alphanumeric and hyphens only
    pattern = r"^[a-z0-9][a-z0-9-]{1,48}[a-z0-9]$"
    return bool(re.match(pattern, slug))


def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: The email to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: The URL to validate

    Returns:
        True if valid, False otherwise
    """
    # Basic URL validation
    pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    return bool(re.match(pattern, url))


def validate_whatsapp(phone: str) -> bool:
    """
    Validate WhatsApp phone number format.

    Args:
        phone: The phone number to validate (should include country code)

    Returns:
        True if valid, False otherwise
    """
    # Remove common separators
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)

    # Should start with + and have 10-15 digits
    pattern = r"^\+\d{10,15}$"
    return bool(re.match(pattern, cleaned))


def sanitize_slug(slug: str) -> str:
    """
    Sanitize and normalize a slug.

    Args:
        slug: The slug to sanitize

    Returns:
        Sanitized slug
    """
    # Convert to lowercase
    slug = slug.lower()

    # Replace spaces with hyphens
    slug = re.sub(r"\s+", "-", slug)

    # Remove special characters
    slug = re.sub(r"[^a-z0-9-]", "", slug)

    # Remove multiple consecutive hyphens
    slug = re.sub(r"-+", "-", slug)

    # Remove leading/trailing hyphens
    slug = slug.strip("-")

    return slug


def validate_hex_color(color: str) -> bool:
    """
    Validate hex color format.

    Args:
        color: The color to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    return bool(re.match(pattern, color))
