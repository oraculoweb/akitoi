"""
JSON file storage backend for the organizational layer (clubs MVP).

Follows the same conventions as storage/json_storage.py: one JSON
file per entity, a slug index for organizations, thread-safe via a
re-entrant lock (methods re-enter each other, see JSONStorage).
"""
import json
from pathlib import Path
from typing import Optional, List, Dict
from threading import RLock

from .org_base import OrgStorageBackend
from ..models.organization import Organization
from ..models.member import Member
from ..models.membership import Membership


class JSONOrgStorage(OrgStorageBackend):
    """JSON file-based storage for organizations, members and memberships."""

    def __init__(self, storage_path: str = ".akitoi_data/orgs"):
        """
        Initialize JSON organizational storage.

        Args:
            storage_path: Root directory for organizational data
        """
        self.storage_path = Path(storage_path)
        self._org_dir = self.storage_path / "organizations"
        self._member_dir = self.storage_path / "members"
        self._membership_dir = self.storage_path / "memberships"
        for directory in (self._org_dir, self._member_dir, self._membership_dir):
            directory.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()

    # --- Generic helpers ---

    @staticmethod
    def _write(path: Path, data: dict) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _read(path: Path) -> Optional[dict]:
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_all(self, directory: Path) -> List[dict]:
        items = []
        for file_path in directory.glob("*.json"):
            if file_path.name == "index.json":
                continue
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    items.append(json.load(f))
            except (json.JSONDecodeError, KeyError, ValueError):
                continue  # Skip corrupted files
        return items

    def _load_org_index(self) -> Dict[str, str]:
        index = self._read(self._org_dir / "index.json")
        return index or {}

    def _save_org_index(self, index: Dict[str, str]) -> None:
        self._write(self._org_dir / "index.json", index)

    # --- Organizations ---

    def save_organization(self, organization: Organization) -> None:
        with self._lock:
            self._write(
                self._org_dir / f"{organization.id}.json", organization.to_dict()
            )
            index = self._load_org_index()
            index[organization.slug] = organization.id
            self._save_org_index(index)

    def get_organization(self, organization_id: str) -> Optional[Organization]:
        with self._lock:
            data = self._read(self._org_dir / f"{organization_id}.json")
            return Organization.from_dict(data) if data else None

    def get_organization_by_slug(self, slug: str) -> Optional[Organization]:
        with self._lock:
            organization_id = self._load_org_index().get(slug)
            return self.get_organization(organization_id) if organization_id else None

    def delete_organization(self, organization_id: str) -> bool:
        with self._lock:
            path = self._org_dir / f"{organization_id}.json"
            organization = self.get_organization(organization_id)
            if not organization:
                return False
            index = self._load_org_index()
            if organization.slug in index:
                del index[organization.slug]
                self._save_org_index(index)
            path.unlink()
            return True

    def list_organizations(self) -> List[Organization]:
        with self._lock:
            return [Organization.from_dict(d) for d in self._load_all(self._org_dir)]

    def org_slug_exists(self, slug: str) -> bool:
        with self._lock:
            return slug in self._load_org_index()

    # --- Members ---

    def save_member(self, member: Member) -> None:
        with self._lock:
            self._write(self._member_dir / f"{member.id}.json", member.to_dict())

    def get_member(self, member_id: str) -> Optional[Member]:
        with self._lock:
            data = self._read(self._member_dir / f"{member_id}.json")
            return Member.from_dict(data) if data else None

    def delete_member(self, member_id: str) -> bool:
        with self._lock:
            path = self._member_dir / f"{member_id}.json"
            if not path.exists():
                return False
            path.unlink()
            return True

    def list_members(self, organization_id: str) -> List[Member]:
        with self._lock:
            return [
                Member.from_dict(d)
                for d in self._load_all(self._member_dir)
                if d.get("organization_id") == organization_id
            ]

    # --- Memberships ---

    def save_membership(self, membership: Membership) -> None:
        with self._lock:
            self._write(
                self._membership_dir / f"{membership.id}.json", membership.to_dict()
            )

    def get_membership(self, membership_id: str) -> Optional[Membership]:
        with self._lock:
            data = self._read(self._membership_dir / f"{membership_id}.json")
            return Membership.from_dict(data) if data else None

    def get_membership_by_member(self, member_id: str) -> Optional[Membership]:
        with self._lock:
            for data in self._load_all(self._membership_dir):
                if data.get("member_id") == member_id:
                    return Membership.from_dict(data)
            return None

    def delete_membership(self, membership_id: str) -> bool:
        with self._lock:
            path = self._membership_dir / f"{membership_id}.json"
            if not path.exists():
                return False
            path.unlink()
            return True

    def list_memberships(self, organization_id: str) -> List[Membership]:
        with self._lock:
            return [
                Membership.from_dict(d)
                for d in self._load_all(self._membership_dir)
                if d.get("organization_id") == organization_id
            ]
