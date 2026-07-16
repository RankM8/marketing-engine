#!/usr/bin/env python3
"""Indexiert alle Bilder aus der konfigurierten Quelle (portal.config.json) fuer die Timeline.

Catch-All: JEDES Bild unterhalb von `quelle` landet im Portal — auch aus neuen
Unterordnern, ohne Pflege. Zeitstempel kommen bevorzugt aus einer manifest.json
im Quell-Root ({dateiname: {"generiert": epoch}}), sonst aus der Datei-mtime
(Drive-Sync kann mtimes verfaelschen — deshalb das Manifest).
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG_FILE = ROOT / "portal.config.json"
GEN = ROOT / "public" / "creatives" / "_gen"
OUT = ROOT / "src" / "data" / "creatives.ts"
EXT = {".png", ".jpg", ".jpeg", ".webp"}
QUIET = "--quiet" in sys.argv


def log(msg: str) -> None:
    if not QUIET:
        print(msg)


def main() -> None:
    if not CFG_FILE.exists():
        sys.exit("portal.config.json fehlt — kopiere portal.config.json.example und trage 'quelle' ein.")
    cfg = json.loads(CFG_FILE.read_text())
    src = Path(cfg["quelle"]).expanduser()
    if not src.is_dir():
        sys.exit(f"Quelle nicht gefunden: {src} — laeuft der Drive-Sync?")

    manifest = {}
    mf = src / "manifest.json"
    if mf.exists():
        try:
            manifest = json.loads(mf.read_text())
        except Exception:
            pass

    GEN.mkdir(parents=True, exist_ok=True)
    rows, seen = [], set()
    for f in sorted(src.rglob("*")):
        if not (f.is_file() and f.suffix.lower() in EXT) or f.name.startswith("."):
            continue
        rel = f.relative_to(src)
        excl = set(cfg.get("exclude", []))
        if any(p.startswith(".") or p == "node_modules" or p in excl for p in rel.parts):
            continue
        flat = "__".join(rel.parts)
        seen.add(flat)
        dst = GEN / flat
        if not (dst.exists() and dst.stat().st_size == f.stat().st_size):
            shutil.copy2(f, dst)
        mtime = manifest.get(f.name, {}).get("generiert", f.stat().st_mtime)
        rows.append({
            "src": f"creatives/_gen/{flat}",
            "name": f.name,
            "file": str(rel),
            "quelle": rel.parts[0] if len(rel.parts) > 1 else "Creatives",
            "mtime": int(mtime),
        })

    # verwaiste Kopien entfernen (Quelle ist die Wahrheit)
    for g in GEN.iterdir():
        if g.is_file() and g.name not in seen:
            g.unlink()

    # Landingpages: HTML-Dateien im konfigurierten public-Unterordner (+1 Ebene tief)
    lps = []
    lp_cfg = cfg.get("landingpages") or {}
    if lp_cfg.get("dir"):
        lp_dir = ROOT / "public" / lp_cfg["dir"]
        if lp_dir.is_dir():
            for h in sorted(list(lp_dir.glob("*.html")) + list(lp_dir.glob("*/*.html"))):
                rel = h.relative_to(ROOT / "public")
                name = (lp_cfg.get("namen") or {}).get(str(rel_name := h.name)) or h.stem.replace("-", " ").replace("_", " ").strip().title()
                if h.stem == "index":
                    name = ("Übersicht" if h.parent == lp_dir else h.parent.name.replace("-", " ").title() + " — Übersicht")
                lps.append({"name": name, "href": str(rel), "gruppe": ("Hauptvarianten" if h.parent == lp_dir else h.parent.name)})
            lps.sort(key=lambda l: (l["gruppe"] != "Hauptvarianten", l["gruppe"], l["name"]))

    rows.sort(key=lambda r: -r["mtime"])
    quellen = sorted({r["quelle"] for r in rows})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "// AUTOGENERIERT von scripts/gen-creatives.py — nicht von Hand editieren\n"
        f"export const meta = {json.dumps({'titel': cfg.get('titel', 'Creative-Portal'), 'quellen': quellen, 'extras': cfg.get('extras', []), 'zip': (cfg.get('landingpages') or {}).get('zip'), 'copyBtn': cfg.get('pfad_kopieren', True)}, ensure_ascii=False)};\n"
        f"export const timeline = {json.dumps(rows, ensure_ascii=False)};\n"
        f"export const landingpages = {json.dumps(lps, ensure_ascii=False)};\n"
    )
    log(f"{len(rows)} Bilder indexiert aus {src} → {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
