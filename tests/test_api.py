"""
Tests for Akitoi convenience API.
"""
import pytest
import tempfile
import shutil

import akitoi
from akitoi import create_profile, get_profile, Link, LinkType


class TestConvenienceAPI:
    """Tests for convenience API functions."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test."""
        # Setup: Create temp storage
        temp_dir = tempfile.mkdtemp()

        # Replace default manager with test manager
        from akitoi.storage.json_storage import JSONStorage
        from akitoi.core.profile_manager import ProfileManager
        storage = JSONStorage(temp_dir)
        akitoi._default_manager = ProfileManager(storage)

        yield

        # Teardown: Clean up
        shutil.rmtree(temp_dir)
        akitoi._default_manager = None

    def test_create_profile_convenience(self):
        """Test creating profile with convenience function."""
        profile = create_profile(
            name="John Doe",
            slug="johndoe",
            bio="Software Developer"
        )

        assert profile.name == "John Doe"
        assert profile.slug == "johndoe"
        assert profile.bio == "Software Developer"

    def test_get_profile_convenience(self):
        """Test getting profile with convenience function."""
        created = create_profile(name="Test", slug="test")

        retrieved = get_profile("test")

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.slug == "test"

    def test_complete_workflow(self):
        """Test complete workflow using convenience API."""
        # Create profile
        profile = create_profile(
            name="Jane Doe",
            bio="Product Manager"
        )

        # Add links
        manager = akitoi._get_manager()

        whatsapp = Link(
            title="WhatsApp",
            url="+34123456789",
            link_type=LinkType.WHATSAPP
        )
        manager.add_link(profile.id, whatsapp)

        email = Link(
            title="Email",
            url="jane@example.com",
            link_type=LinkType.EMAIL
        )
        manager.add_link(profile.id, email)

        website = Link(
            title="Portfolio",
            url="https://janedoe.com",
            link_type=LinkType.WEBSITE
        )
        manager.add_link(profile.id, website)

        # Retrieve and verify
        retrieved = get_profile(profile.slug)

        assert retrieved is not None
        assert len(retrieved.links) == 3
        assert retrieved.links[0].link_type == LinkType.WHATSAPP
        assert retrieved.links[1].link_type == LinkType.EMAIL
        assert retrieved.links[2].link_type == LinkType.WEBSITE
