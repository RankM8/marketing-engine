# Gelernte Fallen

Alles hier ist an echten Kampagnen aufgelaufen. Die Liste erspart es, dieselben Bilder
zweimal zu verwerfen.

## Konzepte, die mit Neu-Generierung zuverlaessig scheitern

- **Breakout- und Billboard-Konzepte**, bei denen das Produkt aus einem Rahmen ragt. Erzeugt
  Artefakte: Halterungs-Klammern an frei gehaltenen Produkten, falsche Endkappen.
- **Produkt-Nahaufnahmen.** Sie entlarven jedes erfundene Detail, allen voran die Mechanik.
  Ein Verstell-Rad, das das Modell nie gesehen hat, sieht aus der Naehe immer falsch aus.
- **Cut-out-Compositing**, also Hintergrund generieren und ein freigestelltes Produkt
  darueberlegen. Man sieht es sofort an den Kanten und am fehlenden Kontaktschatten.
  Stattdessen Background-Swap, dabei bleibt das Produkt im echten Foto eingebettet.
- **Vertikal stehende laengliche Produkte auf einem Sockel.** Werden oft unfoermig, im
  Zweifel eine horizontale Pose waehlen.

## Logo

Bildmodelle reproduzieren kleine Logos beim Neu-Rendern unzuverlaessig. Sie verschwinden oder
werden zu Kritzeln. Drei Wege, in dieser Reihenfolge:

1. **Background-Swap.** Das Logo bleibt automatisch echt, weil das Produkt echt bleibt. Bestes
   Ergebnis, kein Zusatzaufwand.
2. **Neu-Generierung mit Logo.** Die Logo-Flaeche zur Kamera orientieren, einen Ausschnitt des
   Logos aus dem Originalfoto als **zweite Referenz** mitgeben und im Prompt fordern, das Logo
   aus Referenz zwei exakt zu uebernehmen. Es kommt lesbar, aber nicht vektorscharf.
3. **`composite_logo.py`.** Das echte Logo als Marken-Signatur in die Ecke setzen. Garantiert
   korrekt. Niemals ein Logo auf das Produkt selbst faelschen.

## Personen- und In-Use-Ads

Laesst man ein Modell eine Person mit dem Produkt generieren, ist das Produkt **nicht mehr
1:1**. Fuer Treue-Anspruch ist das disqualifiziert.

Der richtige Weg: **echte In-Use-Fotos** als Basis nehmen, also Person plus echtes Produkt.
Stoerendes wie ein Wasserzeichen per Edit-Modus entfernen, mit einer eng gefassten Anweisung
(`nur die Wand saeubern, Produkt unveraendert lassen`). Danach Text-Overlay. Das Ergebnis ist
echtes 1:1 mit Person.

## Text im Bild

- Genau **ein** Prozentzeichen schreiben, nie zwei. Doppelte Zeichen tauchen im Bild auf.
- Lange Copy verkrakelt auch bei guten Modellen. Kurze Strings sind zuverlaessig.
- Rechtschreibpruefung ist Pflicht, besonders bei Umlauten und regionalen Eigenheiten.
- Wenn die Typografie exakt sitzen muss: `--no-text` generieren und per Overlay setzen.

## Referenzen

- **Nie ein generiertes Bild als Referenz weiterverwenden.** Fehler potenzieren sich ueber
  Generationen. Das Feld `ref_images` in der `.meta.json` macht nachpruefbar, was verwendet
  wurde.
- **Pose und Komposition muessen zusammenpassen.** Eine Referenz, auf der das Produkt in der
  Halterung liegt, ergibt kein glaubwuerdiges Bild einer Person, die es frei haelt.

## Shell

Kurze Funktionsnamen wie `gb` oder `g32` kollidieren mit zsh-Aliassen. In Batch-Scripts
eindeutige Namen verwenden.

## Kosten im Blick behalten

Ein Bild ueber OpenRouter mit Referenzen in hoher Qualitaet kostet rund 0.24 bis 0.27 US-Dollar.
Ein Batch von 50 Varianten sind also gut 12 Dollar. Der echte Wert steht nach jedem Lauf im
Feld `cost_usd` der `.meta.json`, bei fal als `cost_estimate_usd`.
