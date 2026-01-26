import './BrandingHeader.css'

type Props = {
  title: string
  subtitle?: string
}

export default function BrandingHeader({ title, subtitle }: Props) {
  return (
    <header className="branding-header">
      <div className="branding-glass">
        <div className="branding-text">
          <div className="branding-title">{title}</div>
          {subtitle && <div className="branding-subtitle">{subtitle}</div>}
        </div>
      </div>
    </header>
  )
}
