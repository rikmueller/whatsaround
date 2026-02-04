import { Link } from 'react-router-dom'
import MarketingLayout from '../components/MarketingLayout'
import SeoMeta from '../components/SeoMeta'
import './MarketingPages.css'

export default function FeaturesPage() {
  return (
    <MarketingLayout>
      <SeoMeta
        title="Features | WhatsAround"
        description="Explore WhatsAround features: map-first discovery, presets, smart filtering, live progress, and export-ready results."
        url="https://getwhatsaround.app/features"
      />
      <section className="marketing-container">
        <h1 className="marketing-section-title">Features</h1>
        <p className="marketing-section-subtitle">
          Everything you need to discover and organize points of interest with a clean, fast workflow.
        </p>

        <div className="marketing-grid">
          <div className="marketing-card">
            <h3>Preset-powered discovery</h3>
            <p>Start with curated presets or build custom filters using standard OpenStreetMap tags.</p>
          </div>
          <div className="marketing-card">
            <h3>Map-first experience</h3>
            <p>See results on a live map with instant track rendering and real-time progress updates.</p>
          </div>
          <div className="marketing-card">
            <h3>Batch Overpass queries</h3>
            <p>Optimized batching reduces API calls while keeping searches responsive.</p>
          </div>
          <div className="marketing-card">
            <h3>Export tools</h3>
            <p>Download Excel files and interactive HTML maps for offline use or sharing.</p>
          </div>
          <div className="marketing-card">
            <h3>Flexible input modes</h3>
            <p>Upload GPX tracks or drop a map marker for quick, targeted exploration.</p>
          </div>
          <div className="marketing-card">
            <h3>Smart filtering</h3>
            <p>Include and exclude tags to surface exactly the results you care about.</p>
          </div>
        </div>

        <div className="marketing-cta-panel">
          <div>
            <h3>See it in action</h3>
            <p>Open the app and run your first search in minutes.</p>
          </div>
          <Link to="/map" className="marketing-button primary">
            Open the map
          </Link>
        </div>
      </section>
    </MarketingLayout>
  )
}
