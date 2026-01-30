import { useEffect, useMemo, useState } from 'react'
import Modal from './Modal'
import './FilterSelectionModal.css'

type Props = {
  open: boolean
  mode: 'include' | 'exclude'
  existing: string[]
  onClose: () => void
  onSave: (filters: string[]) => void
}

const DEFAULT_SUGGESTIONS = [
  'tourism=camp_site',
  'tourism=alpine_hut',
  'amenity=shelter',
  'amenity=drinking_water',
  'amenity=toilets',
  'shop=supermarket',
  'amenity=bicycle_repair_station',
  'amenity=pub',
  'amenity=restaurant',
  'amenity=pharmacy',
]

export default function FilterSelectionModal({ open, mode, existing, onClose, onSave }: Props) {
  const [query, setQuery] = useState('')
  const [selection, setSelection] = useState<string[]>(existing)
  const [custom, setCustom] = useState('')

  useEffect(() => {
    setSelection(existing)
  }, [existing, open])

  const filteredSuggestions = useMemo(() => {
    if (mode === 'exclude') return []
    if (!query) return DEFAULT_SUGGESTIONS
    const q = query.toLowerCase()
    return DEFAULT_SUGGESTIONS.filter((s) => s.toLowerCase().includes(q))
  }, [mode, query])

  const toggle = (value: string) => {
    setSelection((prev) => (prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value]))
  }

  const deleteFilter = (value: string) => {
    setSelection((prev) => prev.filter((v) => v !== value))
  }

  const addCustom = () => {
    const val = custom.trim()
    if (!val || !val.includes('=')) return
    toggle(val)
    setCustom('')
  }

  return (
    <Modal
      open={open}
      title={`Select ${mode} filters`}
      onClose={onClose}
      footer={
        <>
          <button className="btn btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button className="btn btn-primary" onClick={() => onSave(selection)}>
            Save
          </button>
        </>
      }
    >
      {mode === 'include' && (
        <>
          <div className="filter-search">
            <input
              placeholder="Search suggestions"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <div className="filter-suggestions">
            {filteredSuggestions.map((s) => (
              <label key={s} className="filter-item">
                <input type="checkbox" checked={selection.includes(s)} onChange={() => toggle(s)} />
                <span>{s}</span>
              </label>
            ))}
          </div>
        </>
      )}
      <div className="custom-add">
        <label htmlFor="customFilter">Custom (key=value)</label>
        <div className="custom-row">
          <input
            id="customFilter"
            placeholder="amenity=bench"
            value={custom}
            onChange={(e) => setCustom(e.target.value)}
          />
          <button className="btn btn-secondary" onClick={addCustom}>
            Add
          </button>
        </div>
      </div>
      <div className="selected-list">
        {selection.length === 0 && <p className="muted">Nothing selected yet.</p>}
        {selection.map((s) => (
          <span key={s} className="chip">
            {s}
            <button
              className="chip-delete"
              onClick={() => deleteFilter(s)}
              aria-label={`Delete ${s}`}
              title="Remove filter"
            >
              ×
            </button>
          </span>
        ))}
      </div>
    </Modal>
  )
}
