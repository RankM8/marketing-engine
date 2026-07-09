#!/usr/bin/env python3
"""Verarbeitet rohe Meta-Ad-Library-Ads zur Winning-Ads-Datenbank.

Extrahiert Felder, berechnet Laufzeit (= Winning-Signal), filtert auf eine
Branche, rankt nach Laufzeit und laedt die Creatives der Top-Ads.

Die Branchenfilter sind bewusst leer voreingestellt, damit der Skill in jeder Branche
funktioniert. Ohne --brands und --keywords gilt jede Ad als relevant. Sobald einer der
beiden gesetzt ist, muss eine Ad ihn erfuellen.

Aufruf:
  python3 process.py --in fb_ads_raw.json --out winning-ads.json \
      --img-dir ./creatives --today 2026-06-25 --top 20 \
      --brands "atletica,bowflex" --keywords "hantel,dumbbell,home gym" \
      --exclude-terms "trainingsplan,coaching,abo" --blacklist "irgendeine-app"
"""
from __future__ import annotations
import argparse, json, os, re, sys, urllib.request
from collections import Counter
from datetime import date, datetime

def ts_to_date(ts):
    try: return datetime.fromtimestamp(int(ts)).date()
    except Exception: return None

def download(url, dest):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r, open(dest, "wb") as f:
            f.write(r.read())
        return os.path.getsize(dest) > 1024
    except Exception:
        return False

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--img-dir", required=True)
    ap.add_argument("--today", default=date.today().isoformat())
    ap.add_argument("--top", type=int, default=20, help="so viele Top-Ads mit Creative laden")
    ap.add_argument("--brands", default="", help="kommagetrennte Branchen-Brands (Whitelist)")
    ap.add_argument("--keywords", default="",
                    help="kommagetrennte Branchen-Keywords. Leer = kein Keyword-Filter.")
    ap.add_argument("--exclude-terms", default="",
                    help="Begriffe, die eine Ad ausschliessen, sofern der Advertiser keine "
                         "Whitelist-Brand ist. Fuer Fitness z. B. 'trainingsplan,coaching,abo'.")
    ap.add_argument("--blacklist", default="", help="Advertiser auszuschliessen (kommagetrennt)")
    args = ap.parse_args()

    today = date.fromisoformat(args.today)
    os.makedirs(args.img_dir, exist_ok=True)
    brands = {b.strip().lower() for b in args.brands.split(",") if b.strip()}
    kw = [k.strip().lower() for k in args.keywords.split(",") if k.strip()]
    exclude = [k.strip().lower() for k in args.exclude_terms.split(",") if k.strip()]
    blacklist = {b.strip().lower() for b in args.blacklist.split(",") if b.strip()}

    # Ohne Whitelist zaehlt jede Ad als relevant. Sonst wuerde ein leerer Filter
    # alles verwerfen statt nichts.
    no_whitelist = not brands and not kw
    if no_whitelist:
        print("[winning-ads] Hinweis: kein --brands/--keywords gesetzt, es wird nicht auf eine "
              "Branche gefiltert. Erwarte branchenfremde Treffer.", flush=True)

    ads = json.load(open(args.inp))
    out = []
    for a in ads:
        snap = a.get("snapshot", {}) or {}
        body = snap.get("body") or {}
        text = (body.get("text") if isinstance(body, dict) else str(body)) or ""
        adv = a.get("pageName") or snap.get("pageName") or "?"
        start = ts_to_date(a.get("startDate")); end = ts_to_date(a.get("endDate"))
        active_days = ((end or today) - start).days if start else None
        vids = snap.get("videos") or []; imgs = snap.get("images") or []; cards = snap.get("cards") or []
        creative = media = None
        if vids: creative, media = vids[0].get("videoPreviewImageUrl"), "video"
        elif imgs: creative, media = imgs[0].get("originalImageUrl") or imgs[0].get("resizedImageUrl"), "image"
        elif cards: creative, media = cards[0].get("videoPreviewImageUrl") or cards[0].get("originalImageUrl"), "video"
        low = (text + " " + adv).lower()
        is_template = "{{" in (text or "") or "{{" in (snap.get("title") or "")
        is_brand = adv.lower() in brands or any(b in adv.lower() for b in brands)
        has_kw = any(k in low for k in kw)
        is_excluded = any(k in low for k in exclude)
        in_scope = no_whitelist or is_brand or has_kw
        relevant = (in_scope and not (is_excluded and not is_brand)
                    and adv.lower() not in blacklist and not is_template)
        out.append({"advertiser": adv, "text": text.strip()[:600], "title": snap.get("title"),
                    "cta": snap.get("ctaText"), "linkUrl": snap.get("linkUrl"), "media": media,
                    "creativeUrl": creative, "startDate": start.isoformat() if start else None,
                    "activeDays": active_days, "collationCount": a.get("collationCount") or 1,
                    "platforms": a.get("publisherPlatform") or [],
                    "fbLink": f"https://www.facebook.com/ads/library/?id={a.get('adArchiveID') or a.get('adArchiveId')}",
                    "relevant": relevant, "img": None})

    rel = [x for x in out if x["relevant"] and x["activeDays"] is not None]
    rel.sort(key=lambda x: (-(x["activeDays"] or 0), -(x["collationCount"] or 0)))
    loaded = 0
    for i, x in enumerate(rel[: args.top]):
        if x["creativeUrl"]:
            fn = f"ad-{i+1:02d}-{re.sub(r'[^a-z0-9]+','-',x['advertiser'].lower())[:20]}.jpg"
            if download(x["creativeUrl"], os.path.join(args.img_dir, fn)):
                x["img"] = fn; loaded += 1

    data = {"source": "Facebook/Meta Ad Library", "scrapedAt": args.today,
            "totalScraped": len(out), "relevantCount": len(rel),
            "topCtas": Counter(x["cta"] for x in rel if x["cta"]).most_common(8),
            "topAdvertisers": Counter(x["advertiser"] for x in rel).most_common(12),
            "ads": rel}
    json.dump(data, open(args.out, "w"), ensure_ascii=False, indent=2)
    print(f"[winning-ads] {len(out)} gescraped · {len(rel)} relevant · {loaded} Creatives → {args.out}")
    print("Top:", [(x["advertiser"], f"{x['activeDays']}d") for x in rel[:8]])
    return 0

if __name__ == "__main__":
    sys.exit(main())
