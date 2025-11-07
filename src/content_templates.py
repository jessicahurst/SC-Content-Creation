"""Utilities for generating branded social media content and images.

This module produces post templates for Sales Consultants that follow
Pulte's brand guidelines and provides helper functions to overlay
branding on consultant-supplied imagery.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from PIL import Image, ImageDraw, ImageFont


# --- Brand configuration ----------------------------------------------------
BRAND_COLORS: Dict[str, str] = {
    "primary": "#00334C",
    "accent_gold": "#F2C75C",
    "white": "#FFFFFF",
}

LOGO_PLACEHOLDER = "[LOGO_TOP_RIGHT]"
COLOR_PLACEHOLDER = (
    "[BACKGROUND: #00334C | ACCENTS: #F2C75C, #FFFFFF]"
)

FONT_FALLBACK = "arial.ttf"


@dataclass(frozen=True)
class PostTemplate:
    """Structure for a platform-specific social post template."""

    platform: str
    hook: str
    value: str
    call_to_action: str

    def to_markdown(self) -> str:
        """Render the template as a Markdown snippet."""
        return (
            f"### {self.platform}\n"
            f"{LOGO_PLACEHOLDER} {COLOR_PLACEHOLDER}\n\n"
            f"**Hook:** {self.hook}\n\n"
            f"**Value:** {self.value}\n\n"
            f"**Call to Action:** {self.call_to_action}\n"
        )


def build_base_templates() -> List[PostTemplate]:
    """Create post templates for each platform with customization cues."""

    # Sales Consultants may personalize the bracketed segments below.
    customizable_insert = (
        "[Insert community highlight, event, home feature, or promotion details here]"
    )

    return [
        PostTemplate(
            platform="LinkedIn",
            hook="Empower your next move with insights from a trusted partner.",
            value=(
                "Let's explore how the Pulte community can support your goals. "
                f"{customizable_insert}"
            ),
            call_to_action="Schedule a consultation to discover your best-fit home journey today.",
        ),
        PostTemplate(
            platform="Facebook",
            hook="Step into comfort, style, and a community built around you!",
            value=(
                "I'm here to guide you through every question and opportunity. "
                f"{customizable_insert}"
            ),
            call_to_action="Message me to plan your visit or book an appointment at the model home.",
        ),
        PostTemplate(
            platform="Instagram",
            hook="Picture your life in a space designed for connection and growth.",
            value=(
                "Swipe for a closer look or reach out for curated tours—" f"{customizable_insert}"
            ),
            call_to_action="Tap the link in bio to reserve your personalized community tour.",
        ),
        PostTemplate(
            platform="Builder to Realtor",
            hook="Partner with a consultant who understands your buyers' dreams.",
            value=(
                "Share the vision, and I'll provide tailored solutions backed by Pulte's "
                "expertise. " f"{customizable_insert}"
            ),
            call_to_action="Contact me for co-branded materials or to set a joint client meeting.",
        ),
    ]


def generate_markdown_templates() -> str:
    """Return all post templates formatted as Markdown."""
    templates = build_base_templates()
    header = (
        "# Pulte Social Content Templates\n\n"
        "*Voice:* Friendly, Approachable, Knowledgeable, Empowering, always Professional "
        "and Positive.\n\n"
        "Each template includes an engaging hook, informative details, and a clear call to "
        "action. Customize the bracketed sections with your community-specific message.\n\n"
    )

    return header + "\n".join(template.to_markdown() for template in templates)


# --- Image branding utilities -----------------------------------------------

def validate_image_path(image_path: Path) -> Path:
    """Ensure the provided image path exists and uses an approved format."""
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    if image_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
        raise ValueError("Unsupported image format. Use JPG or PNG.")

    return image_path


def _load_font(font_size: int) -> ImageFont.FreeTypeFont:
    """Load a font, falling back to a default Pillow font if unavailable."""
    try:
        return ImageFont.truetype(FONT_FALLBACK, font_size)
    except OSError:
        return ImageFont.load_default()


def generate_branded_image(
    image_path: Path,
    output_path: Path,
    message_text: str,
    logo_path: Path | None = None,
) -> Path:
    """Apply brand styling to an uploaded image and save the result.

    Parameters
    ----------
    image_path:
        Path to the consultant's source photo (JPG or PNG).
    output_path:
        Location where the branded image will be stored.
    message_text:
        Sales message text to overlay. Keep concise for readability.
    logo_path:
        Optional path to the approved logo. When not provided, a placeholder
        badge is rendered in the top-right corner.

    Returns
    -------
    Path
        The path to the saved, branded image.
    """

    image_path = validate_image_path(image_path)
    with Image.open(image_path).convert("RGBA") as base_image:
        width, height = base_image.size

        overlay = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Apply a subtle border using the primary brand color.
        border_thickness = max(8, width // 60)
        draw.rectangle(
            [(0, 0), (width - 1, height - 1)],
            outline=BRAND_COLORS["primary"],
            width=border_thickness,
        )

        # Add a bottom banner for text using the primary color with slight opacity.
        banner_height = max(int(height * 0.22), 120)
        banner_top = height - banner_height
        draw.rectangle(
            [(0, banner_top), (width, height)],
            fill=(0, 51, 76, 210),  # Semi-transparent version of primary color.
        )

        # Prepare text wrapping for clarity.
        padding = border_thickness * 2
        font = _load_font(font_size=max(24, width // 28))
        text_color = BRAND_COLORS["white"]
        wrapped_text = _wrap_text(draw, message_text, font, width - padding * 2)

        draw.multiline_text(
            (padding, banner_top + padding // 2),
            wrapped_text,
            font=font,
            fill=text_color,
            spacing=4,
        )

        # Insert the logo or a placeholder badge in the top-right corner.
        _apply_logo_or_placeholder(overlay, logo_path, width, border_thickness)

        branded = Image.alpha_composite(base_image, overlay)
        branded = branded.convert("RGB")
        branded.save(output_path)
        return output_path


def _apply_logo_or_placeholder(
    overlay: Image.Image,
    logo_path: Path | None,
    width: int,
    border_thickness: int,
) -> None:
    """Place the provided logo or a placeholder block in the top-right corner."""
    padding = border_thickness * 2
    max_logo_width = width // 5

    if logo_path:
        validated_logo = validate_image_path(logo_path)
        with Image.open(validated_logo).convert("RGBA") as logo_img:
            logo_ratio = logo_img.height / logo_img.width
            logo_size = (max_logo_width, int(max_logo_width * logo_ratio))
            logo = logo_img.resize(logo_size, Image.LANCZOS)
            overlay.paste(
                logo,
                (width - logo.width - padding, padding),
                mask=logo,
            )
    else:
        draw = ImageDraw.Draw(overlay)
        placeholder_height = max_logo_width // 2
        draw.rounded_rectangle(
            [
                (width - max_logo_width - padding, padding),
                (width - padding, padding + placeholder_height),
            ],
            radius=12,
            fill=BRAND_COLORS["accent_gold"],
            outline=BRAND_COLORS["primary"],
            width=2,
        )
        draw.text(
            (width - max_logo_width + border_thickness, padding + border_thickness),
            "LOGO",
            font=_load_font(font_size=16),
            fill=BRAND_COLORS["primary"],
        )


def _wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
) -> str:
    """Wrap text to fit within a specified pixel width."""
    words = text.split()
    if not words:
        return ""

    lines: List[str] = []
    current_line: List[str] = []

    for word in words:
        tentative = " ".join(current_line + [word]) if current_line else word
        if draw.textlength(tentative, font=font) <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return "\n".join(lines)


def save_markdown_templates(output_path: Path) -> Path:
    """Persist the Markdown templates to a file for distribution."""
    markdown_content = generate_markdown_templates()
    output_path.write_text(markdown_content, encoding="utf-8")
    return output_path


__all__ = [
    "BRAND_COLORS",
    "LOGO_PLACEHOLDER",
    "COLOR_PLACEHOLDER",
    "PostTemplate",
    "build_base_templates",
    "generate_markdown_templates",
    "generate_branded_image",
    "save_markdown_templates",
]
