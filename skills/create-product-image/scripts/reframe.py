#!/usr/bin/env python3
"""Bringe ein (meist quadratisches) Basisbild in ein Zielformat, OHNE Pixel zu erfinden.

Nur mittiges Beschneiden. Der Grund steht in der SKILL.md unter "Natives Hochformat":
9:16 (0.5625) und 4:5 (0.8) sind SCHMALER als ein Quadrat, also wird die BREITE
beschnitten und der echte Hintergrund bleibt oben und unten erhalten. Frueher wurde
stattdessen die Hoehe "ergaenzt", also Randzeilen gestreckt - das erzeugte schwarze
Balken und verwaschene Streifen. Nie wieder.

Damit ein Mittel-Crop nichts Wichtiges abschneidet, muss das Quadrat 9:16-first
komponiert sein: alle Elemente in einer schmalen vertikalen Mittelspalte.

Usage: reframe.py --image in.png --output out.png --ratio 1:1|4:5|9:16|16:9
                  [--anchor center|top|bottom|left|right]
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

RATIOS = {"1:1": 1.0, "4:5": 0.8, "9:16": 9 / 16, "16:9": 16 / 9}


def crop_to_ratio(img: Image.Image, target: float, anchor: str) -> Image.Image:
    W, H = img.size
    src = W / H
    if abs(src - target) < 1e-3:
        return img
    if target < src:  # Ziel schmaler -> Breite beschneiden
        nw = int(round(H * target))
        if anchor == "left":
            x = 0
        elif anchor == "right":
            x = W - nw
        else:
            x = (W - nw) // 2
        return img.crop((x, 0, x + nw, H))
    # Ziel breiter -> Hoehe beschneiden
    nh = int(round(W / target))
    if anchor == "top":
        y = 0
    elif anchor == "bottom":
        y = H - nh
    else:
        y = (H - nh) // 2
    return img.crop((0, y, W, y + nh))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--ratio", required=True, choices=list(RATIOS))
    ap.add_argument("--anchor", default="center",
                    choices=["center", "top", "bottom", "left", "right"],
                    help="Welcher Bildteil beim Beschneiden erhalten bleibt (Default: center).")
    args = ap.parse_args()

    img = Image.open(args.image).convert("RGB")
    out = crop_to_ratio(img, RATIOS[args.ratio], args.anchor)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    out.save(args.output, quality=94)
    print(f"[reframe] {args.output.name}: {out.size} ({args.ratio}, Crop {args.anchor})")


if __name__ == "__main__":
    main()
