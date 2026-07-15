---
name: setup-portal
description: Lokales Creative-Portal installieren — zeigt alle Creatives aus einem beliebigen (Drive-/OneDrive-)Ordner als chronologische Timeline mit Lightbox und Filter im Browser. Nutzen bei "Portal installieren", "Portal aufsetzen", "Creatives-Portal", "setup portal", "Portal einrichten", "Bilder-Timeline aus Drive-Ordner". Kein Hosting, kein Account: Astro-App läuft lokal, Daten kommen aus dem gesyncten Ordner.
---

# setup-portal — lokales Creative-Portal aus einem Ordner

Installiert das mitgelieferte Portal-Template (`template/` in diesem Skill-Ordner) als
lokale Astro-App. Datenquelle ist ein beliebiger lokaler Ordner — typischerweise der per
Google Drive / OneDrive gesyncte Creatives-Ordner des Kunden. Das Portal indexiert ihn
per Catch-All (jedes Bild, auch aus neuen Unterordnern) und zeigt eine Timeline mit
Lightbox, Quellen-Filter und Pfad-Kopieren-Button.

## Ablauf (Schritt für Schritt, mit dem User abstimmen)

1. **Preflight:**
   - `node --version` (>= 18) und `python3 --version` prüfen. Fehlt Node: auf
     https://nodejs.org verweisen (LTS-Installer) und NACH der Installation weitermachen —
     nicht mit Fehlern weiterlaufen.
   - Den User nach dem **Quellordner** fragen (der lokal gesynchte Creatives-Ordner).
     Prüfen, dass er existiert und Bilder enthält. Bei Google Drive liegt er unter
     `~/Library/CloudStorage/GoogleDrive-<account>/…` (macOS) bzw. `G:\` (Windows) —
     Voraussetzung ist die installierte Drive-/OneDrive-Desktop-App.
2. **Installieren:** Zielordner mit dem User klären (Default: `~/creative-portal`), dann
   das komplette `template/`-Verzeichnis dorthin kopieren und `npm install` ausführen.
3. **Konfigurieren:** `portal.config.json.example` nach `portal.config.json` kopieren und
   `titel` + `quelle` (absoluter Pfad des Quellordners) eintragen.
4. **Starten:** `npm run start` (indexiert + startet Dev-Server auf Port 4340) und dem
   User http://localhost:4340 öffnen. Für Dauerbetrieb zusätzlich `npm run watch` in
   einem zweiten Terminal — indexiert alle 30 s neu, neue Drive-Syncs erscheinen
   automatisch.
5. **Verifizieren:** Seite im Browser prüfen (Bildanzahl > 0, Lightbox öffnet). Erst dann
   als fertig melden.

## Technische Details

- `scripts/gen-creatives.py` liest `portal.config.json`, kopiert Bilder flach nach
  `public/creatives/_gen/` und schreibt `src/data/creatives.ts`. Verwaiste Kopien werden
  entfernt — der Quellordner ist die einzige Wahrheit.
- **Zeitstempel:** Liegt im Quell-Root eine `manifest.json`
  (`{"<dateiname>": {"generiert": <epoch>}}`), gewinnt sie über die Datei-mtime — wichtig,
  weil Drive-Sync mtimes verfälschen kann. Die Produktionsseite (z. B. handoff-sync)
  sollte dieses Manifest mitliefern.
- Unterstützte Formate: png/jpg/jpeg/webp. Versteckte Dateien/Ordner werden ignoriert.
- Das Portal ist reine Ansicht — es verändert den Quellordner nie.

## Abgrenzung

- Creatives GENERIEREN: Skill `codex-create-creative` (bzw. `create-product-image` für
  Pay-per-Use). Dieses Portal zeigt nur an.
- Für das interne RankM8-Arbeitsportal (Analytics, Research, Winning-Ads) ist dieses
  Template bewusst NICHT gedacht — es ist die schlanke Übergabe-Ansicht für Kunden/Teams.
