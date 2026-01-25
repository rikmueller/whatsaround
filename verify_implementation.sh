#!/bin/bash
# Verification script for AlongGPX implementation

echo "=========================================="
echo "AlongGPX Frontend Implementation Check"
echo "=========================================="
echo ""

# Check Python files
echo "📋 Checking Python files..."
python3 -m py_compile docker/app.py && echo "  ✓ docker/app.py syntax OK" || exit 1
python3 -m py_compile cli/main.py && echo "  ✓ cli/main.py syntax OK" || exit 1

# Check web directory structure
echo ""
echo "📁 Checking web directory structure..."
test -f web/package.json && echo "  ✓ web/package.json" || exit 1
test -f web/vite.config.ts && echo "  ✓ web/vite.config.ts" || exit 1
test -f web/tsconfig.json && echo "  ✓ web/tsconfig.json" || exit 1
test -f web/Dockerfile && echo "  ✓ web/Dockerfile" || exit 1
test -f web/index.html && echo "  ✓ web/index.html" || exit 1
test -f web/src/main.tsx && echo "  ✓ web/src/main.tsx" || exit 1
test -f web/src/App.tsx && echo "  ✓ web/src/App.tsx" || exit 1
test -f web/src/api.ts && echo "  ✓ web/src/api.ts" || exit 1
test -d web/src/components && echo "  ✓ web/src/components/" || exit 1

# Check components
echo ""
echo "📦 Checking React components..."
test -f web/src/components/UploadArea.tsx && echo "  ✓ UploadArea" || exit 1
test -f web/src/components/SettingsForm.tsx && echo "  ✓ SettingsForm" || exit 1
test -f web/src/components/ProgressCard.tsx && echo "  ✓ ProgressCard" || exit 1
test -f web/src/components/ResultsPanel.tsx && echo "  ✓ ResultsPanel" || exit 1

# Check Docker files
echo ""
echo "🐳 Checking Docker files..."
test -f docker/docker-compose.yml && echo "  ✓ docker-compose.yml" || exit 1
test -f docker/docker-compose.dev.yml && echo "  ✓ docker-compose.dev.yml" || exit 1
test -f web/Dockerfile && echo "  ✓ web/Dockerfile" || exit 1

# Check documentation
echo ""
echo "📚 Checking documentation..."
test -f docs/QUICKSTART-FRONTEND.md && echo "  ✓ QUICKSTART-FRONTEND.md" || exit 1
test -f docs/FRONTEND.md && echo "  ✓ FRONTEND.md" || exit 1
test -f IMPLEMENTATION_NOTES.md && echo "  ✓ IMPLEMENTATION_NOTES.md" || exit 1

# Check config files are intact
echo ""
echo "⚙️ Checking configuration files..."
test -f config.yaml && echo "  ✓ config.yaml" || exit 1
test -f presets.yaml && echo "  ✓ presets.yaml" || exit 1

echo ""
echo "=========================================="
echo "✅ All checks passed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Local testing:"
echo "   Terminal 1: python3 docker/app.py"
echo "   Terminal 2: cd web && npm install && npm run dev"
echo "   Browser: http://localhost:3000"
echo ""
echo "2. Docker testing:"
echo "   cd docker && docker-compose up"
echo "   Browser: http://localhost:3000"
echo ""
echo "For more details, see docs/QUICKSTART-FRONTEND.md"
