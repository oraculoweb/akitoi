"""
Real QR code generation using segno (pure Python, no native deps).

Two payload modes:
- "url": QR points to the hub page (small, always up to date)
- "vcard": QR embeds the full vCard, so scanning adds the contact to
  the phone's address book even OFFLINE — ideal for the lock-screen
  wallpaper use case.
"""
import io

import segno


def make_qr(data: str) -> "segno.QRCode":
    """Build a QR code with medium error correction."""
    return segno.make(data, error="m")


def qr_svg(data: str, dark: str = "#000000", light: str = None, scale: int = 4) -> str:
    """
    Render a QR code as an SVG string (theme-aware colors).

    Args:
        data: Payload (URL or vCard text)
        dark: Module color (hex)
        light: Background color (hex) or None for transparent
        scale: Module scale factor

    Returns:
        SVG markup as a string
    """
    buffer = io.BytesIO()
    make_qr(data).save(
        buffer, kind="svg", dark=dark, light=light, scale=scale, xmldecl=False
    )
    return buffer.getvalue().decode("utf-8")


def qr_png(data: str, dark: str = "#000000", light: str = "#ffffff", scale: int = 8) -> bytes:
    """Render a QR code as PNG bytes."""
    buffer = io.BytesIO()
    make_qr(data).save(buffer, kind="png", dark=dark, light=light, scale=scale)
    return buffer.getvalue()


def wallpaper_png(
    data: str,
    dark: str = "#000000",
    light: str = "#ffffff",
    scale: int = 14,
    border: int = 10,
) -> bytes:
    """
    High-resolution QR PNG intended for a phone lock-screen wallpaper.

    A wide quiet zone (border) keeps the code scannable when placed
    over wallpaper art, and the large scale keeps modules crisp on
    high-DPI screens.
    """
    buffer = io.BytesIO()
    make_qr(data).save(
        buffer, kind="png", dark=dark, light=light, scale=scale, border=border
    )
    return buffer.getvalue()
