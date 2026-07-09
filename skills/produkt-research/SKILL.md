---
name: produkt-research
description: This skill should be used when the user asks to "research this product", "Produkt recherchieren", "soll ich dieses Produkt sourcen", "Recherche-Ordner anlegen", or wants a research folder built from nothing more than a product URL or name — web sources only, no scraped marketplace data. Builds a complete, versioned research folder (deep-research report, competitor table, marketing brief, sourcing note, sources) and maintains an index. When real scraped marketplace prices must be cross-validated against the web, use apify-deep-research instead. Orchestrates the separate deep-research skill rather than researching on its own.
---

# Produkt- & Markt-Deep-Research → Research-Ordner

> **Voraussetzung:** Dieser Skill ruft den separaten **`deep-research`**-Skill auf, der nicht
> Teil dieses Plugins ist. Fehlt er, kann Schritt 3 nicht ausgeführt werden.

Dieser Skill macht aus **einer Produkt-Eingabe** eine **fundierte, abgelegte Markt-/Wettbewerbs-Recherche**.
Er erfindet die Recherche nicht selbst, sondern **orchestriert den vorhandenen `deep-research`-Skill** und
**verdichtet dessen Output in einen sauberen Ordner**, der (a) als Wissensspeicher wächst und (b) direkt den
Ad-Creative-Workflow füttert. Kein Insel-Tool: Research → Marketing → Sourcing hängen zusammen.

> Gebaut für CH-E-Commerce (Default: Schweizer Markt, CHF, „du"-Ansprache, Schweizer Schreibweise = **ss statt ß**).
> Alle Defaults sind überschreibbar.

---

## 1. Inputs sammeln (fehlende erfragen, sonst Default)

| Input | Pflicht | Default |
|---|---|---|
| **Produkt** — URL *oder* Name | ✅ | — |
| **Markt / Region** | – | Schweiz |
| **Zielgruppe** | – | aus dem Produkt ableiten |
| **Wettbewerber-Hinweise** (bekannte Marken) | – | KI ermittelt selbst |
| **Tiefe** — `schnell` (1 Lauf) / `tief` (mehrere Läufe) | – | `tief` |
| **Output-Basis-Ordner** | – | `Research/` (bei Kundenarbeit: `Kunden/<Kunde>/Research/`) |

Wenn eine Produkt-URL gegeben ist: **zuerst die Seite lesen** (echte Specs/Preis/USP ziehen), damit die Recherche
auf realen Daten fusst. Bei einem bestehenden Produkt-Steckbrief im Repo diesen mitnutzen.

**Slug bilden:** `<YYYY-MM-DD>_<produkt-kebab>` (Datum über `date +%F`, da im Skript keine Uhr verfügbar ist — hier im Shell-Kontext ok).

---

## 2. Ordner anlegen

```
<Basis>/<slug>/
  00_README.md            # Index + Recherche-Steckbrief (Produkt, Datum, Status, Inhaltsverzeichnis)
  01_Deep-Research.md     # VOLLSTÄNDIGER Output des deep-research-Skills (mit Quellen)
  02_Wettbewerber.md      # Wettbewerber-Tabelle, verdichtet
  03_Marketing-Brief.md   # Winkel/Hooks/Einwände → Input für Ad-Creative-Skill (Skill 2)
  04_Sourcing-Hinweis.md  # First-Mover / Nachfolgemodell-Bewertung (für Sourcing-Entscheid)
  05_Quellen.md           # Quellenliste mit Links + Verlässlichkeit
```

Plus eine Registry `<Basis>/INDEX.md` (anlegen falls fehlt, sonst Zeile ergänzen).

---

## 3. Recherche ausführen — **`deep-research`-Skill aufrufen**

Den `deep-research`-Skill (Skill-Tool) mit einer **aus den Inputs komponierten Forschungsfrage** starten.
Bei Tiefe `tief` ggf. 2–3 fokussierte Läufe (Wettbewerb/Preise · Reviews/Einwände · Trend/Nachfrage) und
zusammenführen. Frage-Gerüst (anpassen):

```
Analysiere das Produkt <Produkt/URL> und sein Wettbewerbsumfeld im Markt <Region>, um zu entscheiden,
(a) wie wir es am besten vermarkten und (b) ob das Segment für Sourcing/Nachfolgemodelle attraktiv ist.
Zielgruppe: <…>. Wir sind Händler + Eigenmarke; Sourcing-Geschwindigkeit ist unser Vorteil.

Recherchiere über mehrere Quellen:
- Direkte Wettbewerber in <Region>/DE (Preis, Specs, Mechanik/Variante, lokale Verfügbarkeit)
- Marktplätze (Amazon DE, Galaxus o. ä.): was rankt/verkauft sich im Segment
- Reviews: Top-Kaufargumente und Top-Beschwerden der Zielgruppe
- Trend/Nachfrage: steigend/fallend, Saisonalität

Gib strukturiert mit Quelle pro Aussage:
1) Markt-Snapshot  2) Wettbewerber-Tabelle (Name|Preis|Specs|Verfügbar|Stärke/Schwäche)
3) Positionierung uns  4) Top-Kaufargumente & Top-Einwände (je 3–5)
5) 3 konkrete Marketing-Hooks  6) Sourcing-/Nachfolgemodell-Hinweis (First-Mover-Chance?)
7) Unsicherheiten & was noch zu prüfen ist

Regeln: Preise in <Währung>. Fakten (mit Quelle) von Einschätzung trennen. Unsichere Zahlen kennzeichnen.
Keine erfundenen Quellen.
```

Den **kompletten** zitierten Report unverändert in `01_Deep-Research.md` ablegen (mit Kopf: Produkt, Datum, verwendete Frage).

---

## 4. Verdichten — die abgeleiteten Dateien

Aus `01` ohne neue Erfindungen extrahieren/zusammenfassen:

- **`02_Wettbewerber.md`** — die Wettbewerber-Tabelle als eigenständige, scanbare Übersicht (+ 1 Kernaussage: wo stehen wir?).
- **`03_Marketing-Brief.md`** — der downstream-Teil für den Ad-Creative-Skill:
  - Positionierung in 1 Satz · 3–5 **Hooks** · Top-Einwände + **Konter** · Tonalität/No-Gos (z. B. keine Health-Claims).
  - Kopf-Hinweis: „Input für den Ad-Creative-Workflow (Skill 2)".
- **`04_Sourcing-Hinweis.md`** — lohnt ein stärkeres/günstigeres Nachfolgemodell? First-Mover-Fenster? Klartext-Empfehlung für den Sourcing-Entscheid.
- **`05_Quellen.md`** — alle Quellen mit Link; je Quelle kurz: belastbar / unsicher.

**`00_README.md`** — Recherche-Steckbrief: Produkt, URL, Datum, Region, Status, 3-Bullet-Kernergebnis + Inhaltsverzeichnis (Links auf 01–05).

---

## 5. Index pflegen

`<Basis>/INDEX.md` — Tabellenzeile ergänzen:

```
| Datum | Produkt | Kernergebnis (1 Satz) | Ordner |
```

---

## Guardrails
- **Fakten ≠ Einschätzung** sauber trennen; unsichere Zahlen kennzeichnen; **keine erfundenen Quellen**.
- **Schweizer Schreibweise** (ss), Preise in CHF, „du"-Ansprache — sofern Markt = CH.
- **Margen/Einkaufspreise sind intern** — wenn vorhanden, nur in interne Dateien, nie in den Marketing-Brief als Aussenkommunikation.
- Bei gesundheitsnahen Produkten im Marketing-Brief auf **keine Heilversprechen** hinweisen.
- Skill ist **wiederverwendbar**: pro Produkt ein neuer datierter Ordner — die Research-Ablage wächst.

## Anschluss
Der `03_Marketing-Brief.md` ist die Übergabe an den **Ad-Creative-/Marketing-Skill** (Produkt → Hooks → Ad-Copy + Creative).
