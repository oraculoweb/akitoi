"""
Theme model for profile customization.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Theme:
    """
    Theme configuration for a profile.

    Attributes:
        primary_color: Primary brand color (hex format)
        background_color: Background color (hex format)
        text_color: Text color (hex format)
        button_style: Style of link buttons ('rounded', 'square', 'pill')
        font_family: Font family name
    """

    primary_color: str = "#007bff"
    background_color: str = "#ffffff"
    text_color: str = "#212529"
    button_style: str = "rounded"
    font_family: str = "Inter, system-ui, sans-serif"

    def __post_init__(self):
        """Validate theme configuration."""
        self._validate_color(self.primary_color, "primary_color")
        self._validate_color(self.background_color, "background_color")
        self._validate_color(self.text_color, "text_color")

        if self.button_style not in ["rounded", "square", "pill"]:
            raise ValueError(
                f"Invalid button_style: {self.button_style}. "
                "Must be 'rounded', 'square', or 'pill'"
            )

    @staticmethod
    def _validate_color(color: str, field_name: str) -> None:
        """Validate hex color format."""
        if not color.startswith("#") or len(color) not in [4, 7]:
            raise ValueError(
                f"Invalid {field_name}: {color}. "
                "Must be in hex format (#RGB or #RRGGBB)"
            )

    def to_dict(self) -> dict:
        """Convert theme to dictionary."""
        return {
            "primary_color": self.primary_color,
            "background_color": self.background_color,
            "text_color": self.text_color,
            "button_style": self.button_style,
            "font_family": self.font_family,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Theme":
        """Create theme from dictionary."""
        return cls(
            primary_color=data.get("primary_color", "#007bff"),
            background_color=data.get("background_color", "#ffffff"),
            text_color=data.get("text_color", "#212529"),
            button_style=data.get("button_style", "rounded"),
            font_family=data.get("font_family", "Inter, system-ui, sans-serif"),
        )
