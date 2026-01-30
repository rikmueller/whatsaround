# Web Frontend for AlongGPX

This is the web frontend for the AlongGPX application built with React and Vite.

## Development

```bash
npm install
npm run dev
```

The dev server will proxy `/api` requests to `http://localhost:5000` (Flask backend).

## Building for Production

```bash
npm run build
npm run preview
```

## File Structure

- `src/` - React components and logic
- `src/api.ts` - API client for communicating with Flask backend
- `src/components/` - Reusable UI components
- `public/` - Static assets

## Features

- 📂 Drag-and-drop GPX file upload
- ⚙️ Configurable settings (radius, filters, presets)
- ⏳ Real-time progress tracking
- 🗺️ Interactive Folium map viewer
- 📊 Excel export download
