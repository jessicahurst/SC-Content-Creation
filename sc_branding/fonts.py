"""Font loading utilities with Arial fallback support."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from PIL import ImageFont


ARIAL_CANDIDATES: tuple[str, ...] = (
    "Arial.ttf",
    "arial.ttf",
    "Arial Bold.ttf",
    "arialbd.ttf",
)

SAFE_FALLBACKS: tuple[str, ...] = (
    "DejaVuSans.ttf",
    "LiberationSans-Regular.ttf",
)


def load_font(size: int, extra_search_paths: Optional[Iterable[Path]] = None) -> ImageFont.ImageFont:
    """Return a TrueType font for the requested size."""

    search_paths: list[Path] = []
    if extra_search_paths:
        search_paths.extend(Path(p) for p in extra_search_paths)

    for candidate in ARIAL_CANDIDATES + SAFE_FALLBACKS:
        font_path = _find_font(candidate, search_paths)
        if font_path:
            try:
                return ImageFont.truetype(str(font_path), size=size)
            except OSError:
                continue

    # Final fallback uses the default bitmap font scaled reasonably.
    return ImageFont.load_default()


def _find_font(font_name: str, search_paths: Iterable[Path]) -> Optional[Path]:
    """Locate *font_name* in standard font directories."""
    for base in list(search_paths) + _default_font_dirs():
        candidate = base / font_name
        if candidate.exists():
            return candidate
    return None


def _default_font_dirs() -> list[Path]:
    """Return directories that commonly contain system fonts."""
    return [
        Path("/usr/share/fonts"),
        Path("/usr/local/share/fonts"),
        Path.home() / ".fonts",
        Path.home() / "Library/Fonts",
        Path("C:/Windows/Fonts"),
    ]
