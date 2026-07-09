---
name: apify-deep-research
description: This skill should be used specifically when real scraped marketplace data must be combined and cross-validated with web research — "validate the pricing research with real Galaxus data", "combine scrape and research", "Wettbewerbsanalyse mit echten Marktplatzpreisen", "Scrape-Daten gegen die Recherche prüfen". Combines Apify primary-data scraping (hard numbers: real products and prices) with the deep-research web workflow (cited, adversarially verified findings) into one consolidated report, resolving contradictions in favour of the scrape. For research from a product URL or name without a marketplace scrape, use produkt-research instead. Requires APIFY_TOKEN and the separate deep-research skill.
---

# apify-deep-research

> **Voraussetzung:** Dieser Skill ruft den separaten **`deep-research`**-Skill auf, der
> nicht Teil dieses Plugins ist. Fehlt er, bricht Schritt 2 ab. Verfügbarkeit vorab prüfen.

Orchestriert **Primärdaten (Apify-Scrape)** und **web-verifizierte Recherche
(`deep-research`)** zu einem konsolidierten, quellenbelegten Report. Primärdaten
liefern die harten Zahlen, Deep Research prüft und ergänzt sie — beides zusammen
schlägt jede einzelne Methode (Beispiel: Galaxus-Scrape deckte auf, dass ein
„widerlegter" Konkurrent real ist).

## Inputs

- Produkt-/Markt-Frage (möglichst konkret), Markt/Land, relevante Marktplatz-Quelle(n).

## Workflow

1. **Primärdaten scrapen** mit `marktplatz-scrape` (z. B. Galaxus-Kategorie) →
   echte Konkurrenzprodukte + Preise als JSON. Optional `winning-ads-finder` für
   die Werbeseite.
2. **Web validieren** mit dem `deep-research`-Workflow: die zentralen Claims
   (Wettbewerber-Preise, Positionierung, Reviews/Beschwerden, Mechanik-Standards)
   fan-out recherchieren und adversarial verifizieren lassen.
3. **Konsolidieren:** Scrape-Tabelle (Primärdaten) + Deep-Research-Findings
   (mit Confidence + Quellen) zusammenführen. **Widersprüche auflösen** —
   Primärdaten (live gescrapt) schlagen Web-Inferenz; Korrekturen explizit markieren.
4. **Ausgeben:** als Research-Datei (`Kunden/<Kunde>/Research/<datum>_<thema>/`)
   und via `research-to-portal` als Portal-Seite.

## Outputs

- Konsolidierter Report: Wettbewerber-Tabelle (echte Preise), verifizierte Findings
  (belegt/teils belegt/unsicher), Quellen, Korrekturen, Marketing-Implikationen.

## Prinzipien

- **Fakten von Einschätzung trennen**, Unsicherheiten kennzeichnen, „Widerlegtes" als
  solches markieren (nicht in Entscheidungen einfliessen lassen).
- **Primärdaten > Web-Inferenz** bei Widerspruch.
- **Keine vertraulichen Daten** in publizierbaren Output (Margen etc.).
- Preise als Momentaufnahme behandeln (vor Entscheidungen gegenchecken).

## Verwandte Skills

`marktplatz-scrape` + `winning-ads-finder` (Primärdaten) · `deep-research` (Web) ·
`research-to-portal` (Darstellung) · `research-to-creative` (Aktivierung).
