import { useEffect, useMemo, useState } from 'react'
import Modal from './Modal'
import './PresetSelectionModal.css'

type PresetDetail = {
  name?: string
  category?: string
  info?: string
  include: string[]
  exclude: string[]
}

type Props = {
  open: boolean
  selected: string[]
  presetsDetail: Record<string, PresetDetail>
  onClose: () => void
  onSave: (presets: string[]) => void
}

export default function PresetSelectionModal({ open, selected, presetsDetail, onClose, onSave }: Props) {
  const [query, setQuery] = useState('')
  const [selection, setSelection] = useState<string[]>(selected)

  useEffect(() => {
    setSelection(selected)
  }, [selected, open])

  const grouped = useMemo(() => {
    const out: Record<string, Array<{ id: string; detail: PresetDetail }>> = {}
    Object.entries(presetsDetail).forEach(([id, detail]) => {
      const category = detail.category || 'Other'
      if (!out[category]) out[category] = []
      out[category].push({ id, detail })
    })
    return out
  }, [presetsDetail])

  const filtered = useMemo(() => {
    if (!query) return grouped
    const q = query.toLowerCase()
    const out: typeof grouped = {}
    Object.entries(grouped).forEach(([cat, items]) => {
      const matches = items.filter(({ id, detail }) => {
        return (
          id.toLowerCase().includes(q) ||
          (detail.name || '').toLowerCase().includes(q) ||
          (detail.info || '').toLowerCase().includes(q)
        )
      })
      if (matches.length > 0) out[cat] = matches
    })
    return out
  }, [grouped, query])

  const toggle = (id: string) => {
    setSelection((prev) => (prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]))
  }

  return (
    <Modal
      open={open}
      title="Select presets"
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
      <div className="preset-search">
        <input
          placeholder="Search presets"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      <div className="preset-groups">
        {Object.entries(filtered).sort(([a], [b]) => a.localeCompare(b)).map(([category, items]) => (
          <div key={category} className="preset-group">
            <div className="preset-cat">{category}</div>
            <div className="preset-list">
              {items.map(({ id, detail }) => (
                <label key={id} className="preset-item">
                  <input
                    type="checkbox"
                    checked={selection.includes(id)}
                    onChange={() => toggle(id)}
                  />
                  <div className="preset-info">
                    <div className="preset-name">{detail.name || id}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>
        ))}
        {Object.keys(filtered).length === 0 && <p className="muted">No presets match your search.</p>}
      </div>
    </Modal>
  )
}
