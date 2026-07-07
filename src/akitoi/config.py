"""
Application configuration read from environment variables.

SECRET_KEY signs membership verification tokens (and any future
signed artifact). It must NEVER be hardcoded or committed: set it via
the environment (see .env.example). In production the app refuses to
start without it; in development a fixed insecure fallback is used so
local work "just runs", with a loud warning.
"""
import os
import warnings

_DEV_FALLBACK_SECRET = "akitoi-dev-only-insecure-secret"


def is_production() -> bool:
    """True when ENVIRONMENT points to a production deployment."""
    return os.environ.get("ENVIRONMENT", "development").lower() in (
        "production",
        "prod",
    )


def get_secret_key() -> str:
    """
    Return the signing key from the SECRET_KEY environment variable.

    Raises:
        RuntimeError: In production when SECRET_KEY is not set.
    """
    key = os.environ.get("SECRET_KEY")
    if key:
        return key

    if is_production():
        raise RuntimeError(
            "SECRET_KEY is not set. Generate one with "
            "`python -c \"import secrets; print(secrets.token_urlsafe(32))\"` "
            "and export it in the environment (see .env.example)."
        )

    warnings.warn(
        "SECRET_KEY not set — using the insecure development fallback. "
        "Never use this outside local development.",
        stacklevel=2,
    )
    return _DEV_FALLBACK_SECRET
