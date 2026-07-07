"""
Tests for the mobile layer: ContactCard, vCard, QR, NFC, assistant
and the public mobile API endpoints.
"""
import shutil
import tempfile

import pytest

from akitoi import ProfileManager, Link, LinkType
from akitoi.storage.json_storage import JSONStorage
from akitoi.mobile.contact_card import build_contact_card
from akitoi.mobile.vcard import contact_card_to_vcard
from akitoi.mobile.qr import qr_svg, qr_png, wallpaper_png
from akitoi.mobile.nfc import encode_uri_payload, profile_ndef
from akitoi.mobile.assistant import ContactAssistant


@pytest.fixture
def temp_dir():
    path = tempfile.mkdtemp()
    yield path
    shutil.rmtree(path)


@pytest.fixture
def manager(temp_dir):
    return ProfileManager(JSONStorage(f"{temp_dir}/profiles"))


@pytest.fixture
def profile(manager):
    profile = manager.create_profile(
        name="Juan Tello",
        slug="juan-tello",
        bio="Consultor de tecnología. " * 20,  # long bio -> summary truncated
        profile_image_url="https://example.com/juan.jpg",
    )
    manager.add_link(profile.id, Link(
        title="WhatsApp", url="+51987654321", link_type=LinkType.WHATSAPP))
    manager.add_link(profile.id, Link(
        title="Email", url="juan@example.com", link_type=LinkType.EMAIL))
    manager.add_link(profile.id, Link(
        title="Web", url="https://juantello.com", link_type=LinkType.WEBSITE))
    manager.add_link(profile.id, Link(
        title="LinkedIn", url="https://linkedin.com/in/juantello",
        link_type=LinkType.LINKEDIN))
    manager.add_link(profile.id, Link(
        title="Privado", url="https://secreto.example.com",
        link_type=LinkType.CUSTOM, is_active=False))
    manager.publish_profile(profile.id)
    return manager.get_profile_by_slug("juan-tello")


class TestContactCard:
    def test_basic_fields_extracted(self, profile):
        card = build_contact_card(profile, "https://akitoi.bio")

        assert card.name == "Juan Tello"
        assert card.phone == "+51987654321"
        assert card.email == "juan@example.com"
        assert card.website == "https://juantello.com"
        assert card.socials["linkedin"] == "https://linkedin.com/in/juantello"
        assert card.profile_url == "https://akitoi.bio/juan-tello"

    def test_summary_is_truncated(self, profile):
        card = build_contact_card(profile)
        assert len(card.summary) <= 160
        assert card.summary.endswith("…")

    def test_inactive_links_never_exposed(self, profile):
        card = build_contact_card(profile)
        assert "secreto" not in str(card.to_dict())

    def test_no_analytics_in_public_dict(self, profile):
        data = build_contact_card(profile).to_dict()
        assert "views" not in data
        assert "clicks" not in data
        assert "id" not in data


class TestVCard:
    def test_vcard_structure(self, profile):
        card = build_contact_card(profile, "https://akitoi.bio")
        vcard = contact_card_to_vcard(card)

        assert vcard.startswith("BEGIN:VCARD\r\nVERSION:3.0")
        assert vcard.rstrip().endswith("END:VCARD")
        assert "FN:Juan Tello" in vcard
        assert "TEL;TYPE=CELL:+51987654321" in vcard
        assert "EMAIL;TYPE=INTERNET:juan@example.com" in vcard
        assert "URL:https://juantello.com" in vcard
        assert "PHOTO;VALUE=URI:https://example.com/juan.jpg" in vcard

    def test_vcard_escaping(self, profile):
        card = build_contact_card(profile)
        card.summary = "Ventas; consultoría, y\nmás"
        vcard = contact_card_to_vcard(card)
        assert "NOTE:Ventas\\; consultoría\\, y\\nmás" in vcard


class TestQR:
    def test_svg_generation(self):
        svg = qr_svg("https://akitoi.bio/juan-tello", dark="#6366f1")
        assert "<svg" in svg
        assert "6366f1" in svg.lower()

    def test_png_generation(self):
        png = qr_png("https://akitoi.bio/juan-tello")
        assert png[:8] == b"\x89PNG\r\n\x1a\n"

    def test_wallpaper_is_bigger_than_regular_png(self):
        data = "https://akitoi.bio/juan-tello"
        assert len(wallpaper_png(data)) > len(qr_png(data))


class TestNFC:
    def test_uri_payload_uses_prefix_abbreviation(self):
        payload = encode_uri_payload("https://akitoi.bio/juan")
        assert payload[0] == 0x04  # "https://" prefix code
        assert payload[1:] == b"akitoi.bio/juan"

    def test_single_record_message_flags(self):
        message = profile_ndef("https://akitoi.bio/juan")
        # MB(0x80) | ME(0x40) | SR(0x10) | TNF well-known(0x01) = 0xD1
        assert message[0] == 0xD1
        assert message[2:4] == bytes([len("akitoi.bio/juan") + 1, ord("U")])

    def test_message_with_vcard_record(self):
        vcard = "BEGIN:VCARD\r\nVERSION:3.0\r\nFN:Juan\r\nEND:VCARD\r\n"
        message = profile_ndef("https://akitoi.bio/juan", vcard)
        # First record: MB only (0x91 = MB|SR|well-known)
        assert message[0] == 0x91
        assert b"text/vcard" in message
        assert b"FN:Juan" in message


class TestAssistant:
    def test_receive_and_list(self, profile, temp_dir):
        assistant = ContactAssistant(f"{temp_dir}/requests")
        request = assistant.receive_request(
            profile, "Ana", "+51911222333", "Quiero una cotización")

        stored = assistant.list_requests("juan-tello")
        assert len(stored) == 1
        assert stored[0].id == request.id
        assert stored[0].message == "Quiero una cotización"

    def test_rejects_empty_and_oversized(self, profile, temp_dir):
        assistant = ContactAssistant(f"{temp_dir}/requests")
        with pytest.raises(ValueError):
            assistant.receive_request(profile, "", "a@b.com", "hola")
        with pytest.raises(ValueError):
            assistant.receive_request(profile, "Ana", "a@b.com", "x" * 501)

    def test_handoff_builds_prefilled_links(self, profile, temp_dir):
        assistant = ContactAssistant(f"{temp_dir}/requests")
        request = assistant.receive_request(
            profile, "Ana", "+51911222333", "Hola Juan")
        handoff = assistant.build_handoff(profile, request)
        assert handoff["channels"]["whatsapp"].startswith(
            "https://wa.me/51911222333?text=")


class TestMobileAPI:
    @pytest.fixture
    def client(self, manager, profile, temp_dir):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from akitoi.api.routes.mobile import create_mobile_router

        app = FastAPI()
        app.include_router(create_mobile_router(
            manager,
            base_url="https://akitoi.bio",
            assistant=ContactAssistant(f"{temp_dir}/requests"),
        ))
        return TestClient(app)

    def test_page_renders_public_data(self, client):
        response = client.get("/m/juan-tello")
        assert response.status_code == 200
        assert "Juan Tello" in response.text
        assert "Guardar contacto" in response.text
        assert "secreto" not in response.text  # inactive link hidden

    def test_page_records_view(self, client, manager):
        client.get("/m/juan-tello")
        assert manager.get_profile_by_slug("juan-tello").views == 1

    def test_unpublished_profile_is_404(self, client, manager):
        hidden = manager.create_profile(name="Oculto", slug="oculto")
        response = client.get(f"/m/{hidden.slug}")
        assert response.status_code == 404

    def test_vcard_download(self, client):
        response = client.get("/m/juan-tello/vcard")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/vcard")
        assert "attachment" in response.headers["content-disposition"]
        assert "BEGIN:VCARD" in response.text

    def test_public_card_json(self, client):
        data = client.get("/m/juan-tello/card").json()
        assert data["phone"] == "+51987654321"
        assert "views" not in data

    def test_qr_svg_url_and_vcard_modes(self, client):
        assert "<svg" in client.get("/m/juan-tello/qr.svg").text
        assert "<svg" in client.get("/m/juan-tello/qr.svg?content=vcard").text

    def test_wallpaper_png(self, client):
        response = client.get("/m/juan-tello/wallpaper.png")
        assert response.status_code == 200
        assert response.content[:8] == b"\x89PNG\r\n\x1a\n"

    def test_nfc_payload(self, client):
        data = client.get("/m/juan-tello/nfc").json()
        assert data["records"] == ["uri", "vcard"]
        message = bytes.fromhex(data["ndef_hex"])
        assert message[0] == 0x91  # MB flag on first record

    def test_assistant_endpoint(self, client):
        response = client.post("/m/juan-tello/contact", json={
            "sender_name": "Ana",
            "sender_contact": "ana@example.com",
            "message": "Hola, me interesa tu servicio",
        })
        assert response.status_code == 201
        assert response.json()["status"] == "received"

    def test_assistant_honeypot_silently_drops(self, client, temp_dir):
        response = client.post("/m/juan-tello/contact", json={
            "sender_name": "Bot",
            "sender_contact": "bot@spam.com",
            "message": "spam",
            "company": "SpamCorp",
        })
        assert response.status_code == 201
        assert "request_id" not in response.json()
