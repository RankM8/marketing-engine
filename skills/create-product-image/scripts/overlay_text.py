#!/usr/bin/env python3
"""Lege fehlerfrei geschriebene Ad-Copy per PIL auf eine generierte Szene.

Die Haelfte der Methode, die dem Bildmodell die Typografie NICHT anvertraut: erst die
Szene rendern (generate.py --no-text), dann die Schrift mit Code darueberlegen. Bildmodelle
verstuemmeln kurze Markentexte, URLs und Preise selbst bei explizitem Prompt.

Layout: Headline oben (auf Scrim), Preis-Pille unten, Rabatt-Kreis oben rechts.
Farben und Schrift kommen aus der brand.json (siehe brandkit.py).

Usage:
  overlay_text.py --image scene.png --output ad.png \
     --headline "22 Hantelpaare.\\nEine Hantel." \
     --price "CHF 199.-" [--strike "239.-"] [--discount "-17%"] \
     [--sub "..."] [--theme dark|light] [--badge-pos br|bl]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brandkit import colors, discount_circle, draw_lines, font, scrim  # noqa: E402


def pill(d, anchor, text, fnt, bg, fg, pad=(34, 20)):
    """Abgerundete Preis-Pille. anchor=(x, y, align) mit align 'l' oder 'r'."""
    x, y, align = anchor
    bbox = d.textbbox((0, 0), text, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pw, ph = tw + pad[0] * 2, th + pad[1] * 2
    px = x if align == "l" else x - pw
    py = y - ph
    d.rounded_rectangle([px, py, px + pw, py + ph], radius=ph // 2, fill=bg)
    d.text((px + pad[0] - bbox[0], py + pad[1] - bbox[1]), text, font=fnt, fill=fg)
    return px, py, pw, ph


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--headline", default="")
    ap.add_argument("--sub", default="")
    ap.add_argument("--price", default="")
    ap.add_argument("--strike", default="")
    ap.add_argument("--discount", default="")
    ap.add_argument("--theme", default="dark", choices=["dark", "light"],
                    help="dark = heller Text auf dunklem Scrim; light = umgekehrt")
    ap.add_argument("--badge-pos", default="br", choices=["br", "bl"])
    ap.add_argument("--cta", default="", help="CTA-Pille (dunkel), landet unten auf der Gegenseite der Preis-Pille")
    args = ap.parse_args()

    c = colors()
    accent, ink, paper = c["accent"], c["ink"], c["paper"]

    img = Image.open(args.image).convert("RGBA")
    W, H = img.size
    dark = args.theme == "dark"
    text_col = paper if dark else ink
    d = ImageDraw.Draw(img)

    if args.headline:
        scrim(img, "top", 0.42, dark)
        d = ImageDraw.Draw(img)
        hl = font(int(W * 0.082), 800)
        margin = int(W * 0.06)
        y = draw_lines(d, (margin, int(H * 0.07)), args.headline, hl, text_col)
        if args.sub:
            sf = font(int(W * 0.032), 500)
            draw_lines(d, (margin, y + int(H * 0.015)), args.sub, sf, text_col)

    if args.discount:
        r = int(W * 0.085)
        discount_circle(d, (W - int(W * 0.07) - r, int(H * 0.07) + r), r, args.discount, accent, ink)

    if args.price:
        scrim(img, "bottom", 0.30, dark)
        d = ImageDraw.Draw(img)
        margin = int(W * 0.06)
        pf = font(int(W * 0.052), 800)
        anchor = (margin, H - int(H * 0.06), "l") if args.badge_pos == "bl" \
            else (W - margin, H - int(H * 0.06), "r")
        px, py, pw, ph = pill(d, anchor, args.price, pf, accent, ink)
        if args.strike:
            sf = font(int(W * 0.034), 600)
            sb = d.textbbox((0, 0), args.strike, font=sf)
            sw = sb[2] - sb[0]
            sx = px + pw + int(W * 0.02) if args.badge_pos == "bl" else px - int(W * 0.02) - sw
            sy = py + (ph - (sb[3] - sb[1])) // 2 - sb[1]
            d.text((sx, sy), args.strike, font=sf, fill=text_col)
            mid = sy + (sb[3] - sb[1]) / 2 + sb[1]
            d.line([sx, mid, sx + sw, mid], fill=text_col, width=max(2, W // 500))

    if args.cta:
        if not args.price:
            scrim(img, "bottom", 0.30, dark)
        d = ImageDraw.Draw(img)
        margin = int(W * 0.06)
        cf = font(int(W * 0.040), 700)
        anchor = (W - margin, H - int(H * 0.06), "r") if args.badge_pos == "bl" \
            else (margin, H - int(H * 0.06), "l")
        pill(d, anchor, args.cta, cf, ink, paper)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(args.output, quality=94)
    print(f"[overlay] {args.output} ({W}x{H})")


if __name__ == "__main__":
    main()
