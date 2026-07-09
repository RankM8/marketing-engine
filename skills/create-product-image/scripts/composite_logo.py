#!/usr/bin/env python3
"""Setze das ECHTE Logo als Marken-Element in eine Creative-Ecke.

Das ist KEIN Produkt-Compositing, sondern die Marken-Signatur der Anzeige, wie sie
jede echte Ad hat. Die helle oder dunkle Variante wird automatisch nach der Helligkeit
des Zielbereichs gewaehlt.

Wichtig: niemals ein Logo auf das Produkt selbst fälschen. Wenn das Produkt ein Logo
tragen soll, muss es aus dem echten Referenzfoto stammen (Background-Swap).

Logopfade kommen aus der brand.json (logo.light / logo.dark) oder per Argument.

Usage:
  composite_logo.py --image in.png [--output out.png] \
     [--logo-light hell.png --logo-dark dunkel.png] \
     [--pos bl|tl|br|tr] [--width-frac 0.26] [--margin-frac 0.05]
Ohne --output wird die Eingabedatei ueberschrieben.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brandkit import load_brand, resolve  # noqa: E402


def luminance_of(img: Image.Image, box) -> float:
    crop = img.convert("RGB").crop(box).resize((16, 16))
    px = list(crop.getdata())
    return sum(0.299 * r + 0.587 * g + 0.114 * b for r, g, b in px) / len(px)


def _logo_paths(args) -> tuple[Path, Path]:
    """Argumente gewinnen, sonst brand.json. Fehlt beides, sauber abbrechen."""
    brand_logos = (load_brand().get("logo") or {})
    light = args.logo_light or resolve(brand_logos.get("light"))
    dark = args.logo_dark or resolve(brand_logos.get("dark"))
    if not light or not dark:
        sys.exit(
            "ERROR: Logopfade fehlen. Uebergib --logo-light und --logo-dark, oder trage "
            "logo.light und logo.dark in der brand.json ein."
        )
    for p in (light, dark):
        if not Path(p).exists():
            sys.exit(f"ERROR: Logo nicht gefunden: {p}")
        if Path(p).suffix.lower() == ".svg":
            sys.exit(
                f"ERROR: {p} ist eine SVG. PIL kann kein SVG oeffnen. Exportiere die Wortmarke "
                "als PNG mit transparentem Hintergrund (z. B. 1200px breit)."
            )
    return Path(light), Path(dark)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True, type=Path)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--logo-light", type=Path, help="helle Wortmarke (fuer dunklen Hintergrund)")
    ap.add_argument("--logo-dark", type=Path, help="dunkle Wortmarke (fuer hellen Hintergrund)")
    ap.add_argument("--pos", default="bl", choices=["bl", "tl", "br", "tr"])
    ap.add_argument("--width-frac", type=float, default=0.26)
    ap.add_argument("--margin-frac", type=float, default=0.05)
    args = ap.parse_args()

    logo_light, logo_dark = _logo_paths(args)

    img = Image.open(args.image).convert("RGBA")
    W, H = img.size
    lw = int(W * args.width_frac)
    m = int(W * args.margin_frac)

    x = m if args.pos in ("bl", "tl") else W - m - lw

    probe_h = int(H * 0.12)
    if args.pos in ("bl", "br"):
        ybox = (x, H - m - probe_h, x + lw, H - m)
    else:
        ybox = (x, m, x + lw, m + probe_h)
    lum = luminance_of(img, (max(0, ybox[0]), max(0, ybox[1]), min(W, ybox[2]), min(H, ybox[3])))
    logo_path = logo_light if lum < 130 else logo_dark

    logo = Image.open(logo_path).convert("RGBA")
    lh = int(logo.height * (lw / logo.width))
    logo = logo.resize((lw, lh))
    y = (H - m - lh) if args.pos in ("bl", "br") else m
    img.alpha_composite(logo, (x, y))

    out = args.output or args.image
    img.convert("RGB").save(out, quality=94)
    print(f"[logo] {out.name}: Helligkeit={lum:.0f} -> {'helle' if lum < 130 else 'dunkle'} Variante")


if __name__ == "__main__":
    main()
