# osm_finder

**osm_finder** ist ein modulares Python‑Tool, das OpenStreetMap‑Daten entlang eines GPX‑Tracks analysiert.  
Es kombiniert:

- GPX‑Verarbeitung  
- Overpass‑API‑Abfragen  
- flexible OSM‑Filter (inkl. Presets)  
- Excel‑Export  
- interaktive Folium‑Karten  

Das Projekt ist ideal für Bikepacking‑Routen, Wanderwege, Outdoor‑Planung, Campingplatz‑Suche oder jede Art von OSM‑Analyse entlang eines Tracks.

---

## 🚀 Features

- **GPX‑Track einlesen** und Streckenlänge berechnen  
- **Segmentierte Overpass‑Abfragen** entlang des Tracks  
- **Beliebige OSM‑Filter** (Include/Exclude)  
- **Preset‑System** für häufige Suchtypen  
- **Automatische Filtervalidierung**  
- **Excel‑Export** aller gefundenen Objekte  
- **Interaktive Folium‑Karte** mit Track + Markern  
- **Vollständig konfigurierbar über YAML + CLI**  
- **Modulare Codebasis** für einfache Erweiterbarkeit  

---



## 📁 Projektstruktur
osm_finder/
├── main.py
├── config.yaml
├── presets.yaml
├── README.md
└── core/
├── init.py
├── cli.py
├── config.py
├── presets.py
├── overpass.py
├── gpx_processing.py
├── filtering.py
├── folium_map.py
└── export.py


---

## 🛠️ Installation

### 1. Repository klonen

```bash
git clone https://github.com/<DEIN_USERNAME>/osm_finder.git
cd osm_finder
pip install -r requirements.txt
```

⚙️ Konfiguration
Alle Standard‑Einstellungen findest du in:

config.yaml
