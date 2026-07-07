"""
Profile management endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ...core.profile_manager import ProfileManager
from ...models.profile import Profile
from ...models.link import Link, LinkType
from ...models.theme import Theme
from ...storage.database_storage import DatabaseStorage

router = APIRouter()

# Initialize profile manager with Supabase database storage
profile_manager = ProfileManager(storage=DatabaseStorage())


# Pydantic schemas for API
class LinkCreate(BaseModel):
    """Schema for creating a link."""
    type: LinkType
    url: str
    label: Optional[str] = None
    icon: Optional[str] = None


class ThemeCreate(BaseModel):
    """Schema for theme."""
    primary_color: str = "#007bff"
    background_color: str = "#ffffff"
    text_color: str = "#333333"
    font_family: str = "Inter, sans-serif"


class ProfileCreate(BaseModel):
    """Schema for creating a profile."""
    name: str = Field(..., min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=3, max_length=50)
    bio: str = Field(default="", max_length=500)
    profile_image_url: Optional[str] = None
    logo_url: Optional[str] = None
    theme: Optional[ThemeCreate] = None


class ProfileUpdate(BaseModel):
    """Schema for updating a profile."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    profile_image_url: Optional[str] = None
    logo_url: Optional[str] = None


class ProfileResponse(BaseModel):
    """Schema for profile response."""
    id: str
    name: str
    slug: str
    bio: str
    profile_image_url: Optional[str]
    logo_url: Optional[str]
    links: List[dict]
    theme: dict
    is_published: bool
    view_count: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.get("/{slug}", response_model=ProfileResponse)
async def get_profile_by_slug(slug: str):
    """
    Get a profile by its slug.

    This is the main endpoint for viewing public profiles.
    """
    profile = profile_manager.get_profile_by_slug(slug)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile not found: {slug}"
        )

    # Record view
    profile_manager.record_view(slug)

    # Convert to dict for response
    return ProfileResponse(
        id=profile.id,
        name=profile.name,
        slug=profile.slug,
        bio=profile.bio,
        profile_image_url=profile.profile_image_url,
        logo_url=profile.logo_url,
        links=[link.to_dict() for link in profile.links],
        theme=profile.theme.to_dict(),
        is_published=profile.is_published,
        view_count=profile.views,
        created_at=profile.created_at.isoformat(),
        updated_at=profile.updated_at.isoformat(),
    )


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(profile_data: ProfileCreate):
    """
    Create a new profile.
    """
    try:
        # Convert theme if provided
        theme = None
        if profile_data.theme:
            theme = Theme(
                primary_color=profile_data.theme.primary_color,
                background_color=profile_data.theme.background_color,
                text_color=profile_data.theme.text_color,
                font_family=profile_data.theme.font_family,
            )

        profile = profile_manager.create_profile(
            name=profile_data.name,
            slug=profile_data.slug,
            bio=profile_data.bio,
            profile_image_url=profile_data.profile_image_url,
            logo_url=profile_data.logo_url,
            theme=theme,
        )

        return ProfileResponse(
            id=profile.id,
            name=profile.name,
            slug=profile.slug,
            bio=profile.bio,
            profile_image_url=profile.profile_image_url,
            logo_url=profile.logo_url,
            links=[link.to_dict() for link in profile.links],
            theme=profile.theme.to_dict(),
            is_published=profile.is_published,
            view_count=profile.views,
            created_at=profile.created_at.isoformat(),
            updated_at=profile.updated_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=List[ProfileResponse])
async def list_profiles():
    """
    List all profiles.
    """
    profiles = profile_manager.list_profiles()

    return [
        ProfileResponse(
            id=profile.id,
            name=profile.name,
            slug=profile.slug,
            bio=profile.bio,
            profile_image_url=profile.profile_image_url,
            logo_url=profile.logo_url,
            links=[link.to_dict() for link in profile.links],
            theme=profile.theme.to_dict(),
            is_published=profile.is_published,
            view_count=profile.views,
            created_at=profile.created_at.isoformat(),
            updated_at=profile.updated_at.isoformat(),
        )
        for profile in profiles
    ]


@router.patch("/{profile_id}", response_model=ProfileResponse)
async def update_profile(profile_id: str, profile_data: ProfileUpdate):
    """
    Update a profile.
    """
    profile = profile_manager.update_profile(
        profile_id=profile_id,
        name=profile_data.name,
        bio=profile_data.bio,
        profile_image_url=profile_data.profile_image_url,
        logo_url=profile_data.logo_url,
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile not found: {profile_id}"
        )

    return ProfileResponse(
        id=profile.id,
        name=profile.name,
        slug=profile.slug,
        bio=profile.bio,
        profile_image_url=profile.profile_image_url,
        logo_url=profile.logo_url,
        links=[link.to_dict() for link in profile.links],
        theme=profile.theme.to_dict(),
        is_published=profile.is_published,
        view_count=profile.views,
        created_at=profile.created_at.isoformat(),
        updated_at=profile.updated_at.isoformat(),
    )


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: str):
    """
    Delete a profile.
    """
    success = profile_manager.delete_profile(profile_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile not found: {profile_id}"
        )


@router.post("/{profile_id}/links", response_model=ProfileResponse)
async def add_link(profile_id: str, link_data: LinkCreate):
    """
    Add a link to a profile.
    """
    link = Link(
        title=link_data.label or link_data.type.value.title(),
        url=link_data.url,
        link_type=link_data.type,
        icon=link_data.icon,
    )

    profile = profile_manager.add_link(profile_id, link)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile not found: {profile_id}"
        )

    return ProfileResponse(
        id=profile.id,
        name=profile.name,
        slug=profile.slug,
        bio=profile.bio,
        profile_image_url=profile.profile_image_url,
        logo_url=profile.logo_url,
        links=[link.to_dict() for link in profile.links],
        theme=profile.theme.to_dict(),
        is_published=profile.is_published,
        view_count=profile.views,
        created_at=profile.created_at.isoformat(),
        updated_at=profile.updated_at.isoformat(),
    )


@router.post("/{profile_id}/publish", response_model=ProfileResponse)
async def publish_profile(profile_id: str):
    """
    Publish a profile (make it public).
    """
    profile = profile_manager.publish_profile(profile_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile not found: {profile_id}"
        )

    return ProfileResponse(
        id=profile.id,
        name=profile.name,
        slug=profile.slug,
        bio=profile.bio,
        profile_image_url=profile.profile_image_url,
        logo_url=profile.logo_url,
        links=[link.to_dict() for link in profile.links],
        theme=profile.theme.to_dict(),
        is_published=profile.is_published,
        view_count=profile.views,
        created_at=profile.created_at.isoformat(),
        updated_at=profile.updated_at.isoformat(),
    )


@router.post("/{slug}/view")
async def record_view(slug: str):
    """
    Record a profile view.
    """
    profile = profile_manager.record_view(slug)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile not found: {slug}"
        )

    return {"message": "View recorded", "view_count": profile.views}
