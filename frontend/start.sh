#!/bin/bash

# Force Match Frontend - Quick Start Script

echo "🌟 Starting Force Match Frontend..."
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Start the development server
echo "🚀 Launching development server..."
echo "📍 The app will be available at: http://localhost:3000"
echo ""
npm run dev
