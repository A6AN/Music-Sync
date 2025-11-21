#!/bin/bash
# Deployment script for Oracle Cloud

set -e

echo "🚀 Starting deployment..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo "Please copy .env.example to .env and configure it first:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating directories...${NC}"
mkdir -p data backups logs

# Stop existing containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose down 2>/dev/null || true

# Pull latest changes (if using git)
if [ -d .git ]; then
    echo -e "${YELLOW}📥 Pulling latest changes...${NC}"
    git pull || true
fi

# Build and start containers
echo -e "${YELLOW}🔨 Building Docker image...${NC}"
docker-compose build --no-cache

echo -e "${YELLOW}🚀 Starting containers...${NC}"
docker-compose up -d

# Wait for container to be healthy
echo -e "${YELLOW}⏳ Waiting for application to be ready...${NC}"
sleep 10

# Check if container is running
if docker ps | grep -q music_sync_app; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo -e "${GREEN}🌐 Application is running at http://localhost:5000${NC}"
    echo ""
    echo "Useful commands:"
    echo "  View logs:        docker-compose logs -f"
    echo "  Stop app:         docker-compose down"
    echo "  Restart app:      docker-compose restart"
    echo "  View status:      docker-compose ps"
    echo ""
    echo "Backup database:  ./backup.sh"
else
    echo -e "${RED}❌ Deployment failed! Container is not running.${NC}"
    echo "Check logs with: docker-compose logs"
    exit 1
fi
