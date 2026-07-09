# JSON-Prompting fuer Conversion-Ads

Fuer conversion-optimierte Creatives, bei denen Headline, Sticker, Streichpreis und
CTA-Button praezise sitzen sollen, das Modell mit einem **JSON-Spec** steuern statt mit
Fliesstext. Das gibt deutlich mehr Kontrolle darueber, was wohin gehoert.

## Der bewaehrte Wrapper

Der JSON-Spec wird in einen Prompt eingebettet, der drei Dinge festnagelt: Rechtschreibung,
Produkttreue und die aesthetische Richtung.

> You are designing a HIGH-CONVERTING Meta performance ad. Follow the JSON spec EXACTLY:
> render every text element crisp and CORRECTLY SPELLED in Swiss German.
>
> CRITICAL PRODUCT RULE: the product is the EXACT item from the reference image. Reproduce it
> pixel-faithful (including the logo), ONLY replace the background; do NOT redraw the product
> or invent any stand/tray.
>
> AESTHETIC: raw, native, deliberately UNDERDESIGNED performance-ad look. Bold, scrappy,
> high-contrast, like a real top-performing direct-response ad, NOT glossy corporate.
>
> SPEC: {json}

"Underdesigned" ist Absicht. Hochglanz wirkt wie Werbung, roh wirkt wie ein Post.

## Die Felder

```json
{
  "goal": "conversion",
  "background": "dark studio, single hard light from the left",
  "product_placement": "centred, lower two thirds, three-quarter angle",
  "layout_rule": "all elements inside a narrow vertical centre column (~55% width)",
  "brand_colors": { "ink": "<ink aus brand.json>", "accent": "<accent aus brand.json>" },
  "elements": [
    { "type": "eyebrow",          "text": "NEU IM LAGER",        "pos": "top-left" },
    { "type": "headline",         "line1": "22 Hantelpaare.",
                                   "line2": "Eine Hantel.",       "pos": "top-left" },
    { "type": "discount_sticker", "text": "-17%",                 "pos": "top-right",
                                   "style": "yellow circle, slightly rotated" },
    { "type": "price",            "text": "CHF 199.-",
                                   "strike": "239.-",             "pos": "bottom-left" },
    { "type": "cta_button",       "text": "Jetzt sichern",        "pos": "bottom-centre",
                                   "style": "yellow pill" },
    { "type": "checklist",        "text": ["CH-Lager", "2 Jahre Garantie"] },
    { "type": "marker_note",      "text": "in Sekunden verstellt" }
  ]
}
```

Verfuegbare `type`-Werte: `eyebrow`, `headline`, `discount_sticker`, `price`, `cta_button`,
`checklist`, `marker_note`.

## Was zuverlaessig klappt und was nicht

Headline oben links, gelber Rabatt-Sticker oben rechts, Preis mit Streichpreis und der
CTA-Button als gelbe Pille kommen zuverlaessig und korrekt gesetzt. Das Produkt bleibt via
Background-Swap unveraendert.

Texttreue ist bei **kurzen Strings** gut. Trotzdem gilt: **jedes Bild auf Rechtschreibung
pruefen**. Lange Copy verkrakelt weiterhin. Genau ein Prozentzeichen schreiben, nie zwei.

## Conversion-Hebel, die sich bewaehrt haben

- Ein konkretes Angebot, zum Beispiel ein Rabatt in Prozent
- Ein sichtbarer CTA-Button
- Knappheit oder Verfuegbarkeit
- Lokales Vertrauenssignal, etwa Lager im eigenen Land
- Ein Platz-Hook, der das Kernproblem in zwei Zahlen fasst: "22 Paare. 1 Hantel."

## Varianten testen

Pro Konzept mehrere Copy-Varianten erzeugen, die je einen anderen Hebel ziehen: Platz,
Angebot, Tempo, Umfang, Verfuegbarkeit. Was gewinnt, entscheidet der Test, nicht der Geschmack.
