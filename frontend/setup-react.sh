#!/bin/bash
# Frontend React Setup Script
# This script creates the full React project structure for Crop Zen

set -e

echo "🚀 Setting up Crop Zen React Frontend..."

# Create directory structure
mkdir -p src/components/{Auth,Dashboard,Farms,Predictions,Common}
mkdir -p src/pages
mkdir -p src/services
mkdir -p src/redux/slices
mkdir -p src/hooks
mkdir -p public

echo "✅ Created directory structure"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

echo "✅ Frontend setup complete!"
echo ""
echo "Next steps:"
echo "1. Create .env file: cp .env.example .env"
echo "2. Start dev server: npm run dev"
echo "3. Open http://localhost:3000"
