"""
FastAPI main application for Akitoi platform.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import profiles, health, analytics

app = FastAPI(
    title="Akitoi API",
    description="API for managing bio hub profiles with Supabase",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
# Allow frontend origins for development and production
origins = [
    "http://localhost:3000",  # Next.js dev server
    "http://localhost:8000",  # FastAPI dev server
    "https://*.vercel.app",   # Vercel preview deployments
]

# Add production domain if set
production_domain = os.getenv("PRODUCTION_DOMAIN")
if production_domain:
    origins.append(production_domain)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(profiles.router, prefix="/api/v1/profiles", tags=["Profiles"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])

# Mobile layer (public hub page, vCard, QR, NFC, contact assistant)
# shares the same ProfileManager/storage as the profiles routes.
from .routes.mobile import create_mobile_router  # noqa: E402

app.include_router(
    create_mobile_router(
        profiles.profile_manager,
        base_url=os.getenv("PUBLIC_BASE_URL", "https://akitoi.bio"),
    ),
    tags=["Mobile"],
)

# Clubs: public membership verification (dynamic signed QR target).
# JSON org storage for now; database backend lands with its migration.
from .routes.verify import create_verify_router  # noqa: E402
from ..storage.org_json_storage import JSONOrgStorage  # noqa: E402

app.include_router(create_verify_router(JSONOrgStorage()), tags=["Verification"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Akitoi API",
        "version": "0.1.0",
        "docs": "/docs",
    }
