import React from 'react'
import './UploadArea.css'

interface UploadAreaProps {
  onFileSelected: (file: File) => void
  selectedFile: File | null
}

const UploadArea: React.FC<UploadAreaProps> = ({ onFileSelected, selectedFile }) => {
  const [isDragActive, setIsDragActive] = React.useState(false)
  const inputRef = React.useRef<HTMLInputElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true)
    } else if (e.type === 'dragleave') {
      setIsDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      if (file.name.endsWith('.gpx')) {
        onFileSelected(file)
      }
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelected(e.target.files[0])
    }
  }

  const handleClick = () => {
    inputRef.current?.click()
  }

  return (
    <div className="upload-area">
      <h2>📂 Upload GPX Track</h2>

      <div
        className={`upload-zone ${isDragActive ? 'active' : ''} ${selectedFile ? 'selected' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".gpx"
          onChange={handleChange}
          hidden
        />

        {!selectedFile ? (
          <>
            <div className="upload-icon">📍</div>
            <p className="upload-primary">Drag and drop your GPX file here</p>
            <p className="upload-secondary">or click to browse</p>
          </>
        ) : (
          <>
            <div className="upload-icon">✓</div>
            <p className="upload-primary">File selected</p>
            <p className="upload-secondary">{selectedFile.name}</p>
          </>
        )}
      </div>

      <p className="upload-hint">Supported format: .gpx</p>
    </div>
  )
}

export default UploadArea
