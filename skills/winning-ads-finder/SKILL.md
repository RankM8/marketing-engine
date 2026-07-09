---
name: winning-ads-finder
description: This skill should be used when the user asks to "find winning ads", "analyze competitor ads", "check the Meta Ad Library", "Konkurrenz-Ads analysieren", "Winning Ads finden", "was für Ads laufen bei der Konkurrenz", or wants ad inspiration and proven hooks before launching campaigns. Scrapes active ads by keyword and country via Apify, ranks them by run duration (the best public profitability signal — ads running for months are almost always profitable), filters to the relevant industry, extracts patterns/hooks/CTAs and downloads creatives. Requires APIFY_TOKEN.
---

# winning-ads-finder

Baut eine **Winning-Ads-Datenbank** aus der Meta Ad Library: welche Konkurrenz-Ads
laufen lange (= profitabel), mit welchen Hooks, Formaten und Offers.

## Prinzip

Die Meta Ad Library zeigt für jede Ad das Startdatum und ob sie aktiv ist.
**Laufzeit (Tage aktiv) + Anzahl paralleler Varianten** sind die besten öffentlich
verfügbaren Profitabilitäts-Signale: Eine Ad, die seit Monaten läuft und in mehreren
Varianten getestet wird, verdient fast sicher Geld. Danach ranken wir.

## Voraussetzungen

- `APIFY_TOKEN` in der Umgebung. **Nie ins Repo committen.**
- Python 3 (stdlib).

## Workflow (2 Schritte)

**1. Scrapen** — `apify/facebook-ads-scraper` (offiziell, sehr zuverlässig):

```bash
APIFY_TOKEN=$APIFY_TOKEN python3 ${CLAUDE_PLUGIN_ROOT}/skills/winning-ads-finder/scripts/scrape-ads.py \
  --keywords "verstellbare hantel,home gym,kurzhantel" --country DE \
  --out /tmp/fb_ads_raw.json --limit 45
```
> Tipp: `country=DE` liefert in der EU dank DSA volle Ad-Transparenz (mehr als CH).
> Mehrere Keywords = breitere Konkurrenz-Abdeckung.

**2. Verarbeiten** — ranken, filtern, Creatives laden:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/winning-ads-finder/scripts/process.py \
  --in /tmp/fb_ads_raw.json \
  --out <kunde>/winning-ads.json \
  --img-dir <portal>/public/winning-ads \
  --today $(date +%F) --top 20 \
  --brands "atletica,nüo,bowflex,gymbeam,eleiko,freak athlete,ironmaster" \
  --keywords "hantel,dumbbell,kettlebell,rack,home gym,gewicht,equipment" \
  --exclude-terms "app ,trainingsplan,coaching,challenge,abo,kalorien,mitgliedschaft" \
  --blacklist "muscle monster app,betterme men"
```

Die Filter sind **branchenneutral voreingestellt**, also leer. Ohne `--brands` und
`--keywords` gilt jede Ad als relevant (das Script warnt dann). Sobald einer der beiden
gesetzt ist, muss eine Ad ihn erfuellen. `--exclude-terms` wirft Ads raus, die zwar das
Keyword treffen, aber am Thema vorbeigehen (im Fitness-Umfeld typisch: Trainings-Apps und
Coaching-Abos). Eine Ad eines Whitelist-Brands ueberlebt den Ausschluss immer.
Template-Ads mit `{{platzhalter}}` fliegen ohne Zutun raus.

**3. Darstellen:** Das JSON an `research-to-portal` übergeben → durchklickbare
Winning-Ads-Sektion (Galerie nach Laufzeit, Muster, Learnings).

## Output

`winning-ads.json`: `{ totalScraped, relevantCount, topCtas, topAdvertisers,
ads:[{ advertiser, text, title, cta, media, activeDays, collationCount, platforms,
fbLink, img }] }`. Creatives (Vorschaubilder) liegen im `--img-dir`.

## Muster in den Daten

- **Laufzeit-Ranking** → die echten Winner zuerst.
- **Hooks** aus `title`/`text` (z. B. Mechanik-Demo, All-in-One/Platz, Dringlichkeit).
- **Offer-Mechaniken** (Rabatt-Codes, „solange Vorrat").
- **Format** (`media`, `collationCount`) → Video dominiert, Varianten = Skalierung.
- **CTAs** (`topCtas`) → was die Kategorie nutzt.

## Fallstricke

- **Relevanz-Filter justieren:** Keyword-Suchen ziehen artfremde Werbung rein, im
  Fitness-Umfeld vor allem Apps und Trainingsprogramme. Über `--brands` (Whitelist echter
  Hersteller), `--keywords`, `--exclude-terms` und `--blacklist` scharf stellen. Ohne
  Whitelist wird nicht gefiltert, das Script weist darauf hin.
- **Creative-URLs** der fbcdn laufen ab → das Script lädt sie sofort lokal; nicht die
  URLs speichern, sondern die heruntergeladenen Bilder verwenden.
- Reichweite/Spend liefert die Library nur teils (EU) — Laufzeit ist das stabilste Signal.
