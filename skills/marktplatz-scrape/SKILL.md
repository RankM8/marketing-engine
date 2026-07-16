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

- `APIFY_TOKEN` in der Umgebung (Apify-Firmen-Account). Den Token **nie in Chats
  einfuegen oder ins Repo committen**. In der Projekt-/Ordner-Konfiguration
  hinterlegen, z. B. in einer ignorierten `.env` oder ueber einen
  `AGENTS.md`-Verweis auf die lokale Secret-Konfiguration.
- Python 3 (nur stdlib).

Vor allen Aufrufen zuerst den vorhandenen Python-Launcher pruefen und danach im
gesamten Workflow konsequent denselben verwenden:

macOS/Linux:

```bash
python3 --version
python --version
```

Windows PowerShell:

```powershell
py --version
python --version
python3 --version
```

Nur vorhandene Launcher verwenden. Die Token-Pruefung ist plattformneutral im
Skript enthalten; fehlt die Variable, beendet es sich mit einer Fehlermeldung.

Vor der Actor-Auswahl [references/actor-auswahl.md](references/actor-auswahl.md)
lesen. Dort stehen der verpflichtende Mini-Test, die Schema-/Kostenpruefung sowie
die Galaxus- und Decathlon-Learnings vom 16.07.2026.

## Workflow

1. **Such-/Kategorie-URL holen:** Im Browser den Marktplatz durchsuchen (z. B.
   Galaxus „verstellbare hantel") und die URL kopieren — z. B.
   `https://www.galaxus.ch/de/search?q=verstellbare%20hantel`.
2. **Scrapen:** Zuerst nur einen kleinen Lauf (`--max 5`) ausfuehren. Pfade in
   Anfuehrungszeichen setzen; das Skript legt fehlende Ausgabeordner an.

macOS/Linux (wenn `python3` bei der Launcher-Pruefung funktioniert hat):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/marktplatz-scrape/scripts/scrape.py" \
  --url "https://www.galaxus.ch/de/search?q=verstellbare%20hantel" \
  --out Kunden/<Kunde>/Research/marketplace-data/galaxus-<kategorie>.json \
  --source galaxus --max 5 --wait 8
```

Windows PowerShell (wenn `py` bei der Launcher-Pruefung funktioniert hat):

```powershell
py "$env:CLAUDE_PLUGIN_ROOT\skills\marktplatz-scrape\scripts\scrape.py" `
  --url "https://www.galaxus.ch/de/search?q=verstellbare%20hantel" `
  --out "Kunden\<Kunde>\Research\marketplace-data\galaxus-<kategorie>.json" `
  --source galaxus --max 5 --wait 8
```

Falls stattdessen `python` oder `python3` vorhanden ist, in der passenden Variante
nur den Launcher ersetzen. PowerShells Backtick dient hier lediglich der
Lesbarkeit; derselbe Befehl kann ohne Backticks in einer Zeile ausgefuehrt werden.
Nach erfolgreichem Mini-Test `--max` nur bei verifiziertem Bedarf erhoehen.

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
- Keine Monats-Abos ohne verifizierten Bedarf kaufen. Vor jedem Kauf klaeren,
  welches Problem der Actor genau loest; Details siehe
  [Actor-Auswahl](references/actor-auswahl.md).
