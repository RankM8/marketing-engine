#!/usr/bin/env python3
"""Gib den Struct-Prompt eines Konzept-JSONs als image_gen-fertigen Text aus.

Die Konzept-JSONs tragen die Prompts als strukturierte Objekte
(prompt_basis_struct / prompt_design_struct, siehe references/struct-prompt-format.md).
An image_gen geht der Block als JSON-Text — dieses Script macht die Uebergabe
deterministisch (und prueft nebenbei, dass Copy und Struct-Texte uebereinstimmen).

Usage:
  make_struct_prompt.py --konzept pfad/zum/konzept.json --step basis|design
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--konzept", required=True, type=Path)
    ap.add_argument("--step", required=True, choices=["basis", "design"])
    args = ap.parse_args()

    j = json.loads(args.konzept.read_text())
    key = f"prompt_{args.step}_struct"
    spec = j.get(key)
    if not spec:
        sys.exit(f"FEHLER: {args.konzept} hat kein Feld {key} — Konzept erst migrieren "
                 "(siehe references/struct-prompt-format.md)")

    if args.step == "design":
        copy = j.get("copy", {})
        el = spec.get("elements", {})
        headline = copy.get("headline", "")
        struct_lines = [el.get("headline", {}).get(k, {}).get("text", "")
                        for k in ("line_1", "line_2")]
        struct_headline = "\n".join(s for s in struct_lines if s)
        checks = [
            (headline, struct_headline, "headline"),
            (copy.get("sub", ""), el.get("subline", {}).get("text", ""), "sub"),
            (copy.get("price", ""), el.get("price_block", {}).get("pill", {}).get("text", ""), "price"),
            (copy.get("strike", ""), el.get("price_block", {}).get("strike_price", {}).get("text", ""), "strike"),
            (copy.get("discount", ""), el.get("discount_badge", {}).get("text", ""), "discount"),
        ]
        for soll, ist, name in checks:
            if soll and ist and soll != ist:
                sys.exit(f"FEHLER: copy.{name} != Struct-Text\n  copy:   {soll!r}\n  struct: {ist!r}\n"
                         "Konzept-JSON ist die Quelle — Struct-Feld nachziehen.")

    print(json.dumps(spec, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
