#!/bin/bash

# Alternative start script for Render
# This ensures gunicorn is available and starts the app properly

echo "Starting DUET Events Management System..."

# Check if gunicorn is installed, if not install it
if ! command -v gunicorn &> /dev/null; then
    echo "Installing gunicorn..."
    pip install gunicorn==21.2.0
fi

# Create necessary directories in current working directory
echo "Creating directories..."
mkdir -p instance/uploads
mkdir -p logs

# Set proper permissions
chmod 755 instance 2>/dev/null || true
chmod 755 instance/uploads 2>/dev/null || true

echo "Current working directory: $(pwd)"
echo "Directory contents:"
ls -la

# Start the application - let Flask handle database creation
echo "Starting gunicorn server..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --preload run:app
