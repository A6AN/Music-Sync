#!/bin/bash
# Setup automatic backups with cron

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="$SCRIPT_DIR/backup.sh"

# Make backup script executable
chmod +x "$BACKUP_SCRIPT"

# Create cron job (daily at 2 AM)
CRON_JOB="0 2 * * * $BACKUP_SCRIPT >> $SCRIPT_DIR/logs/backup.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
    echo "✅ Cron job already exists"
else
    # Add cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Cron job added: Daily backups at 2 AM"
fi

echo ""
echo "Current cron jobs:"
crontab -l

echo ""
echo "Backup logs will be saved to: $SCRIPT_DIR/logs/backup.log"
