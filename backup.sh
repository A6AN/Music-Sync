#!/bin/bash
# Database backup script

set -e

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_PATH="./data/music_sync.db"
BACKUP_FILE="$BACKUP_DIR/music_sync_$TIMESTAMP.db"

# Keep last N backups
KEEP_BACKUPS=10

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}💾 Starting database backup...${NC}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    echo "❌ Database file not found: $DB_PATH"
    exit 1
fi

# Create backup
echo "Creating backup: $BACKUP_FILE"
cp "$DB_PATH" "$BACKUP_FILE"

# Compress backup
echo "Compressing backup..."
gzip "$BACKUP_FILE"
BACKUP_FILE="${BACKUP_FILE}.gz"

# Calculate backup size
SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo -e "${GREEN}✅ Backup created: $BACKUP_FILE ($SIZE)${NC}"

# Clean old backups (keep last N)
echo "Cleaning old backups (keeping last $KEEP_BACKUPS)..."
cd "$BACKUP_DIR"
ls -t music_sync_*.db.gz 2>/dev/null | tail -n +$((KEEP_BACKUPS + 1)) | xargs -r rm --
cd - > /dev/null

# Show all backups
echo ""
echo "Available backups:"
ls -lh "$BACKUP_DIR"/music_sync_*.db.gz 2>/dev/null || echo "No backups found"

echo -e "${GREEN}✅ Backup completed successfully!${NC}"
