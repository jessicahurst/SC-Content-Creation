"""Image generation utilities for branded social graphics."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageColor, ImageDraw

from .fonts import load_font

PRIMARY_COLOR = "#00334C"
ACCENT_GOLD = "#F2C75C"
WHITE = "#FFFFFF"

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


@dataclass(slots=True)
class TextBlock:
    """Represents a chunk of text to render."""

    text: str
    font_size: int
    line_spacing: float = 1.2


@dataclass(slots=True)
class LayoutConfig:
    """Configuration values for the branding layout."""

    border_size: int = 40
    overlay_height_ratio: float = 0.36
    padding: int = 48
    accent_bar_height: int = 12
    logo_max_width_ratio: float = 0.22
    logo_max_height_ratio: float = 0.2
    text_column_width_ratio: float = 0.75
    min_text_font_size: int = 28


PRIMARY_RGBA = (*ImageColor.getrgb(PRIMARY_COLOR), 230)
ACCENT_RGBA = (*ImageColor.getrgb(ACCENT_GOLD), 255)
WHITE_RGBA = (*ImageColor.getrgb(WHITE), 255)


def validate_image_path(image_path: Path) -> None:
    """Validate that *image_path* exists and has an approved extension."""
    if image_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported image format '{image_path.suffix}'. "
            "Please provide a JPG or PNG file."
        )
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")


def generate_branded_image(
    source_image_path: Path,
    logo_path: Path,
    output_path: Path,
    texts: Sequence[TextBlock],
    layout: LayoutConfig | None = None,
    *,
    font_search_paths: Iterable[Path] | None = None,
) -> None:
    """Create a branded image using the provided layout."""
    layout = layout or LayoutConfig()

    validate_image_path(source_image_path)
    validate_image_path(logo_path)

    with Image.open(source_image_path).convert("RGBA") as base_image:
        with Image.open(logo_path).convert("RGBA") as logo_image:
            composed = _apply_brand_overlay(
                base_image,
                logo_image,
                texts,
                layout,
                font_search_paths=font_search_paths,
            )
            output_path.parent.mkdir(parents=True, exist_ok=True)
            composed.save(output_path)


def _apply_brand_overlay(
    base_image: Image.Image,
    logo_image: Image.Image,
    texts: Sequence[TextBlock],
    layout: LayoutConfig,
    *,
    font_search_paths: Iterable[Path] | None = None,
) -> Image.Image:
    width, height = base_image.size
    overlay_height = int(height * layout.overlay_height_ratio)

    working = base_image.copy()
    overlay = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    overlay_top = height - overlay_height
    draw.rectangle(
        [(0, overlay_top), (width, height)],
        fill=PRIMARY_RGBA,
    )

    draw.rectangle(
        [(0, overlay_top - layout.accent_bar_height), (width, overlay_top)],
        fill=ACCENT_RGBA,
    )

    column_width = int(width * layout.text_column_width_ratio) - layout.padding * 2
    if column_width <= 0:
        column_width = width - layout.padding * 2
    y_cursor = overlay_top + layout.padding

    for block in texts:
        font = load_font(max(block.font_size, layout.min_text_font_size), font_search_paths)
        y_cursor = _draw_wrapped_text(
            draw,
            block.text,
            font,
            x=layout.padding,
            y=y_cursor,
            max_width=column_width,
            line_spacing=block.line_spacing,
        )
        y_cursor += 12

    composed = Image.alpha_composite(working, overlay)

    composed = _paste_logo(composed, logo_image, layout)
    bordered = _add_brand_border(composed, layout)

    return bordered.convert("RGB")


def _draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font,
    *,
    x: int,
    y: int,
    max_width: int,
    line_spacing: float,
) -> int:
    """Render *text* with word wrapping and return the new y position."""
    words = text.split()
    if not words:
        return y

    lines: list[str] = []
    current_line: list[str] = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_width = bbox[2] - bbox[0]
        if line_width <= max_width or not current_line:
            current_line.append(word)
            continue
        lines.append(" ".join(current_line))
        current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))

    ascent, descent = font.getmetrics()
    line_height = int((ascent + descent) * line_spacing)
    if line_height <= 0:
        line_height = int(font.size * line_spacing)

    for line in lines:
        draw.text((x, y), line, font=font, fill=WHITE_RGBA)
        y += line_height
    return y


def _paste_logo(image: Image.Image, logo: Image.Image, layout: LayoutConfig) -> Image.Image:
    width, height = image.size
    max_width = max(int(width * layout.logo_max_width_ratio), 1)
    max_height = max(int(height * layout.logo_max_height_ratio), 1)

    logo_ratio = min(max_width / logo.width, max_height / logo.height, 1.0)
    new_logo_size = (max(int(logo.width * logo_ratio), 1), max(int(logo.height * logo_ratio), 1))
    resized_logo = logo.resize(new_logo_size, Image.LANCZOS)

    composed = image.copy()
    margin = max(layout.padding // 2, 10)
    position = (width - new_logo_size[0] - margin, margin)
    composed.paste(resized_logo, position, resized_logo)
    return composed


def _add_brand_border(image: Image.Image, layout: LayoutConfig) -> Image.Image:
    border = max(layout.border_size, 1)
    width, height = image.size
    bordered = Image.new("RGB", (width + border * 2, height + border * 2), PRIMARY_COLOR)
    bordered.paste(image, (border, border))

    draw = ImageDraw.Draw(bordered)
    draw.rectangle(
        [(border - 6, border - 6), (bordered.width - border + 6, bordered.height - border + 6)],
        outline=ACCENT_GOLD,
        width=6,
    )
    return bordered
