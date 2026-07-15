# Struct-Prompt-Format — strukturierte JSON-Prompts für image_gen

Prosa-Prompts lassen dem Bildmodell Interpretationsraum; strukturierte JSON-Spezifikationen
zwingen es in jede Einzelentscheidung. A/B-validiert (Fitagon, 15.07.2026): Struct-Prompts
eliminierten erfundene Preise, Produkt-Duplikate und Copy-Drift, die derselbe Inhalt als
Prosa wiederholt produzierte.

**Anwendung:** Der komplette Struct-Block wird als JSON-Text (`json.dumps(spec, indent=2)`)
UNVERÄNDERT als `prompt` an `image_gen__imagegen` übergeben. Die Specs leben als Felder
`prompt_basis_struct` / `prompt_design_struct` in den Konzept-JSONs.

## Schritt 1: prompt_basis_struct (textfreies Basis-Foto)

```json
{
  "task": "Create ONE photorealistic advertising base photo",
  "output": {"aspect_ratio": "1:1 perfect square", "note": "width EXACTLY equals height"},
  "references": {
    "reference_1": "POSE source — replicate body position, grip and camera angle exactly",
    "reference_2": "PRODUCT source — the EXACT product, pixel-faithful"
  },
  "person": {
    "replace_person_from_reference_1_with": "<Casting-Beschreibung: Name, Alter, Haare, Statur, Outfit>",
    "skin": "natural texture with pores, believable muscle tone, no AI-smooth plastic look",
    "hands": "exactly five fingers per hand, natural grip like reference 1"
  },
  "pose": "<exakte Posen-Beschreibung>",
  "product": {
    "source": "reference_2 EXACTLY",
    "rules": [
      "count the visible parts in reference 1 and reproduce the same count",
      "<jedes markante Bauteil als eigene Regel: Platten/Rillen, Clips, Endplatte+Logo, Griff>"
    ],
    "no_additional_units": "HARD RULE: exactly the units visible in reference 1 — no extras, no empty trays, no duplicates; if in doubt show FEWER units, never more"
  },
  "environment": {"scene": "<Szene>", "mood": "<Mood>", "props": "NOTHING beyond the scene description"},
  "camera": {"style": "commercial campaign", "lens": "50mm", "aperture": "f/2.8",
             "framing": "<Layout-Hinweis> — leave the text zone visually calm"},
  "grade": "high-end retouch, rich deep blacks, clean whites, slightly warm highlights",
  "negatives": ["no text", "no typography", "no watermark", "no extra props"]
}
```

## Schritt 2: prompt_design_struct (integriertes Ad-Design auf der Basis)

```json
{
  "task": "DESIGN a premium Meta performance ad ON the finished photograph (reference_1)",
  "keep": "the ENTIRE photo pixel-faithful — everything stays EXACTLY as in reference_1",
  "canvas": {"aspect_ratio": "same square as reference_1", "safe_margin": "5% on all four edges — no element may touch or cross the border"},
  "brand_font": "<Font-Charakteristik, z.B. ultra-bold condensed grotesk, line-height 0.95, sentence case>",
  "elements": {
    "headline": {
      "position": "<Position>",
      "line_1": {"text": "<EXAKTER Text>", "color": "<Farbe>"},
      "line_2": {"text": "<EXAKTER Text>", "color": "<Farbe>"},
      "size": "each line 9-11% of image height",
      "rules": ["render each line EXACTLY ONCE", "no repetition", "never over face or product"]
    },
    "subline": {"text": "<EXAKTER Text>", "position": "directly below headline"},
    "price_block": {
      "pill": {"text": "<Preis>", "style": "<Pillen-Stil>"},
      "strike_price": {"text": "<Streichpreis>", "style": "ONE clean single strikethrough line"},
      "rules": ["the pill price is NOT struck through", "exactly ONE struck-through price",
                "no further price mentions anywhere", "never invent a different price"]
    },
    "discount_badge": {"text": "<-XX%>", "shape": "circle",
                       "rules": ["the percent sign appears EXACTLY ONCE in the whole image"]},
    "logo": {"source": "reference_2 (wordmark file)", "position": "top-right corner", "width": "20% of image width",
             "rules": ["EXACT letterforms from reference_2", "do NOT redesign, do NOT retype"]}
  },
  "integration": ["soft contact shadows under pills/badges", "type picks up scene ambient light"],
  "hierarchy": ["1 headline", "2 subject with product", "3 price block", "4 brand mark"],
  "typography_fidelity": "render German umlauts (ä, ö, ü) exactly as written — never transliterate; Swiss German spelling (ss statt ß)",
  "negatives": ["no extra icons", "no emojis", "no borders", "no gradient washes", "no second logo",
                "no invented slogans", "no additional text of any kind"]
}
```

## Regeln

- **Texte immer EXAKT vordefiniert** — das Modell darf nie formulieren, nur setzen.
- Copy-Quelle ist das `copy`-Feld des Konzept-JSONs; Struct-Texte müssen damit identisch sein
  (Konverter nutzen, nie von Hand doppelt pflegen).
- Jede beobachtete Fehlklasse wird eine neue `rules`-Zeile (z. B. "never invent a different
  price" nach Preis-Halluzination) — Learnings in `dos-and-donts.md` spiegeln.
- Versalien sind erlaubt, wenn die Copy sie vorgibt — Maßstab ist Zeichengenauigkeit,
  nicht die Stilregel.
