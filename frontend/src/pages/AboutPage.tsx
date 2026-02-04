import { Link } from 'react-router-dom'
import MarketingLayout from '../components/MarketingLayout'
import SeoMeta from '../components/SeoMeta'
import './MarketingPages.css'

export default function AboutPage() {
  return (
    <MarketingLayout>
      <SeoMeta
        title="About | WhatsAround"
        description="Learn why WhatsAround was built and how open data powers fast, reliable points-of-interest discovery."
        url="https://getwhatsaround.app/about"
      />
      <section className="marketing-container">
        <h1 className="marketing-section-title">About WhatsAround</h1>
        <p className="marketing-section-subtitle">
          WhatsAround turns OpenStreetMap data into easy-to-use insights for planning, scouting, and exploration.
        </p>

        <div className="marketing-panel">
          <div>
            <h3 className="marketing-section-title">Why we built it</h3>
            <p className="marketing-section-subtitle">
              We wanted a fast way to discover services and destinations around routes and locations without
              juggling multiple tools. WhatsAround combines a clean UI, reliable geodesic calculations, and
              export-ready results so you can move from idea to action quickly.
            </p>
          </div>
          <div>
            <h3 className="marketing-section-title">Powered by open data</h3>
            <p className="marketing-section-subtitle">
              Results are built on OpenStreetMap and the Overpass API, delivering a transparent, community-driven
              data source with detailed tagging and global coverage.
            </p>
          </div>
        </div>

        <div className="marketing-cta-panel">
          <div>
            <h3>Explore the platform</h3>
            <p>Open the app to start a new search or return to the homepage for a quick overview.</p>
          </div>
          <div className="marketing-hero-actions">
            <Link to="/map" className="marketing-button primary">
              Open the map
            </Link>
            <Link to="/home" className="marketing-button ghost">
              Back to home
            </Link>
          </div>
        </div>
      </section>
    </MarketingLayout>
  )
}
