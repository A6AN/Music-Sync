#!/bin/bash
# Oracle Cloud Run Command - Deploy Application
# Run this AFTER uploading the deployment package

set -e

echo "=== Music Sync App - Deployment ==="
echo "Starting at $(date)"

cd /home/ubuntu/music-sync-app

# Check if deployment package exists
if [ ! -f "music-sync-deploy.tar.gz" ]; then
    echo "❌ ERROR: music-sync-deploy.tar.gz not found!"
    echo "Please upload the deployment package first."
    echo ""
    echo "Upload using wget method:"
    echo "  wget https://YOUR-NGROK-URL/music-sync-deploy.tar.gz"
    exit 1
fi

# Extract if not already extracted
if [ ! -f "docker-compose.yml" ]; then
    echo "📦 Extracting deployment package..."
    tar -xzf music-sync-deploy.tar.gz
    echo "✅ Extracted successfully"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo "Creating .env from example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        echo "❌ ERROR: .env.example also missing!"
        echo "Please create .env file manually with your credentials."
        exit 1
    fi
    echo ""
    echo "📝 IMPORTANT: Edit .env file with your credentials:"
    echo "   nano .env"
    echo ""
    echo "Add these values:"
    echo "   SECRET_KEY=your_secret_key_here"
    echo "   SPOTIFY_CLIENT_ID=your_spotify_client_id"
    echo "   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret"
    echo ""
    read -p "Press Enter after you've edited .env..."
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x deploy.sh backup.sh restore.sh setup-cron.sh

# Create required directories
echo "📁 Creating directories..."
mkdir -p data backups logs

# Deploy with Docker Compose
echo "🚀 Deploying application..."
./deploy.sh

# Wait for container to be healthy
echo "⏳ Waiting for application to start..."
sleep 10

# Check if running
if docker ps | grep -q music-sync-web; then
    echo ""
    echo "========================================"
    echo "✅ Deployment Successful!"
    echo "========================================"
    echo ""
    echo "🌐 Access your app at:"
    echo "   http://140.245.21.42:8080"
    echo ""
    echo "📊 Check logs:"
    echo "   docker logs music-sync-web"
    echo ""
    echo "🔄 Restart app:"
    echo "   docker-compose restart"
    echo ""
    echo "⚠️  NEXT STEP: Update Spotify Redirect URI"
    echo "   Go to: https://developer.spotify.com/dashboard"
    echo "   Add redirect URI: http://140.245.21.42:8080/spotify/callback"
    echo ""
    echo "========================================"
else
    echo ""
    echo "❌ Deployment may have failed!"
    echo "Check logs with: docker logs music-sync-web"
fi
