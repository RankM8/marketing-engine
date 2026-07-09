---
name: verify-product-image
description: This skill should be used when the user asks to "verify the creative", "check the generated image", "QA the ad", "Creative prüfen", "Produkttreue kontrollieren", "ist das Bild echt", or after generating ad images that need a quality gate before shipping. Verifies the file opens, matches the requested dimensions, shows the correct product (right shape, colour, mechanism, logo) and has no garbled text or severe artifacts. Assigns an honest fidelity grade and records pass/fail/needs-human in verification.md.
---

# verify-product-image

Qualitaetstor vor der Auslieferung eines generierten Creatives. Der Skill prueft, was
mechanisch pruefbar ist, und zwingt zu einem **ehrlichen Treue-Urteil** bei dem, was nur
das Auge entscheiden kann.

Ohne dieses Tor wandern Bilder mit erfundenen Halterungen und verkrakelten Preisen in
Kampagnen. Das ist teurer als jede Nachgenerierung.

## Ablauf

1. **Datei.** Oeffnet sie? Ist sie groesser als 1 KB? Entsprechen die Abmessungen dem, was
   bestellt wurde (`1024x1024`, `576x1024` fuer 9:16, `819x1024` fuer 4:5)?
2. **Herkunft.** Die `.meta.json` neben dem Bild lesen. Welches Modell, welches Gateway,
   welche `ref_images`? **Eine generierte Datei als Referenz ist ein Fehlschlag**, weil sich
   Fehler ueber Generationen potenzieren.
3. **Produkt.** Das Bild gegen das echte Produktfoto halten. Stimmen Form, Farbe, Mechanik,
   Halterung und Logo? Wurde etwas hinzuerfunden, das auf der Referenz nicht existiert?
4. **Text.** Jedes sichtbare Wort lesen. Rechtschreibung, Umlaute, genau **ein**
   Prozentzeichen, Preisformat korrekt.
5. **Artefakte.** Verzerrte Kanten, doppelte Objekte, unmoegliche Schatten, freigestellt
   wirkende Produkte ohne Kontaktschatten.

## Treue-Urteil, ehrlich vergeben

| Stufe | Bedeutung | Konsequenz |
|---|---|---|
| **echt** | Produkt stammt pixelgenau aus dem Referenzfoto (Background-Swap) | freigeben |
| **produktnah** | Produkt neu gerendert, Details nur angenaehert | nur fuer Vielfalt, nie fuer Detail-Aussagen |
| **abweichend** | falsche Halterung, fehlendes Logo, verkrakelter Text | verwerfen |

**Im Zweifel abwerten.** Ein "produktnah", das als "echt" durchgeht, beschaedigt das
Vertrauen in die gesamte Ablage.

## Ergebnis festhalten

Pro geprueftem Batch eine `verification.md` neben den Bildern:

```markdown
| Datei | Format | Treue | Text ok | Befund |
|---|---|---|---|---|
| hero-916.png | 576x1024 | echt | ja | freigegeben |
| garage-11.png | 1024x1024 | abweichend | nein | erfundene Ablage, "-17%%" doppelt |
```

Zulaessige Status: `pass`, `fail`, `needs human`, `blocked` (z. B. keine Referenz vorhanden),
`skipped`.

## Wenn etwas durchfaellt

Nicht nachbessern, sondern **die Ursache benennen und neu bauen**:

- Erfundene Halterung → Background-Swap mit einer Referenz, die die echte Halterung zeigt.
- Fehlendes Logo → Background-Swap, oder `composite_logo.py` fuer die Ecke.
- Verkrakelter Text → mit `--no-text` generieren und per Overlay setzen.
- Keine passende Referenz vorhanden → **ehrlich melden**, nicht kaschieren.

## Verwandte Skills

`create-product-image` (Erzeugung und die Methoden hinter den Treue-Stufen)
