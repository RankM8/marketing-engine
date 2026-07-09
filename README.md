# marketing-engine

Claude-Code-Plugin für den Weg von der Marktrecherche zum fertigen Ad-Creative. Acht Skills,
die aufeinander aufbauen: Konkurrenz scrapen, Recherche belegen, Werbekonzepte ableiten,
Produktbilder mit echter Produkttreue erzeugen, prüfen und im Kundenportal darstellen.

Der Kern ist eine Haltung: **ein Bildmodell erfindet Details, wenn man es lässt.** Die Skills
verhindern das durch die Background-Swap-Methode, harte Referenz-Regeln und ein
Qualitätstor, das ein ehrliches Treue-Urteil erzwingt.

## Installation

```bash
/plugin marketplace add <repo-url>
/plugin install marketing-engine@360webmanager
```

Lokal zum Testen:

```bash
claude --plugin-dir /pfad/zu/marketing-engine
```

## Voraussetzungen

**Python 3** mit Pillow:

```bash
pip3 install pillow
pip3 install fal_client    # nur für --gateway fal
```

**API-Keys** in der Umgebung oder einer `.env` im Verzeichnisbaum. Die Scripts suchen
aufwärts, eine `.env` im Projektwurzelverzeichnis genügt. **Nie committen.**

| Variable | Wofür | Nötig für |
|---|---|---|
| `OPENROUTER_API_KEY` | Bildgenerierung (Standardweg) | `create-product-image` |
| `APIFY_TOKEN` | Marktplatz- und Ad-Library-Scraping | `marktplatz-scrape`, `winning-ads-finder`, `apify-deep-research` |
| `FAL_API_KEY` | Bildgenerierung über fal.ai | nur `--gateway fal` |

Keys holen: [openrouter.ai/keys](https://openrouter.ai/keys) · [apify.com](https://apify.com) ·
[fal.ai/dashboard/keys](https://fal.ai/dashboard/keys)

**Externer Skill:** `produkt-research` und `apify-deep-research` rufen den Skill
**`deep-research`** auf, der **nicht Teil dieses Plugins** ist. Fehlt er, brechen diese beiden
Skills ab. Vor dem ersten Lauf prüfen, ob er verfügbar ist.

## Laufende Kosten

Bildgenerierung wird pro Bild abgerechnet und summiert sich in Batches.

| Weg | Kosten pro Bild |
|---|---|
| OpenRouter, `gpt-5.4-image-2`, hohe Qualität mit Referenzen | ca. **$0.24 bis $0.27** |
| fal, `gpt-image-1` | $0.04 (low) bis $0.20 (high) |
| fal, `gpt-image-2` | ca. $0.02 (low) bis $0.19 (high) |

Ein Batch von 50 Varianten über OpenRouter kostet also rund 12 US-Dollar. Der tatsächliche
Wert steht nach jedem Lauf in der `.meta.json` neben dem Bild (`cost_usd`, bei fal
`cost_estimate_usd`).

Apify rechnet pro Scrape-Lauf nach Compute-Einheiten ab, in der Regel Bruchteile eines Dollars.

## Die Marke konfigurieren

Farben, Schrift und Logos stehen **nicht im Plugin**, sondern in einer `brand.json` im
jeweiligen Kundenverzeichnis. Die Scripts suchen sie vom Arbeitsverzeichnis aufwärts, eine
Datei in `Kunden/<Kunde>/` gilt also für alles darunter.

Vorlage: [`examples/brand.json`](examples/brand.json). Überschreiben mit
`MARKETING_ENGINE_BRAND=/pfad/zu/brand.json`.

Ohne `brand.json` laufen die Scripts mit neutralen Defaults und warnen. Das Ergebnis ist dann
unmarkiert, aber nichts stürzt ab.

Hinweis: Logos müssen als **PNG mit transparentem Hintergrund** vorliegen. Pillow kann kein
SVG öffnen, `composite_logo.py` meldet das explizit.

## Die Skills

**Recherche**

| Skill | Zweck |
|---|---|
| `produkt-research` | Aus Produkt-URL oder Name eine versionierte Markt- und Wettbewerbsrecherche bauen |
| `marktplatz-scrape` | Konkurrenzprodukte und Preise von Marktplätzen holen |
| `winning-ads-finder` | Langlaufende Konkurrenz-Ads aus der Meta Ad Library finden und Muster extrahieren |
| `apify-deep-research` | Primärdaten aus dem Scrape mit web-verifizierter Recherche zusammenführen |

**Creatives**

| Skill | Zweck |
|---|---|
| `create-product-image` | Produktbilder erzeugen. Background-Swap, Overlays, Formate, zwei Gateways |
| `verify-product-image` | Qualitätstor: Maße, Produkttreue, Text, Artefakte |

**Verkettung**

| Skill | Zweck |
|---|---|
| `research-to-creative` | Aus belegten Findings Hooks, Copy und Creatives ableiten |
| `research-to-portal` | Strukturierte Daten als Seite in ein Astro-Kundenportal bringen |

## Ein typischer Durchlauf

```
marktplatz-scrape      →  wer verkauft was zu welchem Preis
winning-ads-finder     →  welche Hooks laufen bei der Konkurrenz seit Monaten
apify-deep-research    →  beides belegen und Widersprüche auflösen
research-to-creative   →  Hooks in Copy und Ad-Konzepte übersetzen
create-product-image   →  Creatives bauen (Background-Swap)
verify-product-image   →  Treue prüfen, Ausschuss verwerfen
research-to-portal     →  Ergebnis durchklickbar dem Kunden zeigen
```

## Grundsätze, die in den Skills stecken

- **Nichts erfinden.** Kein Claim ohne Beleg, keine Halterung ohne Referenzfoto, keine Quelle
  ohne Link.
- **Fakten von Einschätzung trennen.** Unsichere Zahlen als unsicher kennzeichnen.
- **Primärdaten schlagen Web-Inferenz** bei Widerspruch.
- **Ehrliche Treue-Urteile.** Im Zweifel abwerten. Ein "produktnah", das als "echt" durchgeht,
  beschädigt das Vertrauen in die ganze Ablage.
- **Keine vertraulichen Daten** in publizierbarem Output: keine Margen, Einkaufspreise oder
  internen Umsätze.

## Herkunft

`create-product-image` und `verify-product-image` gehen auf Skills aus
[`gooseworks-ai/goose-skills`](https://github.com/gooseworks-ai/goose-skills) zurück
(`create-image-gpt-image-fal`, `verify-product-image`) und wurden hier erheblich erweitert:
OpenRouter-Gateway, Background-Swap-Methode, Overlay-Pipeline, Marken-Entkopplung.

> **Offener Punkt vor Weitergabe:** Die Lizenz der Ursprungs-Skills ist zu prüfen und hier
> zu vermerken.
