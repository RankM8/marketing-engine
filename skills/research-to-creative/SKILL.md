---
name: research-to-creative
description: This skill should be used when an existing research report or marketing brief should become testable ads — "make ads from this research", "turn the research into creatives", "Ads aus der Recherche bauen", "Hooks in Ad-Copy übersetzen". Requires verified findings as input. Derives hooks and angles, writes Swiss-German Meta-compliant copy, then generates creatives via create-product-image and bundles everything into an ad briefing. For image generation alone, without a research brief, use create-product-image directly.
---

# research-to-creative

Schliesst den Bogen von der Recherche zur fertigen Anzeige: aus **verifizierten
Hooks** werden Ad-Konzepte, Copy (CH-Deutsch) und Bild-Creatives.

## Inputs

- Ein Research-/Marketing-Brief mit belegten **Hooks/Winkeln** und **Einwänden**
  (z. B. aus `deep-research` / `apify-deep-research`).
- Echte **Produktfotos** als Referenz (für `create-product-image`).
- Zielplattform/-format (Meta Feed 1:1 oder 4:5).

## Workflow

1. **Hooks ableiten:** Aus den Findings 3–5 konkrete Werbe-Winkel ziehen — je einer
   pro echtem Kaufgrund / Einwand-Konter. Nur **belegte** Aussagen; keine erfundenen
   Claims, keine Defekt-Behauptungen gegen Wettbewerber, keine Gesundheitsversprechen.
2. **Copy schreiben:** Pro Hook Primärtext + Überschrift (≤40 Z.) + Beschreibung
   (≤30 Z.) + CTA, CH-Deutsch (du-Form, „ss", CHF). Show-don't-tell, konkrete Zahlen.
   Ablegen wie die bestehenden Ad-Briefings in `Kunden/<Kunde>/Meta-Ads/`.
3. **Creatives generieren** mit dem Skill **`create-product-image`**:
   - Szene reference-guided aus Produktfotos (multi-ref = beste Produkttreue).
   - Text wahlweise im Bild ODER `--no-text` + `overlay_text.py` für perfekte
     Marken-Typografie (Headline + Preis-Badge).
   - QC mit `verify-product-image`.
4. **Bündeln:** Pro Konzept Copy + Creative zusammen ablegen; optional via
   `research-to-portal` als Creatives-/Ads-Sektion ins Portal.

## Outputs

- Ad-Briefing (Hooks + Copy je Variante) in `Meta-Ads/`.
- Bild-Creatives (+ `.meta.json`) in `Meta-Ads/creatives/<produkt>/`.

## Leitlinien

- **Differenzierung aus der Research treiben:** Wenn der Preis nicht alleinstellt,
  über die belegten echten Vorteile texten (z. B. Präzision, CH-Lager, Sicherheit).
- **A/B von Anfang an:** pro Hook mind. 2 Varianten (z. B. Platz vs. Angebot).
- **Konsistenz:** Marke, Farben, Tonalität wie im restlichen Material.
- **Nichts erfinden** — jeder Claim muss im Brief belegt sein.

## Verwandte Skills

`create-product-image` (Bilder) · `verify-product-image` (QC) ·
`deep-research`/`apify-deep-research` (Input) · `research-to-portal` (Darstellung).
