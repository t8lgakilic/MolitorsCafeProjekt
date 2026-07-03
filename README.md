# Molitor's Cafe

Ein kleines Buchungssystem für Molitor's Cafe im Rahmen des ABV-Moduls "Programmieren für Wirtschaftswissenschaftler*innen".
Die Anwendung erfasst Einnahmen und Ausgaben des Cafés, speichert sie persistent in SQLite und zeigt eine einfache GuV-Auswertung im Frontend.

## Gruppenmitglieder

- Fuat Bartu Adanur
- Tolga Kilic

## Funktionen

- Neue Café-Buchungen mit Datum, Betrag, Kategorie, Typ und Beschreibung erfassen
- Bestehende Buchungen aus der Datenbank abrufen
- GuV-Auswertung bis zu einem gewählten Datum anzeigen
- Kategorien mit Matplotlib visualisieren
- Kreative Erweiterung: Dashboard mit monatlicher Entwicklung, Kategorieanteilen, periodischen Buchungen, einfachem Forecast für erwarteten Gewinn und vereinfachter Einkommensteuer-Schätzung 2026 für Umsatz-Kategorien

Typische Kategorien sind zum Beispiel Kaffeeumsatz, Gebäckumsatz, Miete, Personal, Einkauf oder Wartung.
Die Steuer-Schätzung zählt Einnahmen aus Kategorien, die "Umsatz" enthalten, unabhängig von Groß- und Kleinschreibung.

## Projektaufbau

- `src/wiwiss_booking/api.py`: FastAPI-Backend und API-Routen
- `src/wiwiss_booking/database.py`: SQLite-Anbindung und Datenbankzugriffe
- `src/wiwiss_booking/models.py`: Pydantic-Modelle für Validierung und Typprüfung
- `src/wiwiss_booking/analytics.py`: Pandas-Auswertungen und Forecast
- `src/wiwiss_booking/frontend.py`: Streamlit-Frontend

Das Frontend greift nicht direkt auf die Datenbank zu. Alle Daten laufen über die FastAPI.

## Lokal starten

Abhängigkeiten installieren:

```bash
uv sync
```

Backend starten:

```bash
uv run uvicorn wiwiss_booking.api:app --reload
```

In einem zweiten Terminal das Frontend starten:

```bash
uv run streamlit run src/wiwiss_booking/frontend.py
```

Die API-Dokumentation ist danach unter `http://127.0.0.1:8000/docs` erreichbar.

## GenAI-Nutzung

Bei der Erstellung dieses Projekts wurde OpenAI Codex als KI-Werkzeug verwendet.
Codex wurde eingesetzt für:

- Strukturierung des Projekts nach den Anforderungen der Aufgabenstellung
- Erstellung erster Code-Entwürfe für FastAPI, SQLite, Pydantic, Pandas und Streamlit
- Debugging und technische Prüfung der API-Endpunkte
- Formulierung dieser README

Die Projektlogik, das Datenmodell und die kreative Erweiterung wurden gemeinsam geplant und können vor der Abgabe weiter angepasst werden.

# Molitor's Cafe Booking App

## Projekt starten

### Backend starten
```bash
uv run uvicorn wiwiss_booking.api:app --reload
```

### Frontend starten
```bash
uv run streamlit run src/wiwiss_booking/frontend.py
```

## Beschreibung

Diese Anwendung ist ein Café-Buchungssystem mit:

- FastAPI Backend
- Streamlit Frontend
- SQLite Datenbank

## Wichtige Dateien

- `frontend.py` → Benutzeroberfläche
- `api.py` → Backend/API
- `database.py` → Datenbankverbindung
- `models.py` → Datenmodelle
- `analytics.py` → Analysen und Statistiken

## Hinweis

`uv.lock` wurde automatisch generiert und verwaltet die Paketversionen des Projekts.