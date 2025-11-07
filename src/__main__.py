"""Command line interface for generating Pulte-branded social assets."""
from __future__ import annotations

import argparse
from pathlib import Path

from .content_templates import (
    generate_branded_image,
    generate_markdown_templates,
    save_markdown_templates,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create Pulte-compliant social content templates and imagery.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    templates_parser = subparsers.add_parser(
        "templates",
        help="Export the Markdown templates for all supported social platforms.",
    )
    templates_parser.add_argument(
        "--output",
        type=Path,
        default=Path("pulte_social_templates.md"),
        help="Destination file for the Markdown output.",
    )

    image_parser = subparsers.add_parser(
        "image",
        help="Apply brand styling to an uploaded image.",
    )
    image_parser.add_argument("image", type=Path, help="Path to the source image (JPG/PNG).")
    image_parser.add_argument(
        "--message",
        required=True,
        help=(
            "Overlay text for the sales message. Keep concise for clarity and compliance."
        ),
    )
    image_parser.add_argument(
        "--output",
        type=Path,
        default=Path("pulte_branded_image.jpg"),
        help="Output path for the branded image.",
    )
    image_parser.add_argument(
        "--logo",
        type=Path,
        help="Optional path to the official logo (JPG/PNG).",
    )

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "templates":
        output_path = save_markdown_templates(args.output)
        print(f"Markdown templates saved to {output_path}")
    elif args.command == "image":
        output_path = generate_branded_image(
            image_path=args.image,
            output_path=args.output,
            message_text=args.message,
            logo_path=args.logo,
        )
        print(f"Branded image saved to {output_path}")


if __name__ == "__main__":
    main()
