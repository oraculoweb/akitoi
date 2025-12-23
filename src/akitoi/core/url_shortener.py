"""
URL shortening and QR code generation for Akitoi platform.
"""
from typing import Optional
from urllib.parse import urljoin

from ..utils.slug_generator import generate_short_code


class URLShortener:
    """
    Handles URL shortening and QR code generation for profiles.
    """

    def __init__(self, base_url: str = "https://akitoi.bio"):
        """
        Initialize URL shortener.

        Args:
            base_url: Base URL for the platform (e.g., "https://akitoi.bio")
        """
        self.base_url = base_url.rstrip("/")

    def get_profile_url(self, slug: str) -> str:
        """
        Get the full URL for a profile.

        Args:
            slug: Profile slug

        Returns:
            Full profile URL
        """
        return f"{self.base_url}/{slug}"

    def get_short_url(self, slug: str, custom_code: Optional[str] = None) -> str:
        """
        Get a short URL for a profile.

        Args:
            slug: Profile slug
            custom_code: Optional custom short code

        Returns:
            Short URL
        """
        code = custom_code or generate_short_code()
        return f"{self.base_url}/s/{code}"

    def generate_qr_data(self, slug: str) -> str:
        """
        Generate QR code data (URL) for a profile.

        Args:
            slug: Profile slug

        Returns:
            URL to encode in QR code
        """
        return self.get_profile_url(slug)

    def generate_qr_code_svg(self, slug: str) -> str:
        """
        Generate a simple SVG QR code placeholder.

        Note: In production, this would integrate with a QR code library
        like qrcode or segno. For MVP, returns SVG placeholder.

        Args:
            slug: Profile slug

        Returns:
            SVG QR code as string
        """
        url = self.get_profile_url(slug)

        # Simple placeholder SVG
        # In production, use a proper QR code library
        svg = f"""
        <svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
            <rect width="200" height="200" fill="white"/>
            <text x="100" y="100" text-anchor="middle" font-family="monospace" font-size="10">
                QR Code
            </text>
            <text x="100" y="115" text-anchor="middle" font-family="monospace" font-size="8">
                {slug}
            </text>
            <text x="100" y="180" text-anchor="middle" font-family="sans-serif" font-size="8">
                Scan to visit profile
            </text>
        </svg>
        """

        return svg.strip()

    @staticmethod
    def create_whatsapp_url(phone: str, message: str = "") -> str:
        """
        Create a WhatsApp click-to-chat URL.

        Args:
            phone: Phone number with country code (e.g., +34123456789)
            message: Pre-filled message (optional)

        Returns:
            WhatsApp URL
        """
        # Remove + and other characters
        clean_phone = phone.replace("+", "").replace(" ", "").replace("-", "")

        if message:
            from urllib.parse import quote
            message = quote(message)
            return f"https://wa.me/{clean_phone}?text={message}"

        return f"https://wa.me/{clean_phone}"

    @staticmethod
    def create_email_url(email: str, subject: str = "", body: str = "") -> str:
        """
        Create a mailto URL.

        Args:
            email: Email address
            subject: Email subject (optional)
            body: Email body (optional)

        Returns:
            Mailto URL
        """
        from urllib.parse import quote

        params = []
        if subject:
            params.append(f"subject={quote(subject)}")
        if body:
            params.append(f"body={quote(body)}")

        if params:
            return f"mailto:{email}?{'&'.join(params)}"

        return f"mailto:{email}"
