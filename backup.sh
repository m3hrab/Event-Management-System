#!/bin/bash

# DUET Events Backup Script

set -e

# Configuration
APP_NAME="duet-events"
APP_DIR="/var/www/$APP_NAME"
BACKUP_DIR="/var/backups/$APP_NAME"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.tar.gz"

echo "Starting backup of DUET Events Management System..."

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Stop the application
echo "Stopping application..."
sudo systemctl stop $APP_NAME

# Create backup
echo "Creating backup..."
tar -czf $BACKUP_FILE \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='logs/*.log' \
    -C $(dirname $APP_DIR) $(basename $APP_DIR)

# Start the application
echo "Starting application..."
sudo systemctl start $APP_NAME

# Clean old backups (keep last 7 days)
echo "Cleaning old backups..."
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
echo "Backup size: $(du -h $BACKUP_FILE | cut -f1)"
