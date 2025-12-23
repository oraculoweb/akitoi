"""
Tests for Akitoi data models.
"""
import pytest
from datetime import datetime

from akitoi.models.theme import Theme
from akitoi.models.link import Link, LinkType
from akitoi.models.profile import Profile


class TestTheme:
    """Tests for Theme model."""

    def test_create_theme_with_defaults(self):
        """Test creating theme with default values."""
        theme = Theme()

        assert theme.primary_color == "#007bff"
        assert theme.background_color == "#ffffff"
        assert theme.text_color == "#212529"
        assert theme.button_style == "rounded"

    def test_create_theme_with_custom_colors(self):
        """Test creating theme with custom colors."""
        theme = Theme(
            primary_color="#ff0000",
            background_color="#000000",
            text_color="#ffffff"
        )

        assert theme.primary_color == "#ff0000"
        assert theme.background_color == "#000000"
        assert theme.text_color == "#ffffff"

    def test_invalid_color_format(self):
        """Test that invalid color format raises error."""
        with pytest.raises(ValueError, match="Invalid primary_color"):
            Theme(primary_color="red")

        with pytest.raises(ValueError, match="Invalid background_color"):
            Theme(background_color="rgb(255,0,0)")

    def test_invalid_button_style(self):
        """Test that invalid button style raises error."""
        with pytest.raises(ValueError, match="Invalid button_style"):
            Theme(button_style="invalid")

    def test_theme_to_dict(self):
        """Test converting theme to dictionary."""
        theme = Theme(primary_color="#ff0000")
        data = theme.to_dict()

        assert data["primary_color"] == "#ff0000"
        assert "background_color" in data
        assert "button_style" in data

    def test_theme_from_dict(self):
        """Test creating theme from dictionary."""
        data = {
            "primary_color": "#ff0000",
            "background_color": "#000000",
            "button_style": "pill"
        }
        theme = Theme.from_dict(data)

        assert theme.primary_color == "#ff0000"
        assert theme.background_color == "#000000"
        assert theme.button_style == "pill"


class TestLink:
    """Tests for Link model."""

    def test_create_link_basic(self):
        """Test creating a basic link."""
        link = Link(
            title="My Website",
            url="https://example.com",
            link_type=LinkType.WEBSITE
        )

        assert link.title == "My Website"
        assert link.url == "https://example.com"
        assert link.link_type == LinkType.WEBSITE
        assert link.is_active is True
        assert link.clicks == 0

    def test_link_default_icon(self):
        """Test that links get default icons based on type."""
        whatsapp_link = Link(
            title="WhatsApp",
            url="+34123456789",
            link_type=LinkType.WHATSAPP
        )
        assert whatsapp_link.icon == "💬"

        email_link = Link(
            title="Email",
            url="test@example.com",
            link_type=LinkType.EMAIL
        )
        assert email_link.icon == "✉️"

    def test_increment_clicks(self):
        """Test incrementing click counter."""
        link = Link(title="Test", url="https://test.com")

        assert link.clicks == 0
        link.increment_clicks()
        assert link.clicks == 1
        link.increment_clicks()
        assert link.clicks == 2

    def test_link_to_dict(self):
        """Test converting link to dictionary."""
        link = Link(
            title="Test",
            url="https://test.com",
            link_type=LinkType.WEBSITE
        )
        data = link.to_dict()

        assert data["title"] == "Test"
        assert data["url"] == "https://test.com"
        assert data["link_type"] == "website"
        assert "created_at" in data

    def test_link_from_dict(self):
        """Test creating link from dictionary."""
        now = datetime.now()
        data = {
            "title": "Test",
            "url": "https://test.com",
            "link_type": "email",
            "clicks": 5,
            "created_at": now.isoformat()
        }
        link = Link.from_dict(data)

        assert link.title == "Test"
        assert link.url == "https://test.com"
        assert link.link_type == LinkType.EMAIL
        assert link.clicks == 5


class TestProfile:
    """Tests for Profile model."""

    def test_create_profile_basic(self):
        """Test creating a basic profile."""
        profile = Profile(
            name="John Doe",
            slug="johndoe",
            bio="Software Developer"
        )

        assert profile.name == "John Doe"
        assert profile.slug == "johndoe"
        assert profile.bio == "Software Developer"
        assert profile.is_published is False
        assert profile.views == 0
        assert len(profile.links) == 0

    def test_profile_requires_name_and_slug(self):
        """Test that profile requires name and slug."""
        with pytest.raises(ValueError):
            Profile(name="", slug="test")

        with pytest.raises(ValueError):
            Profile(name="Test", slug="")

    def test_add_link_to_profile(self):
        """Test adding links to profile."""
        profile = Profile(name="Test", slug="test")

        link1 = Link(title="Website", url="https://example.com")
        link2 = Link(title="Email", url="test@example.com")

        profile.add_link(link1)
        profile.add_link(link2)

        assert len(profile.links) == 2
        assert profile.links[0].position == 0
        assert profile.links[1].position == 1

    def test_remove_link_from_profile(self):
        """Test removing links from profile."""
        profile = Profile(name="Test", slug="test")

        link1 = Link(title="Link 1", url="https://example1.com")
        link2 = Link(title="Link 2", url="https://example2.com")
        link3 = Link(title="Link 3", url="https://example3.com")

        profile.add_link(link1)
        profile.add_link(link2)
        profile.add_link(link3)

        profile.remove_link(1)  # Remove link2

        assert len(profile.links) == 2
        assert profile.links[0].title == "Link 1"
        assert profile.links[1].title == "Link 3"
        assert profile.links[1].position == 1  # Positions reordered

    def test_get_active_links(self):
        """Test getting only active links."""
        profile = Profile(name="Test", slug="test")

        link1 = Link(title="Active", url="https://active.com", is_active=True)
        link2 = Link(title="Inactive", url="https://inactive.com", is_active=False)

        profile.add_link(link1)
        profile.add_link(link2)

        active_links = profile.get_active_links()

        assert len(active_links) == 1
        assert active_links[0].title == "Active"

    def test_increment_views(self):
        """Test incrementing profile views."""
        profile = Profile(name="Test", slug="test")

        assert profile.views == 0
        profile.increment_views()
        assert profile.views == 1
        profile.increment_views()
        assert profile.views == 2

    def test_get_total_clicks(self):
        """Test getting total clicks across all links."""
        profile = Profile(name="Test", slug="test")

        link1 = Link(title="Link 1", url="https://example1.com")
        link2 = Link(title="Link 2", url="https://example2.com")

        link1.increment_clicks()
        link1.increment_clicks()
        link2.increment_clicks()

        profile.add_link(link1)
        profile.add_link(link2)

        assert profile.get_total_clicks() == 3

    def test_publish_unpublish(self):
        """Test publishing and unpublishing profile."""
        profile = Profile(name="Test", slug="test")

        assert profile.is_published is False

        profile.publish()
        assert profile.is_published is True

        profile.unpublish()
        assert profile.is_published is False

    def test_update_theme(self):
        """Test updating profile theme."""
        profile = Profile(name="Test", slug="test")

        new_theme = Theme(primary_color="#ff0000")
        profile.update_theme(new_theme)

        assert profile.theme.primary_color == "#ff0000"

    def test_profile_to_dict(self):
        """Test converting profile to dictionary."""
        profile = Profile(
            name="Test",
            slug="test",
            bio="Test bio"
        )

        link = Link(title="Website", url="https://example.com")
        profile.add_link(link)

        data = profile.to_dict()

        assert data["name"] == "Test"
        assert data["slug"] == "test"
        assert data["bio"] == "Test bio"
        assert len(data["links"]) == 1
        assert "theme" in data
        assert "created_at" in data

    def test_profile_from_dict(self):
        """Test creating profile from dictionary."""
        data = {
            "slug": "test",
            "name": "Test User",
            "bio": "Test bio",
            "links": [
                {
                    "title": "Website",
                    "url": "https://example.com",
                    "link_type": "website",
                    "created_at": datetime.now().isoformat()
                }
            ],
            "theme": {
                "primary_color": "#ff0000"
            },
            "views": 10,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        profile = Profile.from_dict(data)

        assert profile.name == "Test User"
        assert profile.slug == "test"
        assert profile.bio == "Test bio"
        assert len(profile.links) == 1
        assert profile.theme.primary_color == "#ff0000"
        assert profile.views == 10
