"""
Tests for ProfileManager core logic.
"""
import pytest
import tempfile
import shutil
from pathlib import Path

from akitoi import ProfileManager, Link, LinkType, Theme


class TestProfileManager:
    """Tests for ProfileManager."""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def manager(self, temp_storage):
        """Create ProfileManager with temporary storage."""
        from akitoi.storage.json_storage import JSONStorage
        storage = JSONStorage(temp_storage)
        return ProfileManager(storage)

    def test_create_profile_basic(self, manager):
        """Test creating a basic profile."""
        profile = manager.create_profile(
            name="John Doe",
            slug="johndoe",
            bio="Software Developer"
        )

        assert profile.name == "John Doe"
        assert profile.slug == "johndoe"
        assert profile.bio == "Software Developer"
        assert profile.id is not None

    def test_create_profile_auto_slug(self, manager):
        """Test creating profile with auto-generated slug."""
        profile = manager.create_profile(
            name="John Doe",
            bio="Developer"
        )

        assert profile.slug == "john-doe"

    def test_create_profile_duplicate_slug(self, manager):
        """Test that duplicate slugs are rejected."""
        manager.create_profile(name="John", slug="test")

        with pytest.raises(ValueError, match="already exists"):
            manager.create_profile(name="Jane", slug="test")

    def test_create_profile_invalid_slug(self, manager):
        """Test that invalid slugs are rejected."""
        # Slug with only special characters will sanitize to empty/invalid
        with pytest.raises(ValueError, match="Invalid slug"):
            manager.create_profile(name="John", slug="!!!")

    def test_get_profile(self, manager):
        """Test retrieving a profile by ID."""
        created = manager.create_profile(name="Test", slug="test")

        retrieved = manager.get_profile(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.slug == "test"

    def test_get_profile_by_slug(self, manager):
        """Test retrieving a profile by slug."""
        created = manager.create_profile(name="Test", slug="test")

        retrieved = manager.get_profile_by_slug("test")

        assert retrieved is not None
        assert retrieved.slug == "test"
        assert retrieved.name == "Test"

    def test_get_nonexistent_profile(self, manager):
        """Test retrieving non-existent profile."""
        profile = manager.get_profile("nonexistent-id")
        assert profile is None

        profile = manager.get_profile_by_slug("nonexistent")
        assert profile is None

    def test_update_profile(self, manager):
        """Test updating profile information."""
        profile = manager.create_profile(name="Test", slug="test")

        updated = manager.update_profile(
            profile.id,
            name="Updated Name",
            bio="Updated bio"
        )

        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.bio == "Updated bio"

    def test_update_theme(self, manager):
        """Test updating profile theme."""
        profile = manager.create_profile(name="Test", slug="test")

        new_theme = Theme(primary_color="#ff0000")
        updated = manager.update_theme(profile.id, new_theme)

        assert updated is not None
        assert updated.theme.primary_color == "#ff0000"

    def test_delete_profile(self, manager):
        """Test deleting a profile."""
        profile = manager.create_profile(name="Test", slug="test")

        result = manager.delete_profile(profile.id)
        assert result is True

        # Profile should no longer exist
        retrieved = manager.get_profile(profile.id)
        assert retrieved is None

    def test_delete_nonexistent_profile(self, manager):
        """Test deleting non-existent profile."""
        result = manager.delete_profile("nonexistent")
        assert result is False

    def test_list_profiles(self, manager):
        """Test listing all profiles."""
        manager.create_profile(name="Profile 1", slug="profile1")
        manager.create_profile(name="Profile 2", slug="profile2")
        manager.create_profile(name="Profile 3", slug="profile3")

        profiles = manager.list_profiles()

        assert len(profiles) == 3
        slugs = [p.slug for p in profiles]
        assert "profile1" in slugs
        assert "profile2" in slugs
        assert "profile3" in slugs

    def test_publish_unpublish(self, manager):
        """Test publishing and unpublishing profile."""
        profile = manager.create_profile(name="Test", slug="test")

        assert profile.is_published is False

        # Publish
        updated = manager.publish_profile(profile.id)
        assert updated.is_published is True

        # Unpublish
        updated = manager.unpublish_profile(profile.id)
        assert updated.is_published is False

    def test_add_link(self, manager):
        """Test adding a link to profile."""
        profile = manager.create_profile(name="Test", slug="test")

        link = Link(
            title="Website",
            url="https://example.com",
            link_type=LinkType.WEBSITE
        )

        updated = manager.add_link(profile.id, link)

        assert updated is not None
        assert len(updated.links) == 1
        assert updated.links[0].title == "Website"

    def test_remove_link(self, manager):
        """Test removing a link from profile."""
        profile = manager.create_profile(name="Test", slug="test")

        link1 = Link(title="Link 1", url="https://example1.com")
        link2 = Link(title="Link 2", url="https://example2.com")

        manager.add_link(profile.id, link1)
        manager.add_link(profile.id, link2)

        updated = manager.remove_link(profile.id, 0)

        assert updated is not None
        assert len(updated.links) == 1
        assert updated.links[0].title == "Link 2"

    def test_record_view(self, manager):
        """Test recording profile view."""
        profile = manager.create_profile(name="Test", slug="test")

        assert profile.views == 0

        updated = manager.record_view("test")
        assert updated.views == 1

        updated = manager.record_view("test")
        assert updated.views == 2

    def test_record_link_click(self, manager):
        """Test recording link click."""
        profile = manager.create_profile(name="Test", slug="test")

        link = Link(title="Website", url="https://example.com")
        manager.add_link(profile.id, link)

        updated = manager.record_link_click("test", 0)

        assert updated is not None
        assert updated.links[0].clicks == 1

    def test_record_link_click_invalid_index(self, manager):
        """Test recording click on non-existent link."""
        profile = manager.create_profile(name="Test", slug="test")

        updated = manager.record_link_click("test", 99)
        assert updated is None

    def test_persistence(self, manager):
        """Test that data persists across manager instances."""
        # Create profile
        profile = manager.create_profile(name="Test", slug="test")
        profile_id = profile.id

        # Create new manager instance with same storage
        from akitoi.storage.json_storage import JSONStorage
        storage = JSONStorage(manager.storage.storage_path)
        new_manager = ProfileManager(storage)

        # Retrieve profile
        retrieved = new_manager.get_profile(profile_id)

        assert retrieved is not None
        assert retrieved.id == profile_id
        assert retrieved.slug == "test"
