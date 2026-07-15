# Do's & Don'ts — lebendes Learnings-Dokument

Jeder Generierungslauf traegt hier nach. Format: Datum · Kontext · Learning.
Neueste Eintraege OBEN anfuegen.

---

## 2026-07-14 · Batch 1 (Agents A+B, 12 Bilder 1:1)

**DON'T: Der QA-Selbstauskunft des Generierungs-Agents blind glauben.**
Agent B meldete alle Copy-Strings als "wortgetreu" — tatsaechlich hatte er die Review-Headline
eigenmaechtig zum Voll-Zitat erweitert UND die Konzept-Headline zusaetzlich als Sub gerendert
(Text-Dopplung). Der unabhaengige Review muss Strings gegen das Konzept-JSON DIFFEN, nicht nur
lesen. (Kreativ-Pointe: das Voll-Zitat war die bessere Headline — wurde bewusst ins Konzept
uebernommen. Abweichung erkannt ≠ Abweichung schlecht, aber sie muss ERKANNT werden.)

**DO: Batch-Weiterlauf explizit anordnen.**
Der allererste Batch-Job brach nach EINEM gescheiterten 9:16-Konzept den Gesamtauftrag ab.
Seit "Ein fehlgeschlagenes Konzept bricht NIEMALS den Batch ab" im Prompt steht, liefern die
Agents 6/6 bzw. 7 Aufrufe mit Retry sauber durch.

**Empirie Typografie:** Native imagegen rendert kurze de-CH-Copy (Headline, Sub, CHF-Preise,
Streichpreis, Rabatt-Kreis, CTA-Pille) zuverlaessig korrekt — 12/12 Bilder ohne
Rechtschreibfehler. Anfuehrungszeichen sind fehleranfaellig (1 Retry noetig).

**Offen 9:16:** Mittelspalten-Komposition ueberforderte den ersten Versuch (Produkt zu breit
fuer Mittel-Crop, Beschriftungen driften). 9:16 als eigene, neu komponierte Konzepte angehen,
nicht als Nebenprodukt der 1:1-Batches.

## 2026-07-14 · Personen-Creatives: die Treue-Leiter

Drei Methoden getestet, aufsteigende Treue:
1. **Person-Swap (Runde 1): produktnah/abweichend.** Personentausch rendert ALLES neu;
   Boden-Ablagen wurden matschig. Nur fuer Awareness akzeptabel, ehrlich graden.
2. **Background-only-Swap (Runde 2): produktnah.** Deutlich besser (Pose/Kleidung/Produkte
   nah), aber das native Tool hat KEINEN Masken-Parameter — auch 'keep the person' fuehrt
   zu Voll-Re-Rendering inkl. Gesicht. Nie als 'echt' verkaufen.
3. **Chroma-Key-Compositing (Runde 3, Greenscreen-Material): der 1:1-Weg.** Person+Produkt
   lokal freistellen (remove_chroma_key.py aus dem Codex-imagegen-Skill), nur die leere
   Hintergrund-Platte generieren, PIL-Compositing + Kontaktschatten. Echte Pixel bleiben echt.
   Voraussetzung: Greenscreen-Aufnahmen (deshalb schiesst der Kunde sie so).

## 2026-07-14 · Design-Pass: Logo-Fauxpas (Giuliano-Eskalation)

**DON'T: Ein Marken-Logo jemals nur TEXTUELL im Prompt anfordern.**
D1-Design-Pass schrieb 'small Fitagon wordmark top-right' ohne Logo-Referenz — das Modell
erfand eine generische FITAGON(R)-Wortmarke. Regel: Logo entweder (a) deterministisch per
composite_logo.py aus brand.json (100% echt, empfohlen) oder (b) als ZUSAETZLICHE Bild-Referenz
in referenced_image_paths mit 'wordmark exactly as in reference N'. Echte Wortmarken-PNGs:
Kunden/Fitagon/Meta-Ads/creatives/_assets/logo/ (aus den Original-SVGs konvertiert).

## 2026-07-14 · Welle P1: Overlay-Finishing-Regeln

**DO: Overlay-Headlines IMMER mit \n umbrechen.** `overlay_text.py` bricht nicht automatisch um —
lange Einzeiler laufen rechts aus dem Bild (4 von 5 P1-Overlays betroffen). Regel: Headline ab
~14 Zeichen an der Satz-/Sinngrenze umbrechen ("Laptop zu.\nHantel auf.").

**DO: CTA-Pille via `--cta` (seit 1a9a9a8 im Plugin).** Dunkle Pille gegenueber der Preis-Pille.

**DO: Overlay-Fixes sind kostenlos.** Basen (`*_base.png`) aufheben — Typo-Korrekturen brauchen
KEINE neue Generierung, nur einen neuen Overlay-Lauf (MARKETING_ENGINE_BRAND setzen!).

**Stilvergleich baked vs overlay (P1-125):** baked liefert integrierte Layouts (Typo-Poster,
Detail-Copy) ohne Anschnitt-Risiko; overlay liefert pixelgenaue Markentypo und blitzschnelle
Iteration. Beide behalten — baked fuer Poster-/Conversion-Layouts, overlay fuer Foto-Looks.

## 2026-07-14 · Personen-Serienrezept (Synthese aus Strategien H/I/J)

**Die Produktions-Rezeptur fuer Personen-Creatives** (Person+Szene komplett generiert, Produkt heilig):
1. **Multi-Referenz** (Agent-H-Befund): referenced_image_paths = [Posen-Foto, Produkt-Freisteller] —
   die 2. Referenz ankert das Produkt messbar besser als das Posen-Foto allein.
2. **Mehrfach-Versuche + Auslese** (Agent-J-Befund): Trefferquote "echt-nah" liegt bei ~25 %
   pro Einzelversuch — pro Zielmotiv 3-4 Versuche einplanen (kostenlos), NUR den besten behalten.
3. **Produktdominante Detail-Shots** (Agent-I-Befund): Hand-am-Selektor-Motive sind der
   driftaermste Personen-Pfad — ideal fuer Mechanik-Hooks.
4. Strenge Einzelbild-QA bleibt Pflicht (Plattenzahl zaehlen, Selektoren, Logo, Haende/Finger).
Ehrliche Einstufung: Personen-Creatives erreichen "echt-nah", nie garantiert 1:1 —
im Portal via Quelle-/Treue-Label transparent halten.

## 2026-07-14 · Giulianos Aesthetik-Urteil: Composites verworfen

**DON'T: Chroma-Key-Composites als Personen-Creatives ausliefern.**
Giulianos Urteil: sieht "PNG-maessig reingestopft" aus, keine schoene Creative — trotz
pixel-echter Treue. Zielbild: Person UND Umgebung KOMPLETT generiert (natuerlicher
Foto-Look), NUR das Produkt 1:1. Der Treue-Engpass (gehaltenes Produkt driftet beim
Voll-Rendering) wird ueber Strategien getestet: Multi-Referenz (Pose + Produkt-Freisteller
als 2. Ref), produktdominante Detail-Shots, Brute-Force mit strenger Auswahl-QA.

## 2026-07-14 · Chroma-Key-Compositing, Grounding-Learnings

**DO: Fuer Composites Posen mit BEIDEN Fuessen flach am Boden waehlen.**
Ueberkopf-Press mit angehobener Ferse (christian_03) liess sich auch nach Nachbesserung
nicht glaubwuerdig erden. Stehende Posen (stella_04) funktionieren nach einem Fix-Turn.
Posen-Auswahl fuer Composites: stehend, Gewicht auf beiden Fuessen, Bodenkontakt klar.

**DO: Compositing-Basics im ERSTEN Prompt mitgeben, nicht nachreichen:**
Bodenlinie + Personengroesse (75-85% Bildhoehe), Kontaktschatten pro Fuss UND pro
Boden-Objekt (weiche Ellipse, 35-45% Deckkraft), Farb-/Helligkeitsabgleich an die Platte,
--edge-contract 1 gegen Kantensaeume. Boden-Ablagen NICHT separat einsetzen, wenn sie im
Original nicht direkt neben der Person stehen — lieber weglassen (Cutout beschneiden).

## 2026-07-14 · Batch 2, Parallelitaets-Falle

**DON'T: Mehrere image_gen__imagegen-Aufrufe parallel starten.**
Agent E feuerte 4 Generierungen gleichzeitig — alle hingen minutenlang ohne Teilergebnis,
der Batch musste abgebrochen werden. Das native Tool arbeitet offenbar nur seriell pro
Session. Regel fuer jeden Batch-Prompt: 'STRIKT SERIELL: ein Aufruf, Ergebnis abwarten,
QA, dann der naechste.' Parallelitaet erreicht man ueber MEHRERE Codex-Jobs (disjunkte
Scopes), nie innerhalb eines Jobs.

**DON'T: Codex-Jobs ueber run --wait als Claude-Background-Task ohne Not beaufsichtigen.**
Kill des Background-Wrappers riss 3 laufende Codex-Turns mit (Prozessgruppe). Robuster:
run/send OHNE --wait (detacht) + separater Monitor-Poll auf `agent list`-Zustaende.

## 2026-07-14 · Arbeitsweise (Anweisung Giuliano)

**DO: Jedes Konzept vor der Generierung selbst kreativ reviewen.**
Codex-geschriebene Konzepte nie ungesehen generieren: Creative Vision pruefen (wie wirkt
das fertige Bild?), Copy schaerfen (Hook, Rhythmus, CH-Ton), dann erst in den
Generierungs-Job geben.

**DO: Generierung auf mehrere parallele Codex-Agents aufteilen.**
Verschiedene Richtungen gleichzeitig testen — aber IMMER mit disjunkten Schreib-Scopes
pro Agent (z.B. Agent A nur openrouter/flex-12-5kg/, Agent B nur .../flex-5-25kg/;
Review-/Verification-Dateien pro Agent eindeutig benennen). Commits nachgelagert
koordinieren, damit sich die Agents nicht in die Quere kommen.

## 2026-07-14 · Fitagon Flex, Gateway-Validierung

**DO: Referenz IMMER selbst ansehen, bevor sie in den Prompt geht.**
Higgsfield-Test 1 scheiterte, weil `black_1.jpg` blind als Referenz gewaehlt wurde — es war
ein Lifestyle-Foto mit zwei Models, kein Freisteller. Das Modell renderte das Produkt neu
und erfand eine Ablage. Regel: Referenzbild per Read/view_image sichten, Kategorie
(Freisteller/Mood/Pose) bestaetigen, DANN prompten.

**DO: Im Prompt nur Teile aufzaehlen, die WIRKLICH auf der Referenz sind.**
Der fehlgeschlagene Prompt behauptete eine "grey base tray", die die Referenz nicht zeigte —
das Modell hat sie gehorsam dazuerfunden. Der Prompt-Teil "KEEP ... exactly" wirkt nur fuer
real Sichtbares; alles andere ist eine Einladung zum Halluzinieren.

**DO: Freisteller-Referenz + Teil-fuer-Teil-Aufzaehlung = Background-Swap haelt.**
Codex-Test 2 (flex-5-25kg, lieferant-studio_02.png): Platten, gelbe Selektoren, schwarze
Ablage MIT Gewichtsaufdruck, Logo-Endplatte — alles erhalten, nur Hintergrund neu.
Archiviert: Kunden/Fitagon/Meta-Ads/creatives/_tests-codex-imagegen-2026-07-14/.

**DON'T: `referenced_image_paths` und `num_last_images_to_include` kombinieren.**
Tool-Regel, explizit verboten. Lokale Pfade → ersteres; nur Konversationsbilder (max 5) → letzteres.

**DON'T: Ergebnis in `$CODEX_HOME/generated_images/` liegen lassen.**
Der Auftrag muss das Kopieren ins Arbeitsverzeichnis explizit verlangen, sonst ist das
Bild fuer das Projekt verloren (native Signatur hat keinen Zielpfad-Parameter).

**DO: Groesse/Format ueber Nachbearbeitung loesen, nicht ueber das Tool.**
Nativ gibt es KEINE Groessen-/Qualitaets-/AR-Parameter; Ausgabe ist ~1254x1254. Hochformate
per Mittel-Crop (reframe.py), dafuer 9:16-first komponieren (Mittelspalte ~55 %). Nie
strecken, nie oben/unten "ergaenzen".

**DO: Edit-Referenzen vorher mit `view_image` laden lassen.**
Tool-Vorgabe fuer lokale Dateien; gehoert in jeden Subagent-Prompt.

**Timing-Erwartung:** Text-zu-Bild ~18 s, Edit mit Referenz ~85 s pro Bild. 32-Bilder-Batch
also grob 45-60 Min reine Generierungszeit einplanen.

**DON'T: Eigenes Treue-Urteil als final behandeln.**
Anweisung Giuliano: Claude erkennt 1:1-Echtheit nicht zuverlaessig allein. Immer
Doppel-Review (Codex vergleicht per view_image gegen Referenz + eigener Vergleich), nur
doppelt bestaetigte Bilder sind "echt".

## image_gen ist GLOBAL seriell (15.07.2026, v3-Produktionswelle)
- 5 parallele Codex-Jobs (je intern seriell) führten zu `stream disconnected`-Turn-Fails und 3-Minuten-Hängern bei ALLEN Jobs — das imagegen-Backend des Accounts verkraftet nur EINEN aktiven Aufruf, egal aus wie vielen Sessions.
- DON'T: mehrere Generierungs-Jobs gleichzeitig laufen lassen. DO: einen Job zur Zeit; Orchestrierung sequenziell (send → poll → nächster Job).
- Agenten neigen bei Abbrüchen dazu, unbearbeitete Konzepte als "FAIL/nicht produziert" zu deklarieren und den Turn zu beenden — Resume via `whisperm8 agent send <id>` mit expliziter "Turn nicht beenden bevor alles abgearbeitet"-Anweisung funktioniert (Session-Kontext bleibt).
- Turn-Fails durch Stream-Abbruch sind per `send` fortsetzbar (codexThreadID bleibt gültig).

## User-Direktive: KEIN Cut-out-Compositing (15.07.2026, Giuliano)
- Produkt/Person/Szene NIEMALS als Freisteller ausschneiden und einkleben — immer voll generativ: image_gen mit Referenzbildern (Pose + Produkt-Freisteller), Szene komplett NACHBAUEN.
- Qualitaet kommt aus Referenz-Fuehrung + strukturierten JSON-Prompts + Auslese (harte QA, Regen bei Drift) — nicht aus Compositing.
- Einzige geduldete Ausnahme: Logo-Fallback per composite_logo.py, wenn die generierte Wortmarke von der Referenz abweicht (Option-B-Sicherheitsnetz, User-abgesegnet).
