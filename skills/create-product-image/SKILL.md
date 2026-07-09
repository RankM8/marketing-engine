---
name: create-product-image
description: This skill should be used when the user asks to "create a product ad", "generate ad creatives", "make a Meta ad image", "Produktbild generieren", "Ad-Creative erstellen", "Werbebild bauen", "swap the background of a product photo", or wants ad images where the real product must be reproduced faithfully. Covers the BACKGROUND-SWAP method for true product fidelity, brand text/price/discount overlays, feature callouts, logo placement, and native 1:1 / 4:5 / 9:16 framing. Routes to OpenAI gpt-image via OpenRouter (default) or fal.ai.
---

# create-product-image

Vollstaendige Pipeline fuer Produkt-Ad-Creatives: Szene generieren, Format setzen,
Marken-Typografie auflegen, Treue pruefen.

## Das Wichtigste zuerst: drei Treue-Stufen

Ein Bildmodell **re-rendert** das Produkt. Bei reiner Generierung ist es **nie pixelgenau**.
Feine Details wie Logo, Verstell-Rad oder Halterung werden erfunden und variieren pro Lauf.
Deshalb gilt immer eine dieser drei Einstufungen:

1. **Echt (1:1) per BACKGROUND-SWAP.** Echtes Produktfoto als Referenz, das Modell ersetzt
   **nur den Hintergrund** und rechnet Schatten sowie Reflexion dazu. Produkt, Halterung und
   Logo bleiben die echten Pixel. Die Methode der Wahl bei komplexen Produkten.
2. **Produktnah.** Produkt aus der Referenz neu generiert. Sieht gut aus, aber Details sind
   nur angenaehert. Taugt fuer Vielfalt, nicht fuer Detailgenauigkeit.
3. **Abweichend.** Falsche Halterung, fehlendes Logo, verkrakelter Text. Verwerfen.

**Regel:** Bei komplexen Produkten immer Background-Swap. Nie "1:1" behaupten, wenn das
Modell das Produkt neu gemalt hat. Die Einstufung im Zweifel abwerten, nicht schoenreden.

## Gateway waehlen

| | `--gateway openrouter` (Default) | `--gateway fal` |
|---|---|---|
| Ausgabe | immer ~1024x1024 | echte Leinwandgroesse |
| `--aspect-ratio` | nur ein Kompositions-Hinweis | die tatsaechliche Groesse |
| `--image-size` | wirkungslos | bis 3840px (nur `gpt-image-2`) |
| Kosten pro Bild | ca. $0.24 bis $0.27 (high, mit Referenzen) | $0.02 bis $0.20 je Modell und Qualitaet |
| Staerke | starkes Ankern auf der Referenz, beste Produkttreue | echte Hochformate, grosse Bogen |

Fuer Produkt-Ads mit Treue-Anspruch: **openrouter**. Das quadratische Ergebnis wird
anschliessend per `reframe.py` mittig auf 4:5 oder 9:16 beschnitten, nie gestreckt.

Fuer Storyboards, grosse Bogen oder echte Nicht-Quadrat-Leinwaende: **fal** mit `gpt-image-2`.

## BACKGROUND-SWAP, die Kern-Methode

Die Scripts liegen im Plugin, gearbeitet wird im Kundenverzeichnis. Deshalb immer über
`${CLAUDE_PLUGIN_ROOT}` aufrufen:

```bash
S="${CLAUDE_PLUGIN_ROOT}/skills/create-product-image/scripts"

python3 "$S/generate.py" \
  --prompt "This is a REAL product photo of <Produkt>. KEEP THE ENTIRE PRODUCT EXACTLY AS IN
   THE INPUT, pixel-faithful and unchanged: <jedes Teil einzeln nennen>. Do NOT redraw,
   reshape, recolour or move any part of the product. ONLY replace the plain background with
   <SZENE>, add a realistic soft contact shadow and subtle reflection. Photoreal, premium,
   product centred, clean empty space in the upper third for later text." \
  --output base.png --ref-image ORIGINALFOTO.jpg --no-text --quality high

python3 "$S/reframe.py" --image base.png --output base916.png --ratio 9:16
python3 "$S/overlay_portrait.py" --image base916.png --output final.png \
  --headline "Dein Home-Gym.\nEine Hantel." --price "CHF 199.-" --strike "239.-" --discount "-17%"
```

**Warum das funktioniert:** Der Referenz-Modus ankert sehr stark auf dem Eingabebild. Produkt,
Halterung und Logo bleiben praktisch unveraendert, nur der zuvor schlichte Hintergrund wird
ersetzt und Licht sowie Schatten angepasst.

**Grenze:** Die Pose ist durch das Originalfoto vorgegeben. Loesung: mehrere Original-Posen
nutzen (frei, dreiviertel, in der Halterung, von oben) und je Foto verschiedene Szenen bauen.

## Harte Regel: nichts erfinden, was es nicht gibt

Das Modell darf **nie** eine Halterung, Ablage oder Basis erfinden, die auf der Referenz
nicht zu sehen ist.

- Referenz **ohne** Halterung: der Prompt muss enthalten `do NOT add any stand, tray, cradle,
  dock or base that is not in the reference`.
- Halterung **gewollt**: von Anfang an eine Referenz **mit** der echten Halterung verwenden.
  Nie eine freie Referenz nehmen und auf eine Halterung hoffen.

Erfundene Halterung heisst verwerfen, nicht nachbessern.

## Referenz-Regeln

- **Immer echte Originalfotos** von der Produktseite. **Niemals** ein zuvor generiertes Bild
  als Referenz, sonst potenzieren sich Fehler. Nachpruefbar im Feld `ref_images` der
  `.meta.json`, die neben jedes Bild geschrieben wird.
- **Pose passend zur Komposition.** Ein frei gehaltenes Produkt braucht eine freie Referenz.
  Eine falsche Pose-Referenz erzeugt unmoegliche Bilder.
- **Hochaufloesend ziehen**, so gross wie die Quelle hergibt.
- Fuer den Background-Swap reicht **eine** starke Referenz, sie *ist* das Produkt. Beim
  Neu-Generieren verbessern mehrere Referenzen die Treue.

## Scripts

| Script | Zweck |
|---|---|
| `generate.py` | Bild erzeugen. Ohne `--ref-image` Text-zu-Bild, mit Referenz der Edit-Modus. `--gateway`, `--no-text`, `--quality`. Schreibt `<out>.meta.json` mit Modell, Referenzen und Kosten. |
| `reframe.py` | Format per **mittigem Crop**, erfindet nie Pixel. `--ratio 1:1\|4:5\|9:16\|16:9` |
| `overlay_text.py` | Marken-Typo: Headline oben, Preis-Pille unten, Rabatt-Kreis. |
| `overlay_portrait.py` | Hochkant-Layout fuer Stories und Reels. |
| `overlay_landscape.py` | 16:9-Layout, Text links, Produkt rechts. |
| `overlay_callouts.py` | Feature-Callouts mit Linie zum Produktteil. |
| `composite_logo.py` | Echtes Logo als Marken-Signatur in die Ecke, nie aufs Produkt. |
| `brandkit.py` | Loest `brand.json` auf. Kein Aufruf noetig, die Overlays nutzen es. |

## Marke konfigurieren

Farben, Schrift und Logopfade stehen **nicht** im Plugin, sondern in einer `brand.json` im
Kunden-Verzeichnis. Gesucht wird vom Arbeitsverzeichnis aufwaerts. Vorlage: `examples/brand.json`
im Plugin-Root. Ohne `brand.json` laufen die Scripts mit neutralen Defaults und warnen.

## Text: zwei erprobte Wege

**A) Text vom Modell rendern lassen.** Im Background-Swap-Prompt zusaetzlich Headline, Preis
und Rabatt als exakte Strings vorgeben. Kurze Copy und Preise kommen sauber, das Layout ist
voll integriert und verdeckt das Produkt nicht. **Rechtschreibpruefung ist Pflicht**, lange
Copy verkrakelt. Genau ein Prozentzeichen schreiben.

**B) Overlay.** Mit `--no-text` generieren, dann die Overlay-Scripts. Pixelgenaue Marken-Typo,
aber das Textband kann bei Hochkant Teile verdecken.

Beide testen. Fuer die Schweiz: du-Form, "ss" statt "ß", Preisformat `CHF 199.-`.

## QA nach jedem Bild, ohne Ausnahme

- Jedes Bild **visuell gegen das echte Produkt** pruefen, bevor es als gut gilt.
- Treue-Stufe ehrlich vergeben. Im Zweifel abwerten.
- Pruefen: Form, Mechanik, Halterung, Logo, Rechtschreibung.
- Defekte verwerfen und mit richtiger Methode neu bauen, oder ehrlich melden, dass keine
  passende Referenz existiert.

Der Skill `verify-product-image` automatisiert die formalen Teile dieser Pruefung.

## Empfohlener Workflow

1. Originalfotos ziehen, sichten, Posen identifizieren.
2. Background-Swap je Pose mal mehrere Szenen, `--no-text`, `--quality high`.
3. QA jeder Basis: Produkt, Halterung, Logo unveraendert?
4. `reframe.py` auf die Zielformate.
5. Typografie per Overlay, Logo nur in die Ecke.
6. Ablegen und ins Portal uebernehmen, siehe `research-to-portal`.

## Weiterfuehrend

- **`references/hochformat.md`** — warum 9:16 und 4:5 nur per Mittel-Crop entstehen und wie
  das Quadrat dafuer komponiert sein muss. Lesen, bevor Hochformate gebaut werden.
- **`references/json-prompting.md`** — JSON-Spec statt Fliesstext fuer conversion-optimierte
  Ads mit Sticker, Streichpreis und CTA-Button.
- **`references/pitfalls.md`** — gelernte Fallen: Personen-Ads, Logo-Reproduktion, Konzepte,
  die mit Neu-Generierung zuverlaessig scheitern.

## Zugangsdaten

`OPENROUTER_API_KEY` fuer openrouter, `FAL_API_KEY` fuer fal. In der Umgebung oder einer
`.env` im Verzeichnisbaum. **Nie committen.**

## Verwandte Skills

`verify-product-image` (Qualitaetskontrolle) · `research-to-creative` (Hooks und Copy aus
Recherche) · `research-to-portal` (Ergebnisse ins Kundenportal)
