#!/usr/bin/env python3
"""Scrapt eine Marktplatz-Such-/Kategorieseite über Apify und parst Produktdaten.

Robuster Weg für JS-/GraphQL-geschützte CH-Marktplätze (z. B. Galaxus): nutzt
apify/rag-web-browser mit Browser-Rendering (umgeht Schutz, der dedizierte
GraphQL-Actors bricht) und parst das gerenderte Markdown zu strukturierten Produkten.

Aufruf (mit dem auf dem System verfuegbaren Python-Launcher):
  python3 scrape.py --url "<marktplatz-such-url>" --out out.json
  py scrape.py --url "<marktplatz-such-url>" --out out.json

Quelle der URL: die normale Such-/Kategorie-URL im Browser (z. B.
  https://www.galaxus.ch/de/search?q=verstellbare%20hantel ).
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import urllib.request

APIFY = "https://api.apify.com/v2/acts/apify~rag-web-browser/run-sync-get-dataset-items"

def fetch_markdown(url: str, token: str, wait: int) -> str:
    body = json.dumps({
        "query": url,
        "maxResults": 1,
        "scrapingTool": "browser-playwright",
        "outputFormats": ["markdown"],
        "dynamicContentWaitSecs": wait,
    }).encode("utf-8")
    req = urllib.request.Request(f"{APIFY}?token={token}", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.load(r)
    if not isinstance(data, list) or not data:
        sys.exit(f"Kein Ergebnis von rag-web-browser: {str(data)[:200]}")
    return data[0].get("markdown") or data[0].get("text") or ""

def parse_galaxus(md: str) -> list[dict]:
    """Galaxus-Produktliste aus Markdown: Block je '[](/de/s3/product/<slug>)'."""
    out, seen = [], set()
    for p in re.split(r"\[\]\(/de/s3/product/", md)[1:]:
        slug = p.split(")")[0]
        url = f"https://www.galaxus.ch/de/s3/product/{slug}"
        if url in seen:
            continue
        seen.add(url)
        pm = re.search(r"CHF\s?([\d’']*\d(?:[.,]\d+)?)", p)
        price = float(pm.group(1).replace("’", "").replace("'", "").replace(",", ".")) if pm else None
        bm = re.search(r"\*\*([^*]+)\*\*\s*([^\n\[]+)", p)
        am = re.search(r"!\[([^\]]+)\]", p)
        name = am.group(1).strip() if am else (bm.group(2).strip() if bm else "")
        out.append({"brand": bm.group(1).strip() if bm else None,
                    "name": name, "priceChf": price, "url": url})
    return out

PARSERS = {"galaxus": parse_galaxus}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="Marktplatz-Such-/Kategorie-URL")
    ap.add_argument("--out", required=True)
    ap.add_argument("--source", default="galaxus", choices=list(PARSERS))
    ap.add_argument("--max", type=int, default=50)
    ap.add_argument("--wait", type=int, default=8, help="Sekunden für JS-Rendering")
    ap.add_argument("--save-markdown", help="optional: rohes Markdown hierhin sichern")
    args = ap.parse_args()

    token = os.environ.get("APIFY_TOKEN") or os.environ.get("APIFY_API_TOKEN")
    if not token:
        sys.exit("ERROR: APIFY_TOKEN nicht gesetzt (env).")

    print(f"[marktplatz-scrape] rag-web-browser: {args.url}", flush=True)
    md = fetch_markdown(args.url, token, args.wait)
    if args.save_markdown:
        markdown_path = Path(args.save_markdown)
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(md, encoding="utf-8")
    products = PARSERS[args.source](md)[: args.max]
    if not products:
        sys.exit("Keine Produkte geparst - URL pruefen oder --wait erhoehen. "
                 "(Markdown via --save-markdown inspizieren.)")
    data = {"source": args.source, "url": args.url, "count": len(products),
            "method": "apify/rag-web-browser (browser-playwright)", "products": products}
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as output_file:
        json.dump(data, output_file, ensure_ascii=False, indent=2)
        output_file.write("\n")
    prices = [p["priceChf"] for p in products if p["priceChf"]]
    print(f"[marktplatz-scrape] {len(products)} Produkte -> {output_path}")
    if prices:
        print(f"  Preisspanne CHF {min(prices):.0f}-{max(prices):.0f}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
