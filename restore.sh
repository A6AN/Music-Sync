#!/bin/bash
# Database restore script

set -e

BACKUP_DIR="./backups"
DB_PATH="./data/music_sync.db"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}📥 Database Restore Utility${NC}"
echo ""

# List available backups
echo "Available backups:"
ls -lht "$BACKUP_DIR"/music_sync_*.db.gz 2>/dev/null | nl || {
    echo -e "${RED}No backups found in $BACKUP_DIR${NC}"
    exit 1
}

echo ""
read -p "Enter the number of the backup to restore (or 'q' to quit): " choice

if [ "$choice" = "q" ]; then
    echo "Restore cancelled."
    exit 0
fi

# Get the selected backup file
BACKUP_FILE=$(ls -t "$BACKUP_DIR"/music_sync_*.db.gz 2>/dev/null | sed -n "${choice}p")

if [ -z "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ Invalid selection${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Selected backup: $BACKUP_FILE${NC}"
echo ""
read -p "⚠️  This will replace the current database. Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

# Stop the application
echo -e "${YELLOW}Stopping application...${NC}"
docker-compose down 2>/dev/null || true

# Backup current database
if [ -f "$DB_PATH" ]; then
    CURRENT_BACKUP="$BACKUP_DIR/before_restore_$(date +%Y%m%d_%H%M%S).db"
    echo "Backing up current database to: $CURRENT_BACKUP"
    cp "$DB_PATH" "$CURRENT_BACKUP"
fi

# Restore the backup
echo "Restoring backup..."
gunzip -c "$BACKUP_FILE" > "$DB_PATH"

echo -e "${GREEN}✅ Database restored successfully!${NC}"
echo ""
read -p "Start the application now? (yes/no): " start

if [ "$start" = "yes" ]; then
    docker-compose up -d
    echo -e "${GREEN}✅ Application started${NC}"
else
    echo "Start the application manually with: docker-compose up -d"
fi
