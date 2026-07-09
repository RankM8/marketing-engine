#!/usr/bin/env python3
"""Scrapt die Meta/Facebook Ad Library über Apify (apify/facebook-ads-scraper).

Aufruf:
  APIFY_TOKEN=... python3 scrape-ads.py --keywords "verstellbare hantel,home gym,kurzhantel" \
      --country DE --out fb_ads_raw.json [--limit 45] [--active]

Liefert rohe Ad-Objekte (mit Laufzeit, Creatives, Text) → weiter mit process.py.
"""
from __future__ import annotations
import argparse, json, os, sys, urllib.parse, urllib.request

APIFY = "https://api.apify.com/v2/acts/apify~facebook-ads-scraper/run-sync-get-dataset-items"

def ad_library_url(keyword: str, country: str, active: bool) -> str:
    q = urllib.parse.quote(keyword)
    status = "active" if active else "all"
    return (f"https://www.facebook.com/ads/library/?active_status={status}"
            f"&ad_type=all&country={country}&q={q}&search_type=keyword_unordered&media_type=all")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keywords", required=True, help="kommagetrennt")
    ap.add_argument("--country", default="DE")
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=45)
    ap.add_argument("--active", action="store_true", default=True)
    ap.add_argument("--all-status", action="store_true", help="auch inaktive Ads")
    args = ap.parse_args()

    token = os.environ.get("APIFY_TOKEN") or os.environ.get("APIFY_API_TOKEN")
    if not token:
        sys.exit("ERROR: APIFY_TOKEN nicht gesetzt (env).")
    active = not args.all_status
    urls = [{"url": ad_library_url(k.strip(), args.country, active)}
            for k in args.keywords.split(",") if k.strip()]
    body = json.dumps({
        "startUrls": urls,
        "resultsLimit": args.limit,
        "activeStatus": "active" if active else "all",
        "isDetailsPerAd": True,
    }).encode()
    print(f"[winning-ads] scrape {len(urls)} keyword-URLs · country={args.country} · active={active}", flush=True)
    req = urllib.request.Request(f"{APIFY}?token={token}", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        data = json.load(r)
    if not isinstance(data, list):
        sys.exit(f"Unerwartete Antwort: {str(data)[:200]}")
    json.dump(data, open(args.out, "w"), ensure_ascii=False)
    print(f"[winning-ads] {len(data)} Ads → {args.out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
