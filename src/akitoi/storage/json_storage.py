"""
JSON file storage backend for Akitoi platform.
"""
import json
import os
from pathlib import Path
from typing import Optional, List, Dict
from threading import Lock

from .base import StorageBackend
from ..models.profile import Profile


class JSONStorage(StorageBackend):
    """
    JSON file-based storage backend.

    Simple storage implementation for MVP using JSON files.
    Each profile is stored as a separate JSON file.
    """

    def __init__(self, storage_path: str = ".akitoi_data"):
        """
        Initialize JSON storage.

        Args:
            storage_path: Directory to store profile JSON files
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self._lock = Lock()

    def _get_profile_path(self, profile_id: str) -> Path:
        """Get file path for a profile."""
        return self.storage_path / f"{profile_id}.json"

    def _get_index_path(self) -> Path:
        """Get path to the index file (slug -> profile_id mapping)."""
        return self.storage_path / "index.json"

    def _load_index(self) -> Dict[str, str]:
        """Load slug -> profile_id index."""
        index_path = self._get_index_path()
        if not index_path.exists():
            return {}

        with open(index_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_index(self, index: Dict[str, str]) -> None:
        """Save slug -> profile_id index."""
        index_path = self._get_index_path()
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2)

    def save_profile(self, profile: Profile) -> None:
        """Save a profile to JSON file."""
        with self._lock:
            profile_path = self._get_profile_path(profile.id)

            # Save profile data
            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)

            # Update index
            index = self._load_index()
            index[profile.slug] = profile.id
            self._save_index(index)

    def get_profile(self, profile_id: str) -> Optional[Profile]:
        """Get a profile by ID."""
        with self._lock:
            profile_path = self._get_profile_path(profile_id)

            if not profile_path.exists():
                return None

            with open(profile_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return Profile.from_dict(data)

    def get_profile_by_slug(self, slug: str) -> Optional[Profile]:
        """Get a profile by slug."""
        with self._lock:
            index = self._load_index()
            profile_id = index.get(slug)

            if not profile_id:
                return None

            return self.get_profile(profile_id)

    def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile."""
        with self._lock:
            profile_path = self._get_profile_path(profile_id)

            if not profile_path.exists():
                return False

            # Get profile to remove from index
            profile = self.get_profile(profile_id)
            if profile:
                index = self._load_index()
                if profile.slug in index:
                    del index[profile.slug]
                    self._save_index(index)

            # Delete profile file
            profile_path.unlink()
            return True

    def list_profiles(self) -> List[Profile]:
        """List all profiles."""
        with self._lock:
            profiles = []
            for file_path in self.storage_path.glob("*.json"):
                if file_path.name == "index.json":
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        profiles.append(Profile.from_dict(data))
                except (json.JSONDecodeError, KeyError, ValueError):
                    # Skip corrupted files
                    continue

            return profiles

    def slug_exists(self, slug: str) -> bool:
        """Check if a slug exists."""
        with self._lock:
            index = self._load_index()
            return slug in index
