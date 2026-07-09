#!/usr/bin/env python3
"""Erzeuge EIN Produktbild ueber OpenAIs gpt-image-Familie, wahlweise via OpenRouter oder fal.ai.

Ohne --ref-image: Text-zu-Bild.
Mit einer oder mehreren --ref-image: referenzgefuehrt (fal nennt das /edit). Das Modell
ankert stark auf dem Eingabebild - das ist die Grundlage der BACKGROUND-SWAP-Methode.
Reihenfolge zaehlt: sauberstes Produktfoto zuerst.

Gateway-Wahl:
    --gateway openrouter   (Default) ~1024^2, --aspect-ratio steuert nur die Komposition
    --gateway fal          echte Leinwandgroessen; --image-size bis 3840px (nur gpt-image-2)

Beispiele:
    # Background-Swap, echtes Produktfoto als Referenz, ohne Typografie
    generate.py --prompt "..." --output base.png --ref-image original.jpg --no-text

    # Storyboard-Bogen in echter Groesse
    generate.py --prompt "..." --output sheet.png \
        --gateway fal --model gpt-image-2 --image-size 1728x2304 --quality high
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gateways import (  # noqa: E402
    DEFAULT_MODEL,
    MODELS,
    fal_download,
    fal_generate,
    load_key,
    models_for,
    openrouter_generate,
    round16,
    write_meta,
)

# OpenRouter kennt keinen harten Groessen-Parameter, das Verhaeltnis wird ueber den
# Prompt gesteuert. Die Ausgabe bleibt trotzdem ~quadratisch - siehe SKILL.md.
AR_HINT = {
    "1:1": "a perfectly square 1:1",
    "4:5": "a vertical 4:5 portrait",
    "9:16": "a tall 9:16 vertical (story/reels)",
    "16:9": "a wide 16:9 landscape",
    "2:3": "a vertical 2:3 portrait",
}

NO_TEXT_CLAUSE = (
    "\nDo NOT render any text, letters, words, numbers, prices or logos as typography "
    "in the image. Produce a purely visual scene; copy will be added separately."
)


def _parse_size(spec: str) -> tuple[int, int]:
    try:
        w, h = spec.lower().split("x")
        return int(w), int(h)
    except Exception:
        sys.exit(f"ERROR: --image-size erwartet BREITExHOEHE (z. B. 1728x2304), bekam: {spec}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--gateway", default="openrouter", choices=["openrouter", "fal"],
                    help="openrouter (Default): quadratisch, guenstig, staerkstes Ankern. "
                         "fal: echte Ausgabegroessen.")
    ap.add_argument("--model", default=None,
                    help=f"Default je Gateway: {DEFAULT_MODEL}. "
                         f"openrouter: {models_for('openrouter')} · fal: {models_for('fal')}")
    ap.add_argument("--aspect-ratio", default="1:1",
                    help="Bei openrouter ein Kompositions-Hinweis, bei fal die echte Leinwand.")
    ap.add_argument("--image-size", default=None,
                    help="Explizit BREITExHOEHE. Nur fal + gpt-image-2; sonst ignoriert.")
    ap.add_argument("--quality", default="high", choices=["low", "medium", "high"])
    ap.add_argument("--ref-image", action="append", type=Path, default=[],
                    help="Referenzbild, wiederholbar. Sauberstes Produktfoto zuerst.")
    ap.add_argument("--no-text", action="store_true",
                    help="Modell soll KEINE Typografie rendern (Copy spaeter per Overlay).")
    ap.add_argument("--with-logs", action="store_true", help="fal-Queue-Logs mitschreiben.")
    args = ap.parse_args()

    model_name = args.model or DEFAULT_MODEL[args.gateway]
    if model_name not in MODELS:
        sys.exit(f"ERROR: unbekanntes Modell '{model_name}'. Verfuegbar: {list(MODELS)}")
    cfg = MODELS[model_name]
    if cfg["gateway"] != args.gateway:
        sys.exit(f"ERROR: Modell '{model_name}' laeuft ueber '{cfg['gateway']}', "
                 f"nicht ueber '{args.gateway}'. Setze --gateway {cfg['gateway']}.")

    for r in args.ref_image:
        if not Path(r).exists():
            sys.exit(f"ERROR: Referenzbild nicht gefunden: {r}")

    key = load_key(args.gateway)
    variant = "edit" if args.ref_image else "text-to-image"
    prompt = args.prompt.rstrip()
    if args.no_text:
        prompt += NO_TEXT_CLAUSE

    args.output.parent.mkdir(parents=True, exist_ok=True)

    if args.gateway == "openrouter":
        if args.aspect_ratio not in AR_HINT:
            sys.exit(f"ERROR: --aspect-ratio {args.aspect_ratio} wird von openrouter nicht "
                     f"unterstuetzt. Moeglich: {list(AR_HINT)}")
        if args.image_size:
            print("[generate] WARNUNG: --image-size wirkt nur mit --gateway fal --model gpt-image-2. "
                  "Wird ignoriert.", flush=True)
        prompt += (f"\n\nOutput format: {AR_HINT[args.aspect_ratio]} aspect ratio, "
                   f"high resolution, {args.quality} quality.")

        print(f"[openrouter] {cfg['id']} · {variant} · refs={len(args.ref_image)} · "
              f"ar={args.aspect_ratio}", flush=True)
        img, usage = openrouter_generate(cfg["id"], prompt, args.ref_image, key)
        args.output.write_bytes(img)
        if args.output.stat().st_size < 1024:
            sys.exit(f"ERROR: Ausgabe verdaechtig klein ({args.output.stat().st_size} Bytes)")

        write_meta(args.output, gateway="openrouter", model=cfg["id"], model_family=model_name,
                   variant=variant, prompt=prompt, aspect_ratio=args.aspect_ratio,
                   quality=args.quality, no_text=args.no_text,
                   ref_images=[str(r) for r in args.ref_image] or None,
                   cost_usd=usage.get("cost"), usage=usage)
        print(f"[openrouter] {len(img)} Bytes -> {args.output} · Kosten: ${usage.get('cost')}",
              flush=True)
        return 0

    # --- fal --------------------------------------------------------------- #
    if args.image_size:
        w, h = _parse_size(args.image_size)
        if not cfg["custom_size"]:
            allowed = sorted({f"{x}x{y}" for x, y in cfg["size_by_ar"].values()})
            print(f"[fal] WARNUNG: {model_name} kennt keine freien Groessen. Nutze die "
                  f"Zuordnung ueber --aspect-ratio. Erlaubt waeren: {allowed}", flush=True)
            w, h = cfg["size_by_ar"].get(args.aspect_ratio, (1024, 1536))
        else:
            w, h = round16(w), round16(h)
            if max(w, h) > 3840:
                sys.exit(f"ERROR: Groesse ueberschreitet das 3840px-Limit: {w}x{h}")
    else:
        wh = cfg["size_by_ar"].get(args.aspect_ratio)
        if not wh:
            sys.exit(f"ERROR: {model_name} unterstuetzt --aspect-ratio {args.aspect_ratio} nicht. "
                     f"Moeglich: {list(cfg['size_by_ar'])}")
        w, h = wh

    url, payload, result = fal_generate(cfg, prompt, args.ref_image, width=w, height=h,
                                        quality=args.quality, with_logs=args.with_logs)
    nbytes = fal_download(url, args.output)
    cost = cfg["cost_by_quality"][args.quality]

    write_meta(args.output, gateway="fal", model=cfg["edit"] if args.ref_image else cfg["t2i"],
               model_family=model_name, variant=variant, prompt=prompt,
               aspect_ratio=args.aspect_ratio, image_size=f"{w}x{h}", quality=args.quality,
               no_text=args.no_text, ref_images=[str(r) for r in args.ref_image] or None,
               image_url=url, request=payload,
               result_meta={k: v for k, v in (result or {}).items() if k != "images"},
               cost_estimate_usd=cost)
    print(f"[fal] {nbytes} Bytes -> {args.output} · geschaetzte Kosten: ${cost:.2f}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
