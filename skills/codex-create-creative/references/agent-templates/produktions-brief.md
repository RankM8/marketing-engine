# Template: Produktions-Job (Zwei-Schritt, Struct-Prompts)
Platzhalter <...> ersetzen; via `whisperm8 agent run --json --cd <repo> "$(cat brief.txt)"` starten (detacht, NIE --wait in killbarem Wrapper).

---
# Agent <NAME>: <WELLE> — <N> Creatives (Zwei-Schritt + Logo-Referenz)

Arbeite im Repo <REPO>. NUR natives image_gen__imagegen, STRIKT SERIELL (nie zwei Aufrufe parallel). Bei Haenger (>3 Min) oder Stream-Fehler: abbrechen, 120s warten, bis zu 6 Versuche je Aufruf. Ein Fehlschlag bricht NIE den Batch ab; Konzepte ohne Versuch NIE als FAIL dokumentieren. Du beendest den Turn ERST, wenn jedes Konzept ein Final hat oder ZWEI dokumentierte echte Fehlversuche. Kein OpenRouter/API-Key/curl. KEINE git-Befehle.
SCHREIB-SCOPE: NUR <ZIELORDNER> (nur DEINE Konzept-IDs) und <TMP-ORDNER>. Verifikationsdatei EXKLUSIV: <VERIF-DATEI>.

## Deine Konzepte (JSONs in <KONZEPT-ORDNER>/<id>.json):
<ID-LISTE>

## Ablauf je Konzept (JSONs sind vollstaendige Briefs — NICHTS umdichten):
1. JSON lesen. ALLE Referenzen (referenzen.*) mit view_image ansehen; markante Bauteile im Posen-Foto zaehlen.
2. BASIS: image_gen__imagegen, referenced_image_paths=[pose, produkt_freisteller], Prompt = prompt_basis_struct als JSON-Text (json.dumps, indent=2) UNVERAENDERT → <TMP>/<id>_basis.png. QA: exakt QUADRATISCH (Pixelmasse pruefen), Produkt vs Freisteller (Teile zaehlen!), keine Extra-Produktinstanzen, Anatomie. Nicht quadratisch => EIN Retry mit Prefix 'SQUARE 1:1 canvas, width equals height. '
3. DESIGN: image_gen__imagegen, referenced_image_paths=[<Basis>, logo], Prompt = prompt_design_struct als JSON-Text UNVERAENDERT → <ZIEL>/<id>_v1.png (+ Basis als <id>_v1_base.png).
4. QA-VERTRAG (jedes Kriterium PASS/FAIL in die Verifikationsdatei): (1) QUADRAT (2) Produkt Teil-fuer-Teil vs Freisteller (3) exakt die Produktinstanzen aus der Pose-Ref (4) Drift Basis→Final (5) Logo-Buchstabenformen vs Referenz (6) Logo-Fail => composite_logo.py-Fallback (7) Copy ZEICHENGENAU inkl. Umbrueche + Umlaute ä/ö/ü (8) GENAU EIN % (9) GENAU EIN Streichpreis, nie Preise erfinden (10) Anatomie (11) Hierarchie (12) nichts angeschnitten, 5% Rand (13) Verbotsliste.
5. Sidecar <id>_v1.png.meta.json: {"gateway":"codex-imagegen","welle":"<WELLE>","konzept":"<id>","ref_images":[...],"basis":"<pfad>","prompt":"<design-prompt>"}

Budget: MAX <CAP> Aufrufe. Report: Urteilsverteilung, Format-Retries, Logo-Fallbacks, Aufrufe gesamt.
