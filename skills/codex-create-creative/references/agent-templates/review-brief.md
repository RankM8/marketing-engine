# Template: Unabhaengiger Schiedsrichter-Review (read-only, KEINE Generierung)
`whisperm8 agent run --json --sandbox read-only --cd <repo> "$(cat brief.txt)"` — Achtung: read-only-Jobs koennen nicht committen; Ergebnis-Datei danach selbst stagen ODER workspace-write nutzen.

---
# Codex-Auftrag: Abschluss-Review <WELLE> (KEINE Generierung)

Du bist der unabhaengige Schiedsrichter — du generierst NICHTS, du urteilst. Im Zweifel IMMER abwerten.
Je Final in <ORDNER>: (a) Sidecar lesen, Konzept-JSON laden, ALLE Referenzen mit view_image ansehen. (b) PRODUKTTREUE = K.-o.: Teil-fuer-Teil gegen den ECHTEN Freisteller — Bauteile ZAEHLEN, jede Abweichung disqualifiziert. Exakt die Produktinstanzen der Pose-Referenz (keine Extras/leere Ablagen). (c) Copy ZEICHENGENAUER DIFF gegen copy-Feld (Umbrueche, Umlaute, genau EIN %, EIN Streichpreis). (d) Logo-Buchstabenformen gegen Referenz. (e) Anatomie/Composite-Look. (f) Format + Safe-Margin.
Urteil je Final: echt-nah / produktnah / abweichend + 1 Satz. Output-Tabelle nach <REVIEW-DATEI>. Abschnitt 'Regen-Empfehlung': Liste der Finals, die neu generiert gehoeren, mit Fail-Grund.
