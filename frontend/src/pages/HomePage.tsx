import { Link } from 'react-router-dom'
import MarketingLayout from '../components/MarketingLayout'
import SeoMeta from '../components/SeoMeta'
import './MarketingPages.css'

export default function HomePage() {
  return (
    <MarketingLayout>
      <SeoMeta
        title="WhatsAround – Plan smarter nearby"
        description="Discover points of interest near you or along any route. Find restaurants, shops, accommodations, services and attractions using OpenStreetMap data."
        url="https://getwhatsaround.app/"
      />
      <section className="marketing-hero">
        <h1>Plan smarter with nearby insights.</h1>
        <p>
          WhatsAround helps you discover points of interest along any route or around any location.
          Search, filter, and organize results in seconds — then export maps and spreadsheets when you need them.
        </p>
      </section>

      <section className="marketing-container">
        <h2 className="marketing-section-title">Built for quick discovery</h2>
        <p className="marketing-section-subtitle">
          Use presets or custom filters to find restaurants, services, accommodations, or any OpenStreetMap tag.
        </p>
        <div className="marketing-grid">
          <div className="marketing-card">
            <h3>Search any area</h3>
            <p>Drop a marker or upload a GPX route to search around a single spot or across an entire journey.</p>
          </div>
          <div className="marketing-card">
            <h3>Export-ready results</h3>
            <p>Download Excel summaries or interactive HTML maps to share with teams or keep for later.</p>
          </div>
        </div>

        <div className="marketing-cta-panel">
          <div>
            <h3>Ready to explore?</h3>
            <p>Start a search in minutes with your own route or a quick marker.</p>
          </div>
          <Link to="/map" className="marketing-button primary">
            Open Map
          </Link>
        </div>
      </section>
    </MarketingLayout>
  )
}
