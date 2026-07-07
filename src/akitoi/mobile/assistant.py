"""
Contact assistant — an intermediary between visitors and the profile
owner.

Instead of exposing the owner's phone/email directly, a visitor
leaves a message with the assistant. The assistant stores the request
and produces "handoff" deep links (prefilled WhatsApp / email) that
the owner can use to reply from their own device. This keeps private
channels private and creates a natural place to plug in an AI agent
later (auto-replies, screening, scheduling).
"""
import json
import re
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from urllib.parse import quote

from ..models.profile import Profile
from ..models.link import LinkType

MESSAGE_MAX_LENGTH = 500
NAME_MAX_LENGTH = 80
CONTACT_MAX_LENGTH = 120


@dataclass
class ContactRequest:
    """A message a visitor left for a profile owner."""

    profile_slug: str
    sender_name: str
    sender_contact: str
    message: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "ContactRequest":
        return cls(
            profile_slug=data["profile_slug"],
            sender_name=data["sender_name"],
            sender_contact=data["sender_contact"],
            message=data["message"],
            id=data.get("id", str(uuid.uuid4())),
            status=data.get("status", "pending"),
            created_at=datetime.fromisoformat(data["created_at"])
            if "created_at" in data
            else datetime.now(),
        )


class ContactAssistant:
    """Receives, stores and hands off contact requests."""

    def __init__(self, storage_dir: str = ".akitoi_data/contact_requests"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def receive_request(
        self,
        profile: Profile,
        sender_name: str,
        sender_contact: str,
        message: str,
    ) -> ContactRequest:
        """
        Validate and store a visitor's contact request.

        Raises:
            ValueError: On empty or oversized fields
        """
        sender_name = sender_name.strip()
        sender_contact = sender_contact.strip()
        message = message.strip()

        if not sender_name or not sender_contact or not message:
            raise ValueError("Name, contact and message are required")
        if len(sender_name) > NAME_MAX_LENGTH:
            raise ValueError(f"Name too long (max {NAME_MAX_LENGTH})")
        if len(sender_contact) > CONTACT_MAX_LENGTH:
            raise ValueError(f"Contact too long (max {CONTACT_MAX_LENGTH})")
        if len(message) > MESSAGE_MAX_LENGTH:
            raise ValueError(f"Message too long (max {MESSAGE_MAX_LENGTH})")

        request = ContactRequest(
            profile_slug=profile.slug,
            sender_name=sender_name,
            sender_contact=sender_contact,
            message=message,
        )
        self._save(request)
        return request

    def list_requests(self, slug: str) -> List[ContactRequest]:
        """List stored requests for a profile, oldest first."""
        requests = []
        for path in sorted(self.storage_dir.glob(f"{slug}--*.json")):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    requests.append(ContactRequest.from_dict(json.load(f)))
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
        return sorted(requests, key=lambda r: r.created_at)

    def build_handoff(self, profile: Profile, request: ContactRequest) -> dict:
        """
        Build prefilled reply links for the owner's private channels.

        The owner replies from their own WhatsApp/email; the visitor
        never sees those channels unless the owner chooses to answer.
        """
        intro = (
            f"Hola {request.sender_name}, soy {profile.name}. "
            f"Recibí tu mensaje vía Akitoi: \"{request.message}\""
        )
        handoff: dict = {"request_id": request.id, "channels": {}}

        for link in profile.get_active_links():
            if link.link_type == LinkType.WHATSAPP and _looks_like_phone(request.sender_contact):
                phone = re.sub(r"[^\d]", "", request.sender_contact)
                handoff["channels"]["whatsapp"] = (
                    f"https://wa.me/{phone}?text={quote(intro)}"
                )
            elif link.link_type == LinkType.EMAIL and "@" in request.sender_contact:
                subject = quote(f"Re: tu mensaje a {profile.name} (Akitoi)")
                handoff["channels"]["email"] = (
                    f"mailto:{request.sender_contact}?subject={subject}&body={quote(intro)}"
                )
        return handoff

    def _save(self, request: ContactRequest) -> None:
        path = self.storage_dir / f"{request.profile_slug}--{request.id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(request.to_dict(), f, indent=2, ensure_ascii=False)


def _looks_like_phone(value: str) -> bool:
    return bool(re.fullmatch(r"\+?[\d\s\-()]{7,20}", value.strip()))
