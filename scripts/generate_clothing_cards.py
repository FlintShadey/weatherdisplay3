#!/usr/bin/env python3
"""Generate placeholder clothing recommendation cards for the e-paper display."""
from __future__ import annotations

from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

PALETTE = {
    "black": "#000000",
    "white": "#FFFFFF",
    "yellow": "#FFD800",
    "red": "#C62828",
    "blue": "#0052CC",
    "green": "#0B8457",
}

CARDS = (
    {
        "slug": "hot",
        "title": "Hot & Sunny",
        "notes": ["Linen shirt", "Shorts", "Breathable shoes"],
        "base": PALETTE["yellow"],
        "stroke": PALETTE["red"],
        "text": PALETTE["black"],
    },
    {
        "slug": "mild",
        "title": "Mild Breeze",
        "notes": ["Light tee", "Chinos", "Cap"],
        "base": PALETTE["white"],
        "stroke": PALETTE["blue"],
        "text": PALETTE["black"],
    },
    {
        "slug": "cold",
        "title": "Cold Layers",
        "notes": ["Puffer jacket", "Beanie", "Boots"],
        "base": PALETTE["blue"],
        "stroke": PALETTE["white"],
        "text": PALETTE["white"],
    },
    {
        "slug": "rain",
        "title": "Rain Ready",
        "notes": ["Shell jacket", "Waterproof pants", "Umbrella"],
        "base": PALETTE["green"],
        "stroke": PALETTE["black"],
        "text": PALETTE["black"],
    },
)

FONT_PATH = Path("assets/fonts/RobotoMono-Regular.ttf")
TITLE_FONT_SIZE = 46
TEXT_FONT_SIZE = 32
CARD_SIZE = (400, 480)


def draw_outfit(draw: ImageDraw.ImageDraw, stroke: str, y_offset: int) -> None:
    """Draw a simple stylized outfit icon."""
    shirt_top = (100, y_offset)
    shirt_bottom = (300, y_offset + 120)
    draw.rounded_rectangle([shirt_top, shirt_bottom], radius=20, outline=stroke, width=6)
    draw.line([(100, y_offset + 60), (300, y_offset + 60)], fill=stroke, width=6)
    draw.rectangle([(160, y_offset + 120), (240, y_offset + 200)], outline=stroke, width=6)
    draw.line([(160, y_offset + 200), (160, y_offset + 320)], fill=stroke, width=6)
    draw.line([(240, y_offset + 200), (240, y_offset + 320)], fill=stroke, width=6)
    draw.line([(120, y_offset + 320), (280, y_offset + 320)], fill=stroke, width=6)


def main() -> None:
    out_dir = Path("assets/clothing")
    out_dir.mkdir(parents=True, exist_ok=True)
    public_dir = Path("public/right-section")
    public_dir.mkdir(parents=True, exist_ok=True)

    title_font = ImageFont.truetype(str(FONT_PATH), TITLE_FONT_SIZE)
    body_font = ImageFont.truetype(str(FONT_PATH), TEXT_FONT_SIZE)

    for card in CARDS:
        img = Image.new("RGB", CARD_SIZE, color=card["base"])
        draw = ImageDraw.Draw(img)

        draw_outfit(draw, card["stroke"], y_offset=90)

        draw.text((30, 24), card["title"], font=title_font, fill=card["stroke"])
        body_color = card.get("text", PALETTE["black"])
        for idx, note in enumerate(card["notes"]):
            draw.text((30, 360 + idx * 38), f"• {note}", font=body_font, fill=body_color)

        target = out_dir / f"{card['slug']}.png"
        img.save(target, format="PNG", optimize=True)

        mirror = public_dir / f"{card['slug']}.png"
        img.save(mirror, format="PNG", optimize=True)

        print(f"wrote {target} and mirrored to {mirror}")


if __name__ == "__main__":
    main()
