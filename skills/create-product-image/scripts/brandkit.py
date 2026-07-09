"""Marken-Konfiguration und geteilte PIL-Helfer fuer die Overlay-Scripts.

Die Marke wird NICHT im Plugin hinterlegt, sondern in einer `brand.json`, die im
Kunden-Verzeichnis liegt. Gesucht wird vom aktuellen Arbeitsverzeichnis aufwaerts
durch den Verzeichnisbaum - dasselbe Muster, mit dem `gateways.load_key()` die
`.env` findet. Damit gilt eine `brand.json` in `Kunden/<Kunde>/` automatisch fuer
alles darunter, und dasselbe Plugin bedient den naechsten Kunden mit dessen Datei.

Ueberschreiben per Umgebungsvariable: MARKETING_ENGINE_BRAND=/pfad/zu/brand.json

Aufbau siehe examples/brand.json im Plugin-Root.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

BRAND_FILENAME = "brand.json"

# Neutrale Defaults. Greifen nur, wenn keine brand.json gefunden wird - das
# Ergebnis ist dann unmarkiert, aber die Scripts laufen durch statt zu crashen.
DEFAULTS: dict[str, Any] = {
    "brand": "unbenannt",
    "colors": {
        "accent": "#ffcc00",
        "ink": "#1d2a30",
        "paper": "#f5f3ea",
    },
    "fonts": {
        "dir": None,
        "display": None,
    },
}

# PIL bringt DejaVuSans mit. Als letzter Ausweg, damit ein fehlender Marken-Font
# eine Warnung ist und kein Absturz.
_FALLBACK_FONTS = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

_cache: dict[str, Any] | None = None


def _deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        elif v is not None:
            out[k] = v
    return out


def find_brand_file(start: Path | None = None) -> Path | None:
    """Suche brand.json vom Startverzeichnis aufwaerts. Env-Override gewinnt."""
    env = os.environ.get("MARKETING_ENGINE_BRAND")
    if env:
        p = Path(env).expanduser()
        if not p.exists():
            sys.exit(f"ERROR: MARKETING_ENGINE_BRAND zeigt auf {p}, aber die Datei existiert nicht.")
        return p
    cwd = start or Path.cwd()
    for parent in [cwd, *cwd.parents]:
        candidate = parent / BRAND_FILENAME
        if candidate.exists():
            return candidate
    return None


def load_brand(start: Path | None = None) -> dict[str, Any]:
    """Lade die Marken-Konfiguration (gecacht). Fehlt sie, greifen die Defaults."""
    global _cache
    if _cache is not None:
        return _cache

    path = find_brand_file(start)
    if path is None:
        print(
            "[brandkit] WARNUNG: keine brand.json gefunden. Es gelten neutrale Defaults "
            "(kein Marken-Font, generische Farben). Vorlage: examples/brand.json.",
            file=sys.stderr, flush=True,
        )
        _cache = _deep_merge(DEFAULTS, {})
        _cache["_root"] = None
        return _cache

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: {path} ist kein gueltiges JSON: {e}")

    merged = _deep_merge(DEFAULTS, data)
    merged["_root"] = path.parent
    _cache = merged
    return merged


def resolve(rel: str | None, start: Path | None = None) -> Path | None:
    """Loese einen Pfad aus der brand.json relativ zu deren Verzeichnis auf."""
    if not rel:
        return None
    brand = load_brand(start)
    root = brand.get("_root")
    p = Path(rel).expanduser()
    if p.is_absolute() or root is None:
        return p
    return (root / p).resolve()


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    v = value.lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if len(v) != 6:
        sys.exit(f"ERROR: Farbe '{value}' ist kein Hex-Wert der Form #rrggbb.")
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def colors(start: Path | None = None) -> dict[str, tuple[int, int, int]]:
    """Markenfarben als RGB-Tupel: accent, ink, paper."""
    c = load_brand(start)["colors"]
    return {k: hex_to_rgb(v) for k, v in c.items()}


def _font_path(start: Path | None = None) -> str:
    brand = load_brand(start)
    fonts = brand.get("fonts") or {}
    display = fonts.get("display")
    if display:
        fdir = fonts.get("dir")
        candidate = resolve(f"{fdir}/{display}" if fdir else display, start)
        if candidate and candidate.exists():
            return str(candidate)
        print(
            f"[brandkit] WARNUNG: Marken-Font nicht gefunden unter {candidate}. "
            "Nutze System-Fallback - die Typografie entspricht nicht der Marke.",
            file=sys.stderr, flush=True,
        )
    for fb in _FALLBACK_FONTS:
        if Path(fb).exists():
            return fb
    sys.exit(
        "ERROR: Weder Marken-Font noch System-Fallback gefunden. "
        "Trage fonts.dir und fonts.display in der brand.json ein."
    )


def font(size: int, weight: int = 800, start: Path | None = None) -> ImageFont.FreeTypeFont:
    """Marken-Font in der gewuenschten Groesse. weight greift nur bei Variable Fonts."""
    f = ImageFont.truetype(_font_path(start), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass  # statischer Font: Gewicht ist bereits fest
    return f


def scrim(img: Image.Image, side: str, frac: float, dark: bool, strength: int = 150) -> None:
    """Farbverlauf oben oder unten, damit Text auf dem Bild lesbar bleibt."""
    w, h = img.size
    band = int(h * frac)
    if band <= 0:
        return
    grad = Image.new("L", (1, band))
    for y in range(band):
        a = int(strength * (1 - y / band)) if side == "top" else int(strength * (y / band))
        grad.putpixel((0, y), a)
    grad = grad.resize((w, band))
    color = (10, 14, 16) if dark else (250, 249, 244)
    layer = Image.new("RGBA", (w, band), color + (0,))
    layer.putalpha(grad)
    img.alpha_composite(layer, (0, 0 if side == "top" else h - band))


def lines(text: str) -> list[str]:
    """Zeilen aus einem Headline-Argument.

    Aus der Shell kommt `--headline "a\\nb"` als literales Backslash-n an, aus einem
    Python-Aufruf als echter Zeilenumbruch. Beide Formen werden getrennt.
    """
    return text.replace("\\n", "\n").split("\n")


def draw_lines(d: ImageDraw.ImageDraw, xy: tuple[int, int], text: str,
               fnt: ImageFont.FreeTypeFont, fill, line_gap: float = 1.06,
               extra: float = 0.18) -> int:
    """Zeichne mehrzeiligen Text; gibt die y-Position unter der letzten Zeile zurueck."""
    x, y = xy
    for line in lines(text):
        d.text((x, y), line, font=fnt, fill=fill)
        bbox = d.textbbox((0, 0), line, font=fnt)
        y += int((bbox[3] - bbox[1]) * line_gap) + int(fnt.size * extra)
    return y


def strike_through(d: ImageDraw.ImageDraw, xy: tuple[int, int], text: str,
                   fnt: ImageFont.FreeTypeFont, fill, line_width: int = 2) -> tuple[int, int]:
    """Streichpreis: Text plus durchgezogene Linie. Gibt (breite, hoehe) zurueck.

    line_width skaliert der Aufrufer aus der Bildbreite (z. B. max(2, W // 500)),
    damit die Linie bei jeder Aufloesung gleich wirkt.
    """
    x, y = xy
    bb = d.textbbox((0, 0), text, font=fnt)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.text((x, y), text, font=fnt, fill=fill)
    mid = y + th / 2 + bb[1]
    d.line([x, mid, x + tw, mid], fill=fill, width=max(2, line_width))
    return tw, th


def discount_circle(d: ImageDraw.ImageDraw, center: tuple[int, int], radius: int,
                    text: str, accent, ink) -> None:
    """Gelber Rabatt-Kreis mit zentrierter Prozentzahl."""
    cx, cy = center
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=accent)
    df = font(int(radius * 0.62), 800)
    bb = d.textbbox((0, 0), text, font=df)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]),
           text, font=df, fill=ink)
