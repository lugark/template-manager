## 🧠 **README.md**

````{"variant":"standard","title":"README.md für lasercut-manager","id":"40283"}
# 🧩 Lasercut Manager (Docker + Python)

Ein leichtgewichtiges, Docker-basiertes **Digital Asset Management (DAM)** für Lasercut-Vorlagen.  
Scant automatisch einen gemounteten Ordner, erzeugt Thumbnails, speichert Tags in SQLite/MySQL und bietet eine Weboberfläche mit Tag-Suche.

---

## 🚀 Features

- 📁 **Ordner-Scan:** Liest automatisch alle Dateien in `/data` (z. B. ZIP, SVG, PDF, JPG).
- 🖼️ **Thumbnails:** Nutzt vorhandene `preview.jpg/png` oder generiert neue (SVG → PNG, PDF → PNG).
- 🏷️ **Tagging:** Verwaltung von Tags direkt über die Weboberfläche.
- 🔍 **Suche:** Filterung nach Tags oder Dateinamen.
- 🗃️ **Speicherung:** SQLite (Standard) oder MySQL.
- 🐋 **Docker-basiert:** Einfaches Deployment mit `docker-compose`.

---

## 🧱 Projektstruktur

```
app/
├── main.py          # Flask App & Routing
├── models.py        # SQLAlchemy Models
├── scanner.py       # Dateiscanner & Thumbnail-Generator
├── templates/
│   └── index.html   # Weboberfläche
├── static/
│   ├── thumbnails/  # generierte Previews
│   └── style.css    # CSS Layout
└── db/
    └── data.sqlite  # lokale DB (automatisch erstellt)
```

---

## ⚙️ Installation & Start

1. **Clone Repository**
   ```bash
   git clone https://github.com/<user>/lasercut-manager.git
   cd lasercut-manager
   ```

2. **Docker-Setup**
   ```bash
   docker compose up -d --build
   ```

3. **Zugriff**
   → Öffne [http://localhost:8080](http://localhost:8080)

---

## 🧩 Konfiguration

| Variable | Beschreibung |
|-----------|---------------|
| `DATABASE_URL` | Datenbankverbindung (z. B. `sqlite:///app/db/data.sqlite` oder `mysql+pymysql://user:pass@mysql/db`) |
| `/data` | Gemounteter Ordner mit deinen Vorlagen (read-only empfohlen) |
| `/app/static/thumbnails` | Ordner für generierte Thumbnails |

---

## 🛠 Erweiterungen

- **Automatisches Re-Scanning** per Cronjob oder Button in der Weboberfläche
- **Benutzerverwaltung** (Auth) über Flask-Login
- **REST-API** für externe Abfragen (z. B. `GET /api/assets?tag=holz`)

---

## 💡 Tech Stack

- Python 3.12 + Flask
- SQLAlchemy ORM
- Pillow, cairosvg, pdf2image für Bildverarbeitung
- SQLite oder MySQL
- Docker Compose für Containerisierung

---

## 🧪 Entwicklung in Cursor

1. Öffne das Projekt in **Cursor IDE**
2. Lies `.cursorrules` für kontextbezogene Assistenz
3. Generiere oder erweitere Module (z. B. Tag-API, Thumbnail-Service)
4. Teste lokal mit:
   ```bash
   python app/main.py
   ```
