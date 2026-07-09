#!/usr/bin/env python3
"""Landscape-Overlay (16:9): asymmetrische Editorial-Komposition.

Produkt rechts (kommt aus dem Bild), Text-Panel links: Akzentbalken, optionale Eyebrow,
Headline, Preis-Pille mit Streichpreis und Rabatt. Ein weicher Verlauf von links haelt
den Text lesbar, ohne das Produkt zu verdecken.

Usage:
  overlay_landscape.py --image in.png --output out.png --headline "Zeile1\\nZeile2" \
    --price "CHF 199.-" [--strike "239.-"] [--discount "-17%"] [--eyebrow "..."] [--theme dark|light]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brandkit import colors, discount_circle, font, lines  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--headline", default="")
    ap.add_argument("--eyebrow", default="")
    ap.add_argument("--price", default="")
    ap.add_argument("--strike", default="")
    ap.add_argument("--discount", default="")
    ap.add_argument("--theme", default="dark", choices=["dark", "light"])
    args = ap.parse_args()

    c = colors()
    accent, ink, paper = c["accent"], c["ink"], c["paper"]

    img = Image.open(args.image).convert("RGBA")
    W, H = img.size
    dark = args.theme == "dark"
    text_col = paper if dark else ink

    # Horizontaler Verlauf: links deckend, zur Bildmitte hin transparent.
    grad = Image.new("L", (W, 1))
    for x in range(W):
        grad.putpixel((x, 0), int(165 * max(0, 1 - x / (W * 0.55))))
    grad = grad.resize((W, H))
    veil = Image.new("RGBA", (W, H), ((8, 12, 14) if dark else (250, 249, 244)) + (0,))
    veil.putalpha(grad)
    img.alpha_composite(veil)
    d = ImageDraw.Draw(img)

    mx = int(W * 0.055)
    y = int(H * 0.18)
    d.rectangle([mx, y, mx + int(W * 0.05), y + max(5, int(H * 0.012))], fill=accent)
    y += int(H * 0.05)

    if args.eyebrow:
        ef = font(int(H * 0.035), 700)
        d.text((mx, y), args.eyebrow.upper(), font=ef, fill=accent)
        y += int(H * 0.06)

    hl = font(int(H * 0.105), 800)
    for line in lines(args.headline):
        d.text((mx, y), line, font=hl, fill=text_col)
        bb = d.textbbox((0, 0), line, font=hl)
        y += int((bb[3] - bb[1]) * 1.12) + int(hl.size * 0.12)
    y += int(H * 0.04)

    if args.price:
        pf = font(int(H * 0.075), 800)
        bb = d.textbbox((0, 0), args.price, font=pf)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        padx, pady = int(H * 0.035), int(H * 0.025)
        pw, ph = tw + padx * 2, th + pady * 2
        d.rounded_rectangle([mx, y, mx + pw, y + ph], radius=ph // 2, fill=accent)
        d.text((mx + padx - bb[0], y + pady - bb[1]), args.price, font=pf, fill=ink)
        cx = mx + pw

        if args.strike:
            sf = font(int(H * 0.045), 600)
            sb = d.textbbox((0, 0), args.strike, font=sf)
            sw = sb[2] - sb[0]
            sx = mx + pw + int(W * 0.015)
            sy = y + (ph - (sb[3] - sb[1])) // 2 - sb[1]
            d.text((sx, sy), args.strike, font=sf, fill=text_col)
            mid = sy + (sb[3] - sb[1]) / 2 + sb[1]
            d.line([sx, mid, sx + sw, mid], fill=text_col, width=max(2, H // 360))
            cx = sx + sw

        if args.discount:
            r = int(H * 0.07)
            discount_circle(d, (cx + int(W * 0.03) + r, y + ph // 2), r, args.discount, accent, ink)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(args.output, quality=94)
    print(f"[landscape] {args.output.name} ({W}x{H})")


if __name__ == "__main__":
    main()
