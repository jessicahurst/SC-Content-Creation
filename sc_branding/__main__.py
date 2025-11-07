"""Command line interface for the sales consultant branding toolkit."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from .captions import (
    CaptionInputs,
    DEFAULT_CTA,
    DEFAULT_HOOK,
    DEFAULT_VALUE,
    generate_captions,
)
from .generator import TextBlock, generate_branded_image


def _parse_font_paths(values: Iterable[str] | None) -> list[Path]:
    if not values:
        return []
    return [Path(value).expanduser() for value in values]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create branded social graphics with the approved color palette, "
            "logo placement, and caption templates."
        )
    )
    parser.add_argument("source_image", type=Path, help="Path to the background JPG or PNG image.")
    parser.add_argument("logo", type=Path, help="Path to the company logo (PNG with transparency recommended).")
    parser.add_argument("output", type=Path, help="File path for the generated branded image.")

    parser.add_argument(
        "--hook",
        default=DEFAULT_HOOK,
        help="Hook text that appears at the top of the overlay.",
    )  # PERSONALIZE: Provide an engaging intro tailored to the community or offer.
    parser.add_argument(
        "--value",
        default=DEFAULT_VALUE,
        help="Value text explaining the benefits.",
    )  # PERSONALIZE: Highlight key selling points or program details.
    parser.add_argument(
        "--cta",
        default=DEFAULT_CTA,
        help="Call-to-action text that remains editable for consultants.",
    )  # PERSONALIZE: Specify how prospects should reach you (e.g., Book an appointment).

    parser.add_argument(
        "--caption-file",
        type=Path,
        help="Optional path to save the platform captions to a text file.",
    )
    parser.add_argument(
        "--font-path",
        action="append",
        help="Additional directories or font files to search for Arial.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    font_paths = _parse_font_paths(args.font_path)

    texts = [
        TextBlock(args.hook.strip(), font_size=56, line_spacing=1.05),
        TextBlock(args.value.strip(), font_size=38, line_spacing=1.18),
        TextBlock(args.cta.strip(), font_size=34, line_spacing=1.1),
    ]

    generate_branded_image(
        args.source_image,
        args.logo,
        args.output,
        texts,
        font_search_paths=font_paths,
    )

    captions = generate_captions(
        CaptionInputs(hook=args.hook, value=args.value, cta=args.cta)
    )

    if args.caption_file:
        write_captions(Path(args.caption_file), captions)
    else:
        print("\nGenerated Captions:\n-------------------")
        for platform, caption in captions.items():
            print(f"\n[{platform}]\n{caption}")

    print(f"\nBranded image saved to {args.output.resolve()}")


def write_captions(path: Path, captions: dict[str, str]) -> None:
    lines = []
    for platform, caption in captions.items():
        lines.append(f"[{platform}]\n{caption}\n")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Caption file written to {path.resolve()}")


if __name__ == "__main__":  # pragma: no cover
    main()
