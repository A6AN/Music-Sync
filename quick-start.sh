#!/bin/bash
# Quick start script for Music Sync

echo "🎵 Music Sync - Quick Start Setup"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your Spotify credentials"
    echo "   Get them from: https://developer.spotify.com/dashboard"
    echo ""
    echo "   Run this to generate SECRET_KEY:"
    echo "   python3 -c \"import secrets; print('SECRET_KEY=' + secrets.token_hex(32))\""
    echo ""
    read -p "Press Enter after you've edited .env..."
else
    echo "✅ .env file exists"
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements-web.txt

# Initialize database
echo ""
echo "🗄️  Initializing database..."
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Database initialized!')"

echo ""
echo "=================================="
echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo "  python3 app.py"
echo ""
echo "Then open your browser to:"
echo "  http://localhost:5000"
echo ""
echo "For deployment instructions, see DEPLOYMENT.md"
echo "=================================="
