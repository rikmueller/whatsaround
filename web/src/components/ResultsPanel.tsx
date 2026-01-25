import React from 'react'
import { JobStatus, apiClient } from '../api'
import './ResultsPanel.css'

interface ResultsPanelProps {
  status: JobStatus
  onReset: () => void
}

const ResultsPanel: React.FC<ResultsPanelProps> = ({ status, onReset }) => {
  const handleExcelDownload = () => {
    if (status.excel_file) {
      const url = apiClient.getExcelDownloadUrl(status.excel_file)
      window.location.href = url
    }
  }

  const handleMapView = () => {
    if (status.html_file) {
      const url = apiClient.getHtmlMapUrl(status.html_file)
      window.open(url, '_blank')
    }
  }

  return (
    <div className="results-panel">
      <div className="results-header">
        <div className="results-title">
          <span className="icon">✅</span>
          <h1>Processing Complete!</h1>
        </div>
        <p className="results-subtitle">{status.project_name}</p>
      </div>

      <div className="results-grid">
        <div className="result-card map-card">
          <div className="card-icon">🗺️</div>
          <h3>Interactive Map</h3>
          <p className="card-description">View all POIs on an interactive Folium map</p>
          <p className="card-meta">Points found: {status.rows_count}</p>
          <button onClick={handleMapView} className="btn btn-primary">
            Open Map
          </button>
        </div>

        <div className="result-card excel-card">
          <div className="card-icon">📊</div>
          <h3>Excel Export</h3>
          <p className="card-description">Download detailed data with all POI information</p>
          <p className="card-meta">Track: {status.track_length_km?.toFixed(1)} km</p>
          <button onClick={handleExcelDownload} className="btn btn-primary">
            Download Excel
          </button>
        </div>
      </div>

      <div className="results-summary">
        <h3>Summary</h3>
        <ul className="summary-list">
          <li>
            <span className="summary-label">Points of Interest Found:</span>
            <strong>{status.rows_count}</strong>
          </li>
          <li>
            <span className="summary-label">Track Length:</span>
            <strong>{status.track_length_km?.toFixed(1)} km</strong>
          </li>
          <li>
            <span className="summary-label">Completed At:</span>
            <strong>{new Date(status.created_at).toLocaleString()}</strong>
          </li>
        </ul>
      </div>

      <div className="results-actions">
        <button onClick={onReset} className="btn btn-secondary">
          ← Process Another Track
        </button>
      </div>
    </div>
  )
}

export default ResultsPanel
