# Brand-Guidelines-Integration (Pflicht-Preflight)

Seit 2026-07-16 gilt: **Kein Creative ohne Brand-Abgleich.** Kunden liefern Brand-Manuals
(PDF) mit harten Regeln zu Farben, Typografie und Logo-Placement — Verstöße führen zu
Kunden-Rejections des gesamten Bestands (Fitagon-Fall: Logo-Position + Font + Gelbwert).

## Mechanik

1. **Quelle suchen** (in dieser Reihenfolge): `BRAND.md` im Projekt/Kundenordner →
   `brand.json` (brandkit) → Brand-Manual-PDF im Kundenordner → beim User nachfragen.
2. Die Brand-Werte in die Struct-Prompts einbrennen (Farben als exakte Hex-Werte,
   Font-Charakter in `brand_font`).
3. **Logo NIE generieren lassen** — siehe unten.

## Logo: Vektor-Overlay statt Generierung (Standard seit 2026-07-16)

KI-generierte Wortmarken weichen IMMER minimal von der Referenz ab; Brand-Manuals
verlangen exakte Logos und feste Positionen. Deshalb:

- Im `prompt_design_struct`: **kein `logo`-Element**, stattdessen
  `canvas.reserved_logo_zone`: untere 13 % (bzw. obere 13 % bei Hochformat) komplett
  frei von Text/Pille/Badge + negatives: "no logo, no wordmark, no brand lettering".
- Nach dem QA-Pass: `scripts/brand_logo_overlay.py` setzt das echte Logo-PNG
  (aus SVG exportiert, z. B. `rsvg-convert -w 1600 logo.svg -o logo.png`).
- Zwei Manual-konforme Foto-Varianten: `--variant box` (solide Grau-Box) und
  `--variant stripe` (15 %-Streifen volle Breite + Box). Dem Kunden beide zur Wahl liefern.

## Typische Placement-Matrix (Beispiel Fitagon, generisch verbreitet)

| Format | Regel |
|---|---|
| Poster/Feed (1:1, 4:5) | Logo unten-mittig oder unten-rechts — NIE oben |
| Im Foto | NIE nackt: Grau-Box oder 15%-Stripe (`brand_logo_overlay.py`) |
| Banner/Story (9:16, Hochformat) | Logo OBEN-mittig (`--top`) — Gegenregel zu Postern! |
| Weisser Grund | Logo ohne Box erlaubt, unten-mittig/rechts |

**Achtung Format-Falle:** Feed 1:1 = Poster-Regel (unten), Story 9:16 = Banner-Regel (oben).
Die Regel hängt am FORMAT, nicht am Kanal.

## Farb-Falle: Manual vs. Live-Website

Brand-Manuals und Live-Websites weichen oft ab (Fitagon: Manual #FFE500/#465359,
Website #FFED00/#374F5A). Vorgehen: Diskrepanz dokumentieren, User/Kunde entscheidet,
bis dahin Manual-Werte in Neuproduktion. NIE stillschweigend mischen.

## QA-Erweiterung bei Brand-Pflicht

Zusätzlich zum Standard-QA-Vertrag:
- Kein Logo/Wortmarke im generierten Bild (Overlay kommt danach).
- Reservierte Logo-Zone frei (unten bzw. oben 13 %).
- Gelb-Drift-Check: Marken-Gelb satt und rein (kein Senf/Orange), Soll-Hex aus Brand-Quelle.
- Typo-Charakter entspricht `brand_font` (z. B. Roboto Black: geometrisch, sentence case).
