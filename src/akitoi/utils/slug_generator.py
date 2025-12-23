"""
Slug generation utilities for Akitoi platform.
"""
import re
import random
import string
from typing import Optional, Callable


def generate_slug(name: str, max_length: int = 50) -> str:
    """
    Generate a URL-friendly slug from a name.

    Args:
        name: The name to convert to slug
        max_length: Maximum length of the slug

    Returns:
        URL-friendly slug
    """
    # Convert to lowercase
    slug = name.lower()

    # Replace spaces and underscores with hyphens
    slug = re.sub(r"[\s_]+", "-", slug)

    # Remove special characters
    slug = re.sub(r"[^a-z0-9-]", "", slug)

    # Remove multiple consecutive hyphens
    slug = re.sub(r"-+", "-", slug)

    # Remove leading/trailing hyphens
    slug = slug.strip("-")

    # Truncate to max length
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip("-")

    # Ensure slug is not empty
    if not slug:
        slug = generate_random_slug()

    return slug


def generate_random_slug(length: int = 8) -> str:
    """
    Generate a random slug.

    Args:
        length: Length of the random slug

    Returns:
        Random slug
    """
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def generate_unique_slug(
    base_slug: str,
    exists_check: Callable[[str], bool],
    max_attempts: int = 100
) -> str:
    """
    Generate a unique slug by appending numbers if needed.

    Args:
        base_slug: The base slug to start with
        exists_check: Function that returns True if slug exists
        max_attempts: Maximum number of attempts to generate unique slug

    Returns:
        Unique slug

    Raises:
        ValueError: If unable to generate unique slug after max_attempts
    """
    slug = base_slug

    if not exists_check(slug):
        return slug

    # Try appending numbers
    for i in range(1, max_attempts):
        candidate = f"{base_slug}-{i}"
        if not exists_check(candidate):
            return candidate

    # If still not unique, append random string
    random_suffix = generate_random_slug(6)
    final_slug = f"{base_slug}-{random_suffix}"

    if not exists_check(final_slug):
        return final_slug

    raise ValueError(f"Unable to generate unique slug after {max_attempts} attempts")


def generate_short_code(length: int = 6) -> str:
    """
    Generate a short code for URL shortening.

    Args:
        length: Length of the short code

    Returns:
        Short code
    """
    # Use alphanumeric characters (excluding similar-looking ones)
    chars = "abcdefghjkmnpqrstuvwxyz23456789"
    return "".join(random.choice(chars) for _ in range(length))
