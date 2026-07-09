#!/usr/bin/env python3
"""Hochkant-Overlay (Stories/Reels): vertikales Editorial-Layout.

Oben Akzentbalken, optionale Eyebrow und grosse linksbuendige Headline. Unten
Preis-Pille, Streichpreis und Rabatt-Kreis. Das Produkt fuellt die untere Bildhaelfte.

Voraussetzung: das Bild ist bereits im Hochformat (siehe reframe.py). Dieses Script
verzerrt nichts, es legt nur Typografie auf.

Usage:
  overlay_portrait.py --image in.png --output out.png --headline "Z1\\nZ2" \
    --price "CHF 199.-" [--strike "239.-"] [--discount "-17%"] [--eyebrow "..."] [--theme dark|light]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brandkit import colors, discount_circle, font, lines, scrim  # noqa: E402


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
    scrim(img, "top", 0.46, dark, strength=170)
    scrim(img, "bottom", 0.22, dark)
    d = ImageDraw.Draw(img)

    mx = int(W * 0.07)
    y = int(H * 0.06)
    d.rectangle([mx, y, mx + int(W * 0.14), y + max(6, int(W * 0.018))], fill=accent)
    y += int(W * 0.06)

    if args.eyebrow:
        ef = font(int(W * 0.040), 700)
        d.text((mx, y), args.eyebrow.upper(), font=ef, fill=accent)
        y += int(W * 0.07)

    hl = font(int(W * 0.092), 800)
    for line in lines(args.headline):
        d.text((mx, y), line, font=hl, fill=text_col)
        bb = d.textbbox((0, 0), line, font=hl)
        y += int((bb[3] - bb[1]) * 1.1) + int(hl.size * 0.12)

    if args.price:
        pf = font(int(W * 0.065), 800)
        bb = d.textbbox((0, 0), args.price, font=pf)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        padx, pady = int(W * 0.035), int(W * 0.026)
        pw, ph = tw + padx * 2, th + pady * 2
        py = H - int(H * 0.05) - ph
        d.rounded_rectangle([mx, py, mx + pw, py + ph], radius=ph // 2, fill=accent)
        d.text((mx + padx - bb[0], py + pady - bb[1]), args.price, font=pf, fill=ink)
        cx = mx + pw

        if args.strike:
            sf = font(int(W * 0.040), 600)
            sb = d.textbbox((0, 0), args.strike, font=sf)
            sw = sb[2] - sb[0]
            sx = mx + pw + int(W * 0.02)
            sy = py + (ph - (sb[3] - sb[1])) // 2 - sb[1]
            d.text((sx, sy), args.strike, font=sf, fill=text_col)
            mid = sy + (sb[3] - sb[1]) / 2 + sb[1]
            d.line([sx, mid, sx + sw, mid], fill=text_col, width=max(2, W // 360))
            cx = sx + sw

        if args.discount:
            r = int(W * 0.075)
            discount_circle(d, (cx + int(W * 0.04) + r, py + ph // 2), r, args.discount, accent, ink)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(args.output, quality=94)
    print(f"[portrait] {args.output.name} ({W}x{H})")


if __name__ == "__main__":
    main()
