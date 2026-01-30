#!/bin/bash

# AlongGPX Web Frontend Quick Start

set -e

echo "🚀 AlongGPX Web Frontend Setup"
echo "=============================="
echo ""

# Check if in the correct directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the web/ directory."
    exit 1
fi

echo "📦 Installing dependencies..."
npm install

echo ""
echo "✅ Setup complete!"
echo ""
echo "Development mode:"
echo "  npm run dev       - Start dev server with hot reload"
echo ""
echo "Production build:"
echo "  npm run build     - Build for production"
echo "  npm run preview   - Preview production build locally"
echo ""
echo "From the repo root, you can use Docker:"
echo "  docker-compose up                    - Run production build"
echo "  docker-compose -f docker-compose.dev.yml up  - Run development with hot reload"
echo ""
