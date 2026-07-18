"""
Supabase Auth integration for the management API.

Identity is NOT duplicated: the frontend logs in against Supabase
Auth and sends the resulting access token as `Authorization: Bearer
<jwt>`. This module only VERIFIES that token (HS256 signature against
the project's SUPABASE_JWT_SECRET, expiry and audience) and extracts
the Supabase user id (`sub` claim). No parallel user table, no
password handling in this backend.

Authorization (which club a user may manage) is a separate concern:
see OrganizationAdmin and the require_admin dependency in
api/routes/organizations.py.
"""
import os
import warnings
from dataclasses import dataclass, field
from typing import Callable, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..config import is_production

_DEV_FALLBACK_JWT_SECRET = "akitoi-dev-only-jwt-secret"

_bearer = HTTPBearer(auto_error=False)


@dataclass
class AuthUser:
    """Authenticated Supabase user extracted from a verified JWT."""

    user_id: str
    email: Optional[str] = None
    claims: dict = field(default_factory=dict)


def get_supabase_jwt_secret() -> str:
    """
    Return the Supabase JWT secret from the environment.

    Found in Supabase: Project Settings -> API -> JWT Secret.

    Raises:
        RuntimeError: In production when SUPABASE_JWT_SECRET is not set.
    """
    secret = os.environ.get("SUPABASE_JWT_SECRET")
    if secret:
        return secret

    if is_production():
        raise RuntimeError(
            "SUPABASE_JWT_SECRET is not set. Copy it from your Supabase "
            "project (Settings -> API -> JWT Secret) and export it in the "
            "environment (see .env.example)."
        )

    warnings.warn(
        "SUPABASE_JWT_SECRET not set — using the insecure development "
        "fallback. Never use this outside local development.",
        stacklevel=2,
    )
    return _DEV_FALLBACK_JWT_SECRET


def create_user_dependency(
    jwt_secret: Optional[str] = None,
    audience: Optional[str] = None,
) -> Callable:
    """
    Build a FastAPI dependency that authenticates Supabase JWTs.

    Args:
        jwt_secret: Override secret (tests); defaults to SUPABASE_JWT_SECRET
        audience: Expected `aud` claim; defaults to
            SUPABASE_JWT_AUDIENCE or "authenticated" (Supabase default)

    Returns:
        Dependency callable yielding an AuthUser (401 otherwise)
    """
    expected_audience = audience or os.environ.get(
        "SUPABASE_JWT_AUDIENCE", "authenticated"
    )

    async def current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    ) -> AuthUser:
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Falta el token de autenticación",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            payload = jwt.decode(
                credentials.credentials,
                jwt_secret or get_supabase_jwt_secret(),
                algorithms=["HS256"],
                audience=expected_audience,
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token inválido: {exc}",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token sin identidad (claim sub)",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return AuthUser(
            user_id=user_id,
            email=payload.get("email"),
            claims=payload,
        )

    return current_user
