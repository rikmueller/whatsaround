import axios from 'axios'

const API_BASE = '/api'

export interface ConfigResponse {
  defaults: {
    project_name: string
    radius_km: number
    step_km: number | null
    include: string[]
    exclude: string[]
  }
  seline?: {
    enabled: boolean
    token?: string | null
  }
  presets: string[]
  presets_detail: {
    [key: string]: {
      name?: string
      category?: string
      info?: string
      include: string[]
      exclude: string[]
    }
  }
  marker_color_palette?: string[]
  default_marker_color?: string
}

export interface JobStatus {
  id: string
  state: 'queued' | 'processing' | 'completed' | 'failed'
  percent: number
  message: string
  project_name: string
  created_at: string
  excel_file: string | null
  html_file: string | null
  rows_count: number | null
  track_length_km: number | null
  error: string | null
}

export interface GeoJsonFeature {
  type: 'Feature'
  geometry:
    | { type: 'LineString'; coordinates: [number, number][] }
    | { type: 'Point'; coordinates: [number, number] }
  properties: Record<string, any>
}

export interface GeoJsonResponse {
  type: 'FeatureCollection'
  features: GeoJsonFeature[]
}

export const apiClient = {
  async getConfig(): Promise<ConfigResponse> {
    const response = await axios.get(`${API_BASE}/config`)
    return response.data
  },

  async startProcessing(
    file: File | null,
    projectName: string,
    radiusKm: number,
    includes: string[],
    excludes: string[],
    presets: string[] = [],
    markerPosition: [number, number] | null = null,
  ): Promise<{ job_id: string; status_url: string }> {
    const formData = new FormData()
    
    // Add file or marker position based on input mode
    if (file) {
      formData.append('file', file)
    } else if (markerPosition) {
      formData.append('marker_lat', markerPosition[0].toString())
      formData.append('marker_lon', markerPosition[1].toString())
    }
    
    formData.append('project_name', projectName)
    formData.append('radius_km', radiusKm.toString())
    includes.forEach((inc) => formData.append('include', inc))
    excludes.forEach((exc) => formData.append('exclude', exc))
    presets.forEach((preset) => formData.append('preset', preset))

    const response = await axios.post(`${API_BASE}/process`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  async getJobStatus(jobId: string): Promise<JobStatus> {
    const response = await axios.get(`${API_BASE}/status/${jobId}`)
    return response.data
  },

  async getGeoJson(jobId: string): Promise<GeoJsonResponse> {
    const response = await axios.get(`${API_BASE}/job/${jobId}/geojson`)
    return response.data
  },

  getExcelDownloadUrl(jobId: string): string {
    return `${API_BASE}/download/excel/${jobId}`
  },

  getHtmlMapUrl(jobId: string): string {
    return `${API_BASE}/download/html/${jobId}`
  },
}
