"""
Tests for Akitoi utility functions.
"""
import pytest

from akitoi.utils.validators import (
    validate_slug,
    validate_email,
    validate_url,
    validate_whatsapp,
    sanitize_slug,
    validate_hex_color,
)
from akitoi.utils.slug_generator import (
    generate_slug,
    generate_random_slug,
    generate_unique_slug,
    generate_short_code,
)


class TestValidators:
    """Tests for validation functions."""

    def test_validate_slug_valid(self):
        """Test validation of valid slugs."""
        assert validate_slug("johndoe") is True
        assert validate_slug("john-doe") is True
        assert validate_slug("john123") is True
        assert validate_slug("abc") is True

    def test_validate_slug_invalid(self):
        """Test validation of invalid slugs."""
        assert validate_slug("") is False
        assert validate_slug("ab") is False  # Too short
        assert validate_slug("John-Doe") is False  # Uppercase
        assert validate_slug("john_doe") is False  # Underscore
        assert validate_slug("john doe") is False  # Space
        assert validate_slug("-johndoe") is False  # Starts with hyphen
        assert validate_slug("johndoe-") is False  # Ends with hyphen

    def test_validate_email_valid(self):
        """Test validation of valid emails."""
        assert validate_email("test@example.com") is True
        assert validate_email("user.name@example.co.uk") is True
        assert validate_email("user+tag@example.com") is True

    def test_validate_email_invalid(self):
        """Test validation of invalid emails."""
        assert validate_email("") is False
        assert validate_email("notanemail") is False
        assert validate_email("@example.com") is False
        assert validate_email("user@") is False
        assert validate_email("user@domain") is False

    def test_validate_url_valid(self):
        """Test validation of valid URLs."""
        assert validate_url("https://example.com") is True
        assert validate_url("http://example.com/path") is True
        assert validate_url("https://example.com/path?query=1") is True

    def test_validate_url_invalid(self):
        """Test validation of invalid URLs."""
        assert validate_url("") is False
        assert validate_url("example.com") is False
        assert validate_url("ftp://example.com") is False

    def test_validate_whatsapp_valid(self):
        """Test validation of valid WhatsApp numbers."""
        assert validate_whatsapp("+34123456789") is True
        assert validate_whatsapp("+1234567890123") is True
        assert validate_whatsapp("+34 123 456 789") is True
        assert validate_whatsapp("+34-123-456-789") is True

    def test_validate_whatsapp_invalid(self):
        """Test validation of invalid WhatsApp numbers."""
        assert validate_whatsapp("") is False
        assert validate_whatsapp("123456789") is False  # No country code
        assert validate_whatsapp("+123") is False  # Too short

    def test_sanitize_slug(self):
        """Test slug sanitization."""
        assert sanitize_slug("John Doe") == "john-doe"
        assert sanitize_slug("Test@123!") == "test123"
        assert sanitize_slug("Hello   World") == "hello-world"
        assert sanitize_slug("---test---") == "test"
        assert sanitize_slug("Test--Name") == "test-name"

    def test_validate_hex_color_valid(self):
        """Test validation of valid hex colors."""
        assert validate_hex_color("#fff") is True
        assert validate_hex_color("#FFF") is True
        assert validate_hex_color("#ffffff") is True
        assert validate_hex_color("#FFFFFF") is True
        assert validate_hex_color("#123abc") is True

    def test_validate_hex_color_invalid(self):
        """Test validation of invalid hex colors."""
        assert validate_hex_color("") is False
        assert validate_hex_color("fff") is False
        assert validate_hex_color("#ff") is False
        assert validate_hex_color("#fffffff") is False
        assert validate_hex_color("#gggggg") is False


class TestSlugGenerator:
    """Tests for slug generation functions."""

    def test_generate_slug_basic(self):
        """Test basic slug generation."""
        assert generate_slug("John Doe") == "john-doe"
        assert generate_slug("Test Name 123") == "test-name-123"
        assert generate_slug("Hello_World") == "hello-world"

    def test_generate_slug_special_chars(self):
        """Test slug generation with special characters."""
        slug = generate_slug("Test@Name!")
        assert "@" not in slug
        assert "!" not in slug
        assert slug == "testname"

    def test_generate_slug_max_length(self):
        """Test slug generation with max length."""
        long_name = "a" * 100
        slug = generate_slug(long_name, max_length=20)
        assert len(slug) <= 20

    def test_generate_slug_empty_name(self):
        """Test slug generation with empty name."""
        slug = generate_slug("")
        assert len(slug) > 0  # Should generate random slug
        assert slug.islower()

    def test_generate_random_slug(self):
        """Test random slug generation."""
        slug = generate_random_slug(10)
        assert len(slug) == 10
        assert slug.isalnum()
        assert slug.islower()

    def test_generate_unique_slug(self):
        """Test unique slug generation."""
        existing = {"test", "test-1", "test-2"}

        def exists_check(s):
            return s in existing

        # Should generate test-3
        unique = generate_unique_slug("test", exists_check)
        assert unique == "test-3"
        assert unique not in existing

    def test_generate_unique_slug_no_conflict(self):
        """Test unique slug generation when base is available."""
        def exists_check(s):
            return False

        unique = generate_unique_slug("test", exists_check)
        assert unique == "test"

    def test_generate_short_code(self):
        """Test short code generation."""
        code = generate_short_code(6)
        assert len(code) == 6
        assert code.isalnum()
        assert code.islower()

        # Should not contain confusing characters
        assert "0" not in code
        assert "1" not in code
        assert "o" not in code
        assert "i" not in code
