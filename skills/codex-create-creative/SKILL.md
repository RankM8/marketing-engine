---
name: codex-create-creative
description: Ad-Creatives und Produktbilder ÜBER CODEX generieren (natives image_gen__imagegen via whisperm8-Subagents) — kostenlos im Codex-Flat-Plan, Standard-Pfad wenn Codex verfügbar ist. Nutzen bei "Creative erstellen", "Bild generieren", "Produktbild", "Ad bauen", "Personen-Creative", "Bild reviewen/QA". Deckt Zwei-Schritt-Pipeline (Basis + Design-Pass), strukturierte JSON-Prompts, Produkttreue-QA, Doppel-Review und Job-Orchestrierung ab. Für Pay-per-Use ohne Codex stattdessen create-product-image (OpenRouter/fal).
---

# codex-create-creative — Creative-Produktion über Codex-Subagents

Vollständige Produktions-Pipeline für Ad-Creatives über Codex' natives Bildgenerierungs-Tool
`image_gen__imagegen` (Codex-Flat-Plan: kein API-Key, keine Pro-Bild-Kosten). Schwester-Skill
von `create-product-image` (OpenRouter/fal, Pay-per-Use) — **dieser Skill ist der Standard,
sobald Codex + WhisperM8 verfügbar sind.**

## Voraussetzungen (Preflight — bei Fehlen sauber abbrechen, NICHT auf OpenRouter ausweichen)

1. `whisperm8 --version` funktioniert (WhisperM8-App installiert, Skill `codex-subagent`).
2. Codex CLI eingeloggt mit Flat-Plan.
3. `brand.json` des Kunden vorhanden (Farben, Font, Logo-Pfade — siehe `brandkit.py`
   in `create-product-image/scripts/`).

Kostenpflichtige Gateways (OpenRouter, fal, OPENAI_API_KEY-Fallback) nur nach **explizitem
User-Go** — nie stillschweigend ausweichen.

## Ausführungsmodell (wichtigster Unterschied zu create-product-image)

`image_gen__imagegen` ist **kein API-Endpoint**: Es existiert nur innerhalb eines
Codex-Agenten. Claude ruft es nie direkt auf, sondern briefed einen Subagenten
(`whisperm8 agent run/send`), der die Aufrufe macht. Dieser Skill liefert dafür die
Kopiervorlagen (`references/agent-templates/`).

Native Tool-Signatur (vollständig — mehr gibt es nicht):
`prompt` (Pflicht) · `referenced_image_paths` (lokale Pfade) · `num_last_images_to_include`
(max 5; nie zusammen mit referenced_image_paths). **Keine** Parameter für Größe, Qualität,
Seed, Maske, Anzahl. Ausgabe ~1254×1254 px. Format/Qualität steuert man ausschließlich über
den Prompt; Details: `references/schema-vollstaendig.md`.

## Betriebsregeln (empirisch erhärtet — Verstöße kosten Stunden)

- **STRIKT SERIELL, auch global:** Nur EIN aktiver image_gen-Aufruf pro Account — egal aus
  wie vielen Jobs. Parallele Generierungs-Jobs erzeugen Stream-Abbrüche und Hänger bei ALLEN.
  Wenn parallelisiert wird: Auto-Resume-Überwachung einplanen (Heal-Monitor-Muster in
  `references/dos-and-donts.md`).
- Hänger >3 Min abbrechen, 60–120 s warten, wiederholen (bis 6 Versuche bei Backend-Last).
- Ein Fehlschlag bricht NIE den Batch ab; unbearbeitete Motive nie als FAIL dokumentieren.
- Ergebnis aus `$CODEX_HOME/generated_images/` ins Arbeitsverzeichnis kopieren lassen —
  sonst verloren. Sidecar `<name>.png.meta.json` (gateway, konzept, prompt, ref_images) Pflicht.
- Jobs detacht starten (`run` ohne `--wait`); Turns überleben Wrapper-Kills nur so.

## Produktionsrezept: Zwei-Schritt + Struct-Prompts

Bewährt (Fitagon v3-Welle, 100+ Creatives): **Konzept-JSONs als Single Source of Truth**,
je Motiv zwei Aufrufe:

1. **Basis** — `referenced_image_paths=[Posen-Foto, Produkt-Freisteller]`, Prompt =
   `prompt_basis_struct` als JSON-Text. Ergebnis: textfreies Foto, Person ersetzt,
   Produkt nach Referenz nachgebaut, Szene neu.
2. **Design-Pass** — `referenced_image_paths=[Basis, Logo-PNG]`, Prompt =
   `prompt_design_struct` als JSON-Text. Ergebnis: integriertes Ad-Design (Headline,
   Preis-Pille, Rabatt-Badge, Wortmarke) IM Bild — kein Sticker-Look.

**Prompts sind strukturierte JSON-Spezifikationen, keine Prosa** — jedes Element ein eigenes
Feld (Text, Position, Farbe, Größe, Regeln). Das hat im A/B-Test klar gewonnen: keine
erfundenen Preise, keine Extra-Produkte, exakte Copy. Feld-Spezifikation und Beispiel:
`references/struct-prompt-format.md`. Konvertierung: `scripts/make_struct_prompt.py`.

**Kein Cut-out-Compositing:** Produkt/Person niemals als Freisteller einkleben — immer voll
generativ nachbauen (User-Direktive). Ausnahme ist ausschliesslich das Marken-Logo (s. u.).

## Brand-Guidelines-Pflicht (seit 2026-07-16)

Vor jeder Produktion Brand-Quelle laden (`BRAND.md` → `brand.json` → Manual-PDF → User
fragen) und in die Struct-Prompts einbrennen: exakte Farb-Hexwerte, `brand_font` im
Charakter der Marken-Schrift. **Das Logo wird NICHT mehr mitgeneriert:** Im Design-Struct
kein `logo`-Element, stattdessen `canvas.reserved_logo_zone` (untere 13 % frei; Hochformat:
obere 13 %) — nach dem QA-Pass setzt `scripts/brand_logo_overlay.py` das echte Vektor-Logo
Manual-konform (Foto: Grau-Box oder 15%-Stripe; Feed unten, Story/Banner oben). Details,
Placement-Matrix und Farb-Fallen: `references/brand-guidelines.md`.
Alt-Fallback für Bestandsmotive mit generierter Wortmarke:
`create-product-image/scripts/composite_logo.py`.

## QA-Vertrag (jedes Final, jedes Kriterium einzeln PASS/FAIL)

1. **Produkttreue = K.-o.-Kriterium:** Teil-für-Teil gegen den ECHTEN Freisteller (nicht
   gegen die Basis): Plattenzahl/Bauteile ZÄHLEN, Details einzeln (Rillen, Clips, Endplatte,
   Griff). Exakt die Produktinstanzen aus dem Posen-Foto — keine Extras, keine leeren
   Ablagen, im Zweifel weniger.
2. Copy ZEICHENGENAU gegen das Konzept-JSON inkl. Umbrüchen und Umlauten (ä/ö/ü — nie
   ae/oe/ue), genau EIN %-Zeichen, genau EIN Streichpreis, nie Preise erfinden.
3. Logo: KEIN generiertes Logo/Wortmarke im Bild; reservierte Logo-Zone (13 %) frei.
   (Bestandsmotive mit generierter Wortmarke: Buchstabenformen gegen Referenz, sonst
   Fallback composite_logo.)
4. Format exakt quadratisch (bzw. Sollformat), 5 % Safe-Margin: nichts angeschnitten.
5. Anatomie (Hände/Finger), kein Composite-Look, Text verdeckt weder Gesicht noch Produkt.
6. Brand-Checks bei Brand-Pflicht: Marken-Gelb rein (kein Senf-Drift), Typo-Charakter
   gemäss `brand_font` — siehe `references/brand-guidelines.md`.

## Doppel-Review (Pflicht)

Selbst-QA des Generier-Agenten ist nachweislich zu milde. Immer:
1. **Unabhängiger Codex-Schiedsrichter** (separater read-only Job, `agent-templates/review-brief.md`):
   Urteile echt/produktnah/abweichend, im Zweifel abwerten.
2. **Eigener Bildvergleich** durch Claude (Read auf Final + Freisteller).
Nur doppelt Bestätigtes ist freigegeben; Fails in eine REGEN-QUEUE.md und mit Struct-Prompts
neu generieren (Auslese statt Hoffnung — 100 % gibt es pro Wurf nicht, nur im Endbestand).

## Lernpflicht

Jede neue Erkenntnis sofort in `references/dos-and-donts.md` nachtragen — das lebende
Gedächtnis dieses Skills, im Repo geteilt mit dem ganzen Team.
