# Natives Hochformat: 9:16 und 4:5 ohne Strecken

## Der Fehler, der einmal gemacht wurde

Ein fertiges quadratisches Creative nehmen und oben sowie unten Hoehe "ergaenzen". Das Ergebnis
sind gestauchte Baender oben, verwaschene gestreckte Streifen unten oder schwarze Balken. Das
ist kein Hochformat, sondern ein verunstaltetes Quadrat. Es faellt sofort auf und wirkt billig.

## Warum mittiger Crop die einzige richtige Antwort ist

Die Seitenverhaeltnisse als Zahl, Breite geteilt durch Hoehe:

| Format | Verhaeltnis | Verglichen mit dem Quadrat (1.0) |
|---|---|---|
| 16:9 | 1.778 | breiter |
| 1:1 | 1.0 | gleich |
| 4:5 | 0.8 | **schmaler** |
| 9:16 | 0.5625 | **deutlich schmaler** |

9:16 und 4:5 sind **schmaler** als ein Quadrat. Man gewinnt keine Hoehe dazu, man nimmt Breite
weg. `reframe.py` beschneidet die Breite mittig, dadurch bleibt der echte Hintergrund oben und
unten vollstaendig erhalten. Nichts wird erfunden, nichts gestreckt.

Aus 1024x1024 wird:

- **9:16** = 576 x 1024
- **4:5** = 819 x 1024
- **1:1** = das Quadrat unveraendert

## Die Voraussetzung: 9:16-first komponieren

Ein Mittel-Crop schneidet links und rechts je rund 230 Pixel weg. Steht dort etwas Wichtiges,
ist es verloren. Das Quadrat muss deshalb von vornherein so gebaut sein, dass der Crop nichts
kostet.

Die Anweisung an das Modell:

> Alle Elemente (Headline, Produkt, Sticker, Preis, CTA) liegen strikt in einer schmalen
> vertikalen **Mittelspalte** von etwa 55 Prozent der Breite, also rund 560 Pixel, vertikal
> gestapelt. Die linken und rechten rund 230 Pixel enthalten **nur durchgehenden Hintergrund**.
> Der Hintergrund fuellt randlos die ganze Flaeche, kein Rahmen, keine Balken. Das Produkt ist
> kompakter und leicht dreiviertel angewinkelt, damit es in die schmale Spalte passt.

Praktisch heisst das: eine `layout_rule` im JSON-Prompt (siehe `json-prompting.md`), die genau
diese Mittelspalte beschreibt.

## Mehrere Varianten generieren

Die Mittelspalten-Komposition gelingt **nicht immer beim ersten Versuch**. Das Modell zieht
Elemente gern nach aussen. Pro Konzept mehrere Varianten erzeugen und die beste waehlen, statt
eine misslungene per Crop retten zu wollen.

## Ablauf

```bash
S="${CLAUDE_PLUGIN_ROOT}/skills/create-product-image/scripts"

# 1. Quadrat generieren, 9:16-first komponiert, ohne Typografie
python3 "$S/generate.py" --prompt "<mit layout_rule Mittelspalte>" \
  --output base.png --ref-image original.jpg --no-text --quality high

# 2. Mittig auf das Zielformat beschneiden
python3 "$S/reframe.py" --image base.png --output story.png --ratio 9:16

# 3. Typografie auflegen
python3 "$S/overlay_portrait.py" --image story.png --output final.png \
  --headline "..." --price "CHF 199.-"
```

## Der andere Weg: echte Leinwand bei fal

Wer eine echte 1024x1536-Leinwand statt eines beschnittenen Quadrats braucht, nimmt
`--gateway fal --aspect-ratio 9:16`. Das Modell komponiert dann direkt fuer das Hochformat.

Der Preis: fal ankert schwaecher auf der Referenz als OpenRouter. Fuer Ads mit hohem
Treue-Anspruch bleibt der Weg ueber das Quadrat plus Mittel-Crop die bessere Wahl.
