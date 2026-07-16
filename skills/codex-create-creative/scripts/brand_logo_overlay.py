#!/usr/bin/env python3
"""Manual-konformes Logo-Overlay fuer Ad-Creatives (Brand-Guidelines-Pfad).

Setzt das ECHTE Vektor-Logo (als PNG-Export) gemaess Brand-Manual-Placement-Matrix
auf ein fertiges Creative — als eine von zwei erlaubten Foto-Varianten:

  box    — solide Logo-Box (Brand-Grau, abgerundet), unten-mittig oder unten-rechts
  stripe — Streifen ueber volle Breite (dunkel, 15% Deckkraft) am unteren Rand,
           darauf die solide Logo-Box (im Foto steht das Logo nie "nackt")

Hochformate (Banner-Regel: Logo OBEN-mittig) via --top.
Voraussetzung: Das Creative haelt die untere (bzw. obere) Zone frei —
im Design-Struct-Prompt "reserved_logo_zone" (13%) setzen.

Usage:
  brand_logo_overlay.py --image final.png --logo logo-weiss.png \
     --variant box|stripe [--pos center|right] [--top] \
     [--box-color 465359] [--width-frac 0.30] [--out out.png]
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw


def build(args) -> None:
    img = Image.open(args.image).convert("RGBA")
    W, H = img.size
    logo = Image.open(args.logo).convert("RGBA")

    box_w = int(W * args.width_frac)
    pad_x = int(box_w * 0.085)
    logo_w = box_w - 2 * pad_x
    logo_h = int(logo.height * (logo_w / logo.width))
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
    pad_y = int(logo_h * 0.55)
    box_h = logo_h + 2 * pad_y

    margin = int(H * 0.045)
    box_col = tuple(int(args.box_color[i:i + 2], 16) for i in (0, 2, 4)) + (255,)

    if args.pos == "right":
        bx = W - margin - box_w
    else:
        bx = (W - box_w) // 2
    by = margin if args.top else H - margin - box_h

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(overlay)

    if args.variant == "stripe":
        stripe_h = box_h + margin
        sy = 0 if args.top else H - stripe_h
        dr.rectangle((0, sy, W, sy + stripe_h), fill=(20, 25, 28, 38))  # 15% Deckkraft
        by = sy + (stripe_h - box_h) // 2
        if args.pos != "right":
            bx = (W - box_w) // 2

    dr.rounded_rectangle((bx, by, bx + box_w, by + box_h),
                         radius=max(6, box_h // 7), fill=box_col)
    overlay.alpha_composite(logo, (bx + pad_x, by + pad_y))

    img.alpha_composite(overlay)
    out = Path(args.out) if args.out else Path(args.image)
    img.convert("RGB").save(out, quality=94)
    print(f"[brand-logo] {out.name}: {args.variant}/{'top' if args.top else 'bottom'}-{args.pos} "
          f"box {box_w}x{box_h}px")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--logo", required=True, help="weisse Wortmarken-PNG (transparent)")
    ap.add_argument("--variant", choices=["box", "stripe"], default="box")
    ap.add_argument("--pos", choices=["center", "right"], default="right")
    ap.add_argument("--top", action="store_true",
                    help="Banner-/Hochformat-Regel: Logo oben-mittig statt unten")
    ap.add_argument("--box-color", default="465359")
    ap.add_argument("--width-frac", type=float, default=0.30)
    ap.add_argument("--out")
    build(ap.parse_args())


if __name__ == "__main__":
    main()
