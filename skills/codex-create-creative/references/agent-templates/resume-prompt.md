# Template: Resume-Prompt (Auto-Heal nach Turn-Abbruch/Stagnation)
Via `whisperm8 agent send <id> --json "..."` — Session-Kontext bleibt erhalten.

---
Setze deinen Auftrag fort. Stream-Fehler/Haenger bei image_gen sind MOEGLICH und NORMAL:
1. Bei Haenger (>3 Min): abbrechen, 120s warten, denselben Aufruf wiederholen (bis 6 Versuche). Danach: Konzept ueberspringen, am Batch-Ende erneut.
2. Ueberspringe jedes Konzept, dessen finales <id>_v1.png bereits existiert.
3. Turn ERST beenden, wenn jedes Konzept ein Final hat oder ZWEI dokumentierte echte Fehlversuche.
4. Konzepte ohne Versuch NIE als FAIL dokumentieren.
5. Strikt seriell, voller QA-Vertrag, Sidecars, Verifikationsdatei aktualisieren.

Heal-Monitor-Muster: Hintergrund-Loop prueft alle 2 Min Job-State + Soll-Dateien; ist der Job idle und Motive fehlen => send mit diesem Prompt (max 8x). Stagniert ein Job ueber mehrere Resumes (Session degradiert): Job stoppen und FRISCHEN Job fuer die Rest-IDs starten statt weiter zu resumen.
