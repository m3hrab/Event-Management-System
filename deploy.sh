#!/bin/bash

# DUET Events Production Deployment Script
# Run this script as root or with sudo privileges

set -e

# Configuration
APP_NAME="duet-events"
APP_USER="www-data"
APP_DIR="/var/www/$APP_NAME"
SERVICE_FILE="/etc/systemd/system/$APP_NAME.service"
NGINX_SITE="/etc/nginx/sites-available/$APP_NAME"
BACKUP_DIR="/var/backups/$APP_NAME"

echo "Starting deployment of DUET Events Management System..."

# Create application directory
echo "Creating application directory..."
sudo mkdir -p $APP_DIR
sudo chown $APP_USER:$APP_USER $APP_DIR

# Create backup directory
echo "Creating backup directory..."
sudo mkdir -p $BACKUP_DIR

# Copy application files
echo "Copying application files..."
sudo cp -r . $APP_DIR/
sudo chown -R $APP_USER:$APP_USER $APP_DIR

# Create virtual environment
echo "Setting up Python virtual environment..."
cd $APP_DIR
sudo -u $APP_USER python3 -m venv venv
sudo -u $APP_USER $APP_DIR/venv/bin/pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
sudo -u $APP_USER mkdir -p $APP_DIR/logs
sudo -u $APP_USER mkdir -p $APP_DIR/instance/uploads

# Set up environment file
echo "Setting up environment configuration..."
if [ ! -f $APP_DIR/.env ]; then
    sudo -u $APP_USER cp $APP_DIR/.env.example $APP_DIR/.env
    echo "Please edit $APP_DIR/.env with your production settings"
fi

# Install and configure systemd service
echo "Installing systemd service..."
sudo cp $APP_DIR/duet-events.service $SERVICE_FILE
sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME

# Configure nginx
echo "Configuring nginx..."
if [ ! -f $NGINX_SITE ]; then
    sudo cp $APP_DIR/nginx.conf $NGINX_SITE
    sudo ln -sf $NGINX_SITE /etc/nginx/sites-enabled/
    echo "Please edit $NGINX_SITE and configure SSL certificates"
fi

# Database setup
echo "Setting up database..."
cd $APP_DIR
sudo -u $APP_USER $APP_DIR/venv/bin/python -c "
from app import create_app, db
app = create_app('production')
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"

# Set proper permissions
echo "Setting file permissions..."
sudo chown -R $APP_USER:$APP_USER $APP_DIR
sudo chmod -R 755 $APP_DIR
sudo chmod -R 775 $APP_DIR/instance/uploads
sudo chmod -R 775 $APP_DIR/logs

# Start services
echo "Starting services..."
sudo systemctl start $APP_NAME
sudo systemctl restart nginx

# Check status
echo "Checking service status..."
sudo systemctl status $APP_NAME --no-pager
sudo systemctl status nginx --no-pager

echo "Deployment completed!"
echo ""
echo "Next steps:"
echo "1. Edit $APP_DIR/.env with your production settings"
echo "2. Configure SSL certificates in $NGINX_SITE"
echo "3. Update the domain name in nginx configuration"
echo "4. Test the application at http://your-domain.com"
echo ""
echo "Service management commands:"
echo "  Start:   sudo systemctl start $APP_NAME"
echo "  Stop:    sudo systemctl stop $APP_NAME"
echo "  Restart: sudo systemctl restart $APP_NAME"
echo "  Status:  sudo systemctl status $APP_NAME"
echo "  Logs:    sudo journalctl -u $APP_NAME -f"
