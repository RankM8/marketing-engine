# Apify-Actor-Auswahl

## Generischer Ablauf

1. Im Apify Store nach dem Namen des Marktplatzes suchen.
2. Das Input-Schema und die Beispiele des Actors pruefen: Loest er technisch das
   konkrete Ziel (Suche, Kategorie-Scrape oder Produkt-Detail)? Erwartete Inputs,
   Outputs und Limits vergleichen.
3. Bei technisch gleichwertigen Actors Pay-per-Use bevorzugen.
4. Immer zuerst einen Mini-Testlauf mit genau einer Suche und wenigen Items
   ausfuehren. Erst danach groessere Runs starten oder einen Actor kaufen.
5. Vor jedem Kauf mit dem Agenten klaeren, welches konkrete Problem der Actor
   loest. Kein Monats-Abo ohne verifizierten, wiederkehrenden Bedarf abschliessen.

## Learnings aus dem Fitagon-Call vom 16.07.2026

- Galaxus-Actors waren durchweg kostenpflichtig. Der meistgenutzte Actor kostete
  20 USD pro Monat und bot einen 120-Minuten-Trial.
- Eine Pay-per-Use-Alternative kostete ungefaehr 0,003 USD pro Produkt.
- Die getesteten Gratis-Varianten lieferten unbrauchbare Ergebnisse.
- Fuer Decathlon funktionierte ein Pay-per-Use-Actor mit Suchfunktion. Der
  Mini-Test fand 27 Kurzhanteln.
- Der zuerst getestete Decathlon-Actor passte technisch nicht zum Ziel. Deshalb
  ist die Schema-Pruefung vor einem Lauf oder Kauf verpflichtend.

Preise und Actor-Angebote koennen sich aendern. Vor der Auswahl die aktuellen
Store-Angaben pruefen; die Werte oben sind Call-Learnings, keine Preisgarantie.

## Token und Accounts

- Den Apify-Token nie in Chats einfuegen und nie committen. Ihn als
  `APIFY_TOKEN` in der Projekt-/Ordner-Konfiguration hinterlegen, zum Beispiel in
  einer ignorierten `.env`-Datei oder ueber einen in `AGENTS.md` dokumentierten
  Verweis auf die lokale Secret-Konfiguration.
- Fuer Kundenarbeit einen Firmen-Account statt privater Accounts verwenden.
- Eine `.env`-Datei wird vom Skript nicht automatisch geladen. Die Variable vor
  dem Aufruf in die Prozessumgebung laden oder ueber die Laufzeitumgebung setzen.
