"""Caption generation helpers for social platforms."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(slots=True)
class CaptionInputs:
    """Text blocks supplied by the user."""

    hook: str
    value: str
    cta: str


# PERSONALIZE: Update the default hook to highlight the latest promotion or news.
DEFAULT_HOOK = "Discover what makes our newest community special."
# PERSONALIZE: Share specific value points such as amenities, incentives, or timelines.
DEFAULT_VALUE = (
    "Tailored floor plans, transparent pricing, and expert guidance help you move forward with confidence."
)
# PERSONALIZE: Provide the best call-to-action for your sales workflow.
DEFAULT_CTA = "Book an appointment to explore your options."  # CTA text remains editable.


def generate_captions(inputs: CaptionInputs) -> Dict[str, str]:
    """Return platform-formatted captions respecting brand tone."""
    hook = inputs.hook.strip()
    value = inputs.value.strip()
    cta = inputs.cta.strip()

    base_message = f"{hook}\n\n{value}\n\n{cta}"

    linkedin = (
        f"{base_message}\n\n"
        "Let's connect to build the right solution together.\n"
        "# PERSONALIZE: Add up to three compliant hashtags (e.g., #NewHomes #PulteHomes)"
    )

    instagram = (
        f"{base_message}\n\n"
        "# PERSONALIZE: Add emojis or branded hashtags that fit Instagram's tone (e.g., #DesignInspo)"
    )

    facebook = (
        f"{base_message}\n\n"
        "We're here to answer questions—message us anytime!"
    )

    builder_to_realtor = (
        f"{base_message}\n\n"
        "Share with a client who is ready for their next step."
    )

    return {
        "LinkedIn": linkedin,
        "Instagram": instagram,
        "Facebook": facebook,
        "Builder to Realtor": builder_to_realtor,
    }
