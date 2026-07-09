---
name: research-to-portal
description: This skill should be used when the user asks to "add this to the portal", "put the research into the portal", "ins Portal übernehmen", "Portal-Seite bauen", or has structured data (marketplace scrape, winning-ads analysis, analytics, research findings) that should become a browsable page in an Astro client portal. Builds KPI cards, tables, findings and galleries using the portal's existing Layout, global.css classes and nav.ts, without inventing a new design system.
---

# research-to-portal

Macht aus strukturierten Daten eine durchklickbare, markenkonforme Portal-Seite.

Setzt ein bestehendes **Astro-Kundenportal** voraus, das dem unten beschriebenen Muster
folgt: ein `Layout.astro`, eine `global.css` mit Utility-Klassen und eine `nav.ts` als
zentrale Navigationsquelle. Der Skill fügt sich in dieses Muster ein, statt ein eigenes
Design-System danebenzustellen.

## Wann

Immer wenn Daten vorliegen (z. B. aus `marktplatz-scrape`, `winning-ads-finder`,
GA4-Auswertung, `deep-research`) und sie als Portal-Sektion/-Seite erscheinen sollen.

## Muster des Portals (nicht neu erfinden)

- **Astro static.** Daten als `src/data/<name>.ts` (`export const … = {…} as const`).
- **Layout:** jede Seite `import Layout from '../../layouts/Layout.astro'` und
  `<Layout active="/<sektion>/" title="…">`. Import-Tiefe beachten (Unterordner = `../../`).
- **Nur bestehende `global.css`-Klassen** verwenden, keine neuen Design-Systeme. Die
  vorhandenen Klassen zuerst aus der `global.css` des Zielportals lesen. Typischer Satz:
  `eyebrow`, `page disp`, `lede`, `sec-wrap`, `sec-head`, `card`, `grid` (cols-2/3/auto),
  `kpi`/`kpis`, `tbl` (`td.num`), `insight`, `chip`, `badge`, `crumb`, `pager`, `funnel`, `hbar`.
- **Navigation:** neue Sektion/Unterseite in `src/data/nav.ts` eintragen (num, label,
  href, desc, icon, ggf. `children`). Bei neuer Hauptsektion die nachfolgenden `num` anpassen.

## Workflow

1. **Daten ablegen:** Scrape-/Research-Output nach `src/data/<name>.ts` bringen. Bei
   wiederkehrenden Datenquellen lohnt ein kleines `scripts/gen-<quelle>.py` im Portal, das
   das Roh-JSON in eine `.ts` übersetzt, statt die Daten von Hand zu pflegen.
2. **Seite bauen:** `assets/page-template.astro` (in diesem Skill) nach
   `src/pages/<sektion>/<slug>.astro` kopieren und mit den Daten füllen.
   Bausteine je nach Daten: KPI-Karten (Kennzahlen), `tbl` (Vergleiche/Listen),
   `card`-Grid (Findings/Konzepte), `insight` (Schlussfolgerung), Galerie+Lightbox (Bilder).
3. **Verlinken:** `nav.ts` ergänzen; ggf. Übersichts-/Index-Seite der Sektion erweitern.
4. **Bauen & prüfen:** `npm run build` (muss fehlerfrei sein), dann `npm run dev`
   und die Seite visuell kontrollieren.

## Prinzipien

- **Nichts erfinden.** Nur Daten zeigen, die in der Quelle stehen; fehlende Werte als
  „–"/„offen" kennzeichnen, Unsicherheiten benennen.
- **Keine vertraulichen Daten** (Margen, Einkaufspreise, interne Umsätze) — das Portal
  ist publizierbar.
- **Ehrliche Einordnung:** jede Sektion endet mit einer `insight`-Box „was heisst das".
- Konsistenz vor Kreativität: gleiche Klassen, gleiche Tonalität (CH-Deutsch, du-Form).

## Bausteine nach Datentyp

| Daten | Baustein |
|---|---|
| Kennzahlen, Vergleichswerte | KPI-Karten (`kpi` / `kpis`), optional Funnel oder Balken |
| Wettbewerber, Preise, Listen | Tabelle (`tbl`, Zahlen in `td.num`) |
| Findings, Konzepte, Hooks | `card`-Grid |
| Bilder, Creatives, Ad-Galerien | Galerie mit Lightbox |
| Schlussfolgerung je Sektion | `insight`-Box |

Vor dem Bauen die bestehenden Seiten des Zielportals ansehen und den nächstliegenden
Seitentyp als Vorlage nehmen. Konsistenz schlägt Neuerfindung.
