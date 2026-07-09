#!/usr/bin/env python3
"""Feature-Callouts: Label plus Linie zum jeweiligen Produktteil.

Das Produkt kommt aus der Generierung; hier werden NUR Erklaer-Grafiken ergaenzt,
kein Produkt-Compositing. Fuer den Ad-Typ "Produkt mittig, Pfeile erklaeren die USPs".

Usage:
  overlay_callouts.py --image in.png --output out.png \
    --headline "In Sekunden verstellt." \
    --callouts '[{"text":"1-kg-Schritte","lx":0.04,"ly":0.42,"tx":0.55,"ty":0.55,"align":"l"}]' \
    [--price "CHF 199.-"] [--strike "239.-"] [--discount "-17%"] [--theme dark|light]

lx/ly ist der Label-Anker, tx/ty der Zielpunkt am Produkt, beide als Fraktionen (0..1).
align: "l" Label rechts der Ankerlinie, "r" linksbuendig davon.
"""
from __future__ import annotations

import argparse
import json
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
    ap.add_argument("--callouts", required=True, help="JSON-Liste aus {text,lx,ly,tx,ty,align}")
    ap.add_argument("--price", default="")
    ap.add_argument("--strike", default="")
    ap.add_argument("--discount", default="")
    ap.add_argument("--theme", default="dark", choices=["dark", "light"])
    args = ap.parse_args()

    try:
        callouts = json.loads(args.callouts)
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: --callouts ist kein gueltiges JSON: {e}")

    c = colors()
    accent, ink, paper = c["accent"], c["ink"], c["paper"]

    img = Image.open(args.image).convert("RGBA")
    W, H = img.size
    dark = args.theme == "dark"
    text_col = paper if dark else ink

    if args.headline:
        scrim(img, "top", 0.30, dark, strength=140)
    d = ImageDraw.Draw(img)

    if args.headline:
        hl = font(int(W * 0.060), 800)
        x, y = int(W * 0.05), int(H * 0.05)
        for line in lines(args.headline):
            d.text((x, y), line, font=hl, fill=text_col)
            bb = d.textbbox((0, 0), line, font=hl)
            y += int((bb[3] - bb[1]) * 1.1) + int(hl.size * 0.15)

    cf = font(int(W * 0.030), 700)
    dotr = max(5, W // 150)
    for co in callouts:
        lx, ly = int(co["lx"] * W), int(co["ly"] * H)
        tx, ty = int(co["tx"] * W), int(co["ty"] * H)
        align = co.get("align", "l")

        d.ellipse([tx - dotr, ty - dotr, tx + dotr, ty + dotr], fill=accent)
        d.ellipse([tx - dotr * 2, ty - dotr * 2, tx + dotr * 2, ty + dotr * 2],
                  outline=accent, width=max(2, W // 400))
        d.line([lx, ly, tx, ty], fill=accent, width=max(2, W // 380))

        bb = d.textbbox((0, 0), co["text"], font=cf)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        pad = int(W * 0.014)
        bx0 = lx - tw - pad * 2 if align == "r" else lx
        by0 = ly - th // 2 - pad
        chip_bg = paper if dark else ink
        chip_fg = ink if dark else paper
        d.rounded_rectangle([bx0, by0, bx0 + tw + pad * 2, by0 + th + pad * 2],
                            radius=int(th * 0.9), fill=chip_bg)
        d.text((bx0 + pad - bb[0], by0 + pad - bb[1]), co["text"], font=cf, fill=chip_fg)

    if args.price:
        scrim(img, "bottom", 0.24, dark, strength=140)
        d = ImageDraw.Draw(img)
        pf = font(int(W * 0.050), 800)
        bb = d.textbbox((0, 0), args.price, font=pf)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        padx, pady = int(W * 0.03), int(W * 0.02)
        pw, ph = tw + padx * 2, th + pady * 2
        px, py = W - int(W * 0.05) - pw, H - int(H * 0.05) - ph
        d.rounded_rectangle([px, py, px + pw, py + ph], radius=ph // 2, fill=accent)
        d.text((px + padx - bb[0], py + pady - bb[1]), args.price, font=pf, fill=ink)

        if args.strike:
            sf = font(int(W * 0.032), 600)
            sb = d.textbbox((0, 0), args.strike, font=sf)
            sw = sb[2] - sb[0]
            sx = px - int(W * 0.02) - sw
            sy = py + (ph - (sb[3] - sb[1])) // 2 - sb[1]
            d.text((sx, sy), args.strike, font=sf, fill=text_col)
            mid = sy + (sb[3] - sb[1]) / 2 + sb[1]
            d.line([sx, mid, sx + sw, mid], fill=text_col, width=max(2, W // 500))

    if args.discount:
        r = int(W * 0.075)
        discount_circle(d, (W - int(W * 0.06) - r, int(H * 0.06) + r), r, args.discount, accent, ink)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(args.output, quality=94)
    print(f"[callouts] {args.output} ({W}x{H})")


if __name__ == "__main__":
    main()
