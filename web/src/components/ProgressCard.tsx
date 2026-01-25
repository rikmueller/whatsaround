import React from 'react'
import { JobStatus } from '../api'
import './ProgressCard.css'

interface ProgressCardProps {
  status: JobStatus
}

const ProgressCard: React.FC<ProgressCardProps> = ({ status }) => {
  const getStateIcon = (state: string) => {
    switch (state) {
      case 'queued':
        return '⏳'
      case 'processing':
        return '⚙️'
      case 'completed':
        return '✓'
      case 'failed':
        return '✕'
      default:
        return '•'
    }
  }

  const getStateLabel = (state: string) => {
    switch (state) {
      case 'queued':
        return 'Queued'
      case 'processing':
        return 'Processing'
      case 'completed':
        return 'Completed'
      case 'failed':
        return 'Failed'
      default:
        return 'Unknown'
    }
  }

  return (
    <div className="progress-card">
      <div className="progress-header">
        <div className="progress-title">
          <span className="state-icon">{getStateIcon(status.state)}</span>
          <div>
            <h2>{status.project_name}</h2>
            <p className="state-label">{getStateLabel(status.state)}</p>
          </div>
        </div>
        <div className="progress-percent">{status.percent}%</div>
      </div>

      <div className="progress-bar-container">
        <div className="progress-bar">
          <div
            className={`progress-fill ${status.state}`}
            style={{ width: `${status.percent}%` }}
          />
        </div>
      </div>

      <div className="progress-message">{status.message}</div>

      {status.state === 'completed' && (
        <div className="progress-summary">
          <div className="summary-item">
            <span className="label">POIs Found:</span>
            <span className="value">{status.rows_count}</span>
          </div>
          <div className="summary-item">
            <span className="label">Track Length:</span>
            <span className="value">{status.track_length_km?.toFixed(1)} km</span>
          </div>
        </div>
      )}

      {status.state === 'failed' && (
        <div className="progress-error">
          <strong>Error:</strong> {status.error}
        </div>
      )}

      <div className="progress-meta">
        <small>Started: {new Date(status.created_at).toLocaleString()}</small>
      </div>
    </div>
  )
}

export default ProgressCard
