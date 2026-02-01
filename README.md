# AlongGPX

**Find OpenStreetMap POIs along your GPX tracks. Plan smarter: campsites, water sources, shelters, restaurants—everything you need along your route.**

**🌐 Try it online: [along-gpx.de](https://along-gpx.de)**

---

## 💡 How to Use

### 1. Upload Your GPX Track

- Drag and drop your `.gpx` file onto the map
- Your track appears instantly (blue line with start/end markers)
- Map automatically centers on your route

### 2. Choose What to Find

**Quick presets:**
- 🏕️ Campsites
- 💧 Drinking water
- 🏠 Accommodation (hotels, hostels, B&Bs)
- 🍴 Food & restaurants
- 🏪 Shops & supermarkets
- 🚽 Public toilets
- ⛺ Shelters

**Custom filters:**
Build your own using OpenStreetMap tags (e.g., `amenity=restaurant`, `shop=bicycle`)

### 3. Generate Results

- Set your search radius (1-50 km from track)
- Click **Process**

### 4. Explore Results

- **Interactive map** - Click markers for details (name, distance, website, hours)
- **Excel export** - Sorted by distance from start, with all metadata
- **Multiple tile layers** - OpenStreetMap, OpenTopoMap, CyclOSM
- **Mobile-friendly** - Works on phones and tablets

---

## ⚠️ Development Status

This project is under active development. Features and APIs may change. Documentation may lag behind implementation. Use at your own risk for production workloads.

**Current focus:** Stabilizing Docker deployment and improving UI/UX.

---


## 🚀 Getting Started

AlongGPX offers **four ways to run** the application, depending on your needs:

### 🌐 Web Interface (Recommended)

**Use online:** Visit [along-gpx.de](https://along-gpx.de) - no installation required

**Self-host with Docker:**
```bash
git clone https://github.com/rikmueller/alonggpx.git
cd alonggpx/config/docker-prod
cp .env.example .env
docker compose up -d
```
Open http://localhost:3000

📖 Full guide: [config/docker-prod/README.md](config/docker-prod/README.md)

### ⌨️ Command-Line Interface

For batch processing and automation:
```bash
python3 cli/main.py --gpx-file data/input/route.gpx --preset camp_sites_tent
```

📖 Setup instructions: [config/cli/README.md](config/cli/README.md)

### 💻 Local Development

Run backend and frontend locally for development:
```bash
# Terminal 1: Backend
python3 backend/api/app.py

# Terminal 2: Frontend
cd frontend && npm run dev
```

📖 Development setup: [config/local-dev/README.md](config/local-dev/README.md)

### 🐳 Docker Development

Development environment with hot reload:
```bash
cd config/docker-dev
docker compose up
```

📖 Docker dev guide: [config/docker-dev/README.md](config/docker-dev/README.md)

---

## 🏗️ Project Structure

```
AlongGPX/
├── backend/              # Python backend
│   ├── api/             # Flask REST API
│   └── core/            # Processing pipeline (GPX, Overpass, filtering)
├── cli/                 # Command-line interface
├── frontend/            # React + TypeScript web UI
│   └── src/
│       ├── components/  # UI components (Map, Settings, Modals)
│       └── hooks/       # WebSocket integration
├── config/              # Configuration by usage mode
│   ├── cli/            # CLI standalone
│   ├── local-dev/      # Local development
│   ├── docker-dev/     # Docker with hot reload
│   └── docker-prod/    # Production Docker
├── deployment/          # Docker build files
└── data/
    ├── presets.yaml    # Filter presets
    ├── input/          # GPX files
    └── output/         # Generated results
```

### Key Technologies

**Backend:**
- Python 3.x with Flask for REST API
- pandas + openpyxl for Excel export
- Folium for map generation
- pyproj for geodesic calculations
- Overpass API for OSM queries

**Frontend:**
- React 18 + TypeScript
- Vite for fast development
- Leaflet + React-Leaflet for interactive maps
- Socket.IO for real-time updates
- Axios for API communication

**Infrastructure:**
- Docker Compose for containerization
- Nginx for production reverse proxy

---

## ✨ Key Features

- **🗺️ Map-first interface** - See your track and POIs continuously
- **⚡ Real-time updates** - POIs appear as they're found
- **📱 Mobile responsive** - Collapsible settings, touch-friendly
- **🎨 Smart coloring** - Different colors for different POI types
- **🎯 Accurate distances** - WGS84 geodesic calculations
- **📦 Self-contained** - Runs offline after setup (uses public Overpass API)
- **🔒 Privacy-focused** - Your GPX files never leave your device/server

---

## ⚙️ Configuration

AlongGPX is configured via environment variables. See respective configuration directories for available options.

**Filter presets** are defined in [data/presets.yaml](data/presets.yaml). Add your own!

---

## 📖 Documentation

### Usage Guides
- **[Docker Production](config/docker-prod/README.md)** - Self-hosted production deployment
- **[Docker Development](config/docker-dev/README.md)** - Development with hot reload
- **[Local Development](config/local-dev/README.md)** - Local Flask + Vite setup
- **[CLI Usage](config/cli/README.md)** - Command-line batch processing

### Technical Documentation
- **[FRONTEND.md](FRONTEND.md)** - Frontend architecture, component design, API integration, and development guide

---

## 🤝 Contributing

Contributions welcome! Please open an issue first to discuss major changes.

### Development Setup

```bash
# Clone repository
git clone https://github.com/rikmueller/along-gpx.git
```
---

## 📜 License

MIT License - see [LICENSE](LICENSE) for details

---

## 🙏 Credits

Built with amazing open-source projects:

- **[OpenStreetMap](https://www.openstreetmap.org/)** - Community-driven map data
- **[Overpass API](https://overpass-api.de/)** - OSM query infrastructure
- **[React](https://react.dev/)** + **[TypeScript](https://www.typescriptlang.org/)** - Modern web framework
- **[Leaflet](https://leafletjs.com/)** - Interactive maps
- **[Flask](https://flask.palletsprojects.com/)** - Python web framework
- **[pandas](https://pandas.pydata.org/)** + **[openpyxl](https://openpyxl.readthedocs.io/)** - Data processing
- **[Folium](https://python-visualization.github.io/folium/)** - Python → Leaflet maps

Inspired by **[GPX Studio](https://gpx.studio/)** ❤️



