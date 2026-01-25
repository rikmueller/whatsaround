import React from 'react'
import { ConfigResponse } from '../api'
import './SettingsForm.css'

interface SettingsFormProps {
  config: ConfigResponse
  settings: {
    projectName: string
    radiusKm: number
    includes: string[]
    excludes: string[]
    presets: string[]
  }
  onChange: (settings: any) => void
  onStart: () => void
  isProcessing: boolean
}

const SettingsForm: React.FC<SettingsFormProps> = ({
  config,
  settings,
  onChange,
  onStart,
  isProcessing,
}) => {
  const handleAddFilter = (type: 'include' | 'exclude') => {
    const value = prompt(`Enter new ${type} filter (e.g., tourism=camp_site):`)
    if (value) {
      onChange({
        ...settings,
        [type === 'include' ? 'includes' : 'excludes']: [
          ...(type === 'include' ? settings.includes : settings.excludes),
          value,
        ],
      })
    }
  }

  const handleRemoveFilter = (type: 'include' | 'exclude', index: number) => {
    const list = type === 'include' ? settings.includes : settings.excludes
    const updated = list.filter((_, i) => i !== index)
    onChange({
      ...settings,
      [type === 'include' ? 'includes' : 'excludes']: updated,
    })
  }

  const handlePresetToggle = (preset: string) => {
    const updated = settings.presets.includes(preset)
      ? settings.presets.filter((p) => p !== preset)
      : [...settings.presets, preset]
    onChange({
      ...settings,
      presets: updated,
    })
  }

  return (
    <div className="settings-form">
      <h2>⚙️ Settings</h2>

      <div className="form-group">
        <label>Project Name</label>
        <input
          type="text"
          value={settings.projectName}
          onChange={(e) =>
            onChange({
              ...settings,
              projectName: e.target.value,
            })
          }
          disabled={isProcessing}
        />
      </div>

      <div className="form-group">
        <label>Search Radius: {settings.radiusKm} km</label>
        <input
          type="range"
          min="1"
          max="50"
          value={settings.radiusKm}
          onChange={(e) =>
            onChange({
              ...settings,
              radiusKm: parseFloat(e.target.value),
            })
          }
          disabled={isProcessing}
          className="slider"
        />
        <p className="help-text">Distance to search around each track segment</p>
      </div>

      <div className="form-group">
        <label>Presets</label>
        <div className="preset-grid">
          {config.presets.map((preset) => (
            <label key={preset} className="preset-chip">
              <input
                type="checkbox"
                checked={settings.presets.includes(preset)}
                onChange={() => handlePresetToggle(preset)}
                disabled={isProcessing}
              />
              <span>{preset}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label>Include Filters (OSM Tags)</label>
        <div className="filter-chips">
          {settings.includes.map((filter, idx) => (
            <div key={idx} className="filter-chip">
              <span>{filter}</span>
              <button
                onClick={() => handleRemoveFilter('include', idx)}
                disabled={isProcessing}
                className="chip-remove"
              >
                ×
              </button>
            </div>
          ))}
        </div>
        <button
          onClick={() => handleAddFilter('include')}
          disabled={isProcessing}
          className="btn btn-secondary btn-sm"
        >
          + Add Include
        </button>
      </div>

      <div className="form-group">
        <label>Exclude Filters (OSM Tags)</label>
        <div className="filter-chips">
          {settings.excludes.map((filter, idx) => (
            <div key={idx} className="filter-chip exclude">
              <span>{filter}</span>
              <button
                onClick={() => handleRemoveFilter('exclude', idx)}
                disabled={isProcessing}
                className="chip-remove"
              >
                ×
              </button>
            </div>
          ))}
        </div>
        <button
          onClick={() => handleAddFilter('exclude')}
          disabled={isProcessing}
          className="btn btn-secondary btn-sm"
        >
          + Add Exclude
        </button>
      </div>

      <button
        onClick={onStart}
        disabled={isProcessing}
        className="btn btn-primary btn-large"
      >
        {isProcessing ? 'Processing...' : '🚀 Generate'}
      </button>
    </div>
  )
}

export default SettingsForm
