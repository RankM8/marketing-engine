---
name: marktplatz-scrape
description: This skill should be used when the user asks to "scrape Galaxus", "scrape a marketplace", "get competitor prices", "Konkurrenzpreise holen", "Marktplatz scrapen", "Preisvergleich erstellen", or wants to map who sells a product category and at what price. Scrapes competitor products and prices from Swiss online marketplaces via Apify's rag-web-browser with browser rendering — the robust path when dedicated GraphQL scrapers break. Returns structured product data (brand, name, CHF price, link). Requires APIFY_TOKEN.
---

# marktplatz-scrape

Holt Konkurrenzprodukte + Preise von CH-Marktplätzen für die Wettbewerbsanalyse.

## Warum so

Dedizierte Marktplatz-Actors (z. B. `santamaria-automations/galaxus-ch-scraper`)
brechen, sobald der Marktplatz seine interne GraphQL-API ändert (hardcodierte
Query-IDs werden stale). Der **robuste Weg** ist `apify/rag-web-browser` mit
`scrapingTool: "browser-playwright"` — er rendert die Seite wie ein Browser und
liefert Markdown, das wir parsen. So bleibt der Skill stabil.

## Voraussetzungen

- `APIFY_TOKEN` in der Umgebung (Apify-Account). **Nie ins Repo committen.**
- Python 3 (nur stdlib).

```bash
test -n "$APIFY_TOKEN" || { echo "APIFY_TOKEN fehlt"; exit 1; }
```

## Workflow

1. **Such-/Kategorie-URL holen:** Im Browser den Marktplatz durchsuchen (z. B.
   Galaxus „verstellbare hantel") und die URL kopieren — z. B.
   `https://www.galaxus.ch/de/search?q=verstellbare%20hantel`.
2. **Scrapen:**

```bash
APIFY_TOKEN=$APIFY_TOKEN python3 ${CLAUDE_PLUGIN_ROOT}/skills/marktplatz-scrape/scripts/scrape.py \
  --url "https://www.galaxus.ch/de/search?q=verstellbare%20hantel" \
  --out Kunden/<Kunde>/Research/marketplace-data/galaxus-<kategorie>.json \
  --source galaxus --max 50 --wait 8
```

3. **Auswerten:** Das JSON (brand, name, priceChf, url) für Preis-Positionierung,
   Konkurrenz-Tabelle und Sourcing nutzen — oder direkt an `research-to-portal`
   übergeben.

## Output

`<out>.json`:
```json
{ "source":"galaxus", "url":"…", "count":48,
  "method":"apify/rag-web-browser (browser-playwright)",
  "products":[{"brand":"Bowflex","name":"…","priceChf":219,"url":"…"}] }
```

## Parameter

- `--url` (Pflicht) — Such-/Kategorie-URL des Marktplatzes.
- `--source` — Parser. Default `galaxus`. Weitere CH-Marktplätze (toppreise,
  decathlon, idealo) als zusätzliche Parser in `scripts/scrape.py` ergänzen
  (`PARSERS`-Dict) — Vorgehen: einmal mit `--save-markdown` rohes Markdown
  sichern, Produktblock-Muster erkennen, Parser nach dem Galaxus-Vorbild schreiben.
- `--max` — max. Produkte (Default 50). `--wait` — JS-Renderzeit in Sek. (Default 8;
  bei 0 Treffern erhöhen). `--save-markdown` — rohes Markdown zum Debuggen sichern.

## Qualität / Fallstricke

- **0 Produkte** → meist falsche URL oder zu kurze `--wait`. Mit `--save-markdown`
  prüfen, ob die Seite geladen hat, und Parser/Selektor anpassen.
- Preise als Momentaufnahme behandeln (Marktplatzpreise fluktuieren, Aktionen!).
- Bewertungen/Reviews liefert die Listenseite oft nicht — dafür einzelne
  Produktseiten nachladen (gleicher rag-web-browser-Weg).
- **Nie** Margen/interne Daten mit Scrape-Daten vermischen, wenn der Output publiziert wird.
