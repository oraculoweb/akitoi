#!/usr/bin/env python
"""
Generate a LOCAL DEV admin token for the clubs panel.

Signs a Supabase-shaped JWT with the same dev fallback secret the
backend uses when SUPABASE_JWT_SECRET is unset, so the token is valid
against a locally-running API. Useless (correctly rejected) against
any deployment with a real secret.

Usage:
    python scripts/make_demo_token.py [user_id]
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import jwt  # noqa: E402

from akitoi.api.auth import _DEV_FALLBACK_JWT_SECRET  # noqa: E402

DEMO_USER_ID = "demo-admin-akitoi"


def make_token(user_id: str = DEMO_USER_ID, days: int = 7) -> str:
    now = int(time.time())
    return jwt.encode(
        {
            "sub": user_id,
            "aud": "authenticated",
            "email": "admin@demo.akitoi",
            "role": "authenticated",
            "iat": now,
            "exp": now + days * 86400,
        },
        _DEV_FALLBACK_JWT_SECRET,
        algorithm="HS256",
    )


if __name__ == "__main__":
    user_id = sys.argv[1] if len(sys.argv) > 1 else DEMO_USER_ID
    print(make_token(user_id))
