#!/bin/bash

# Alternative start script for Render
# This ensures gunicorn is available and starts the app properly

echo "Starting DUET Events Management System..."

# Check if gunicorn is installed, if not install it
if ! command -v gunicorn &> /dev/null; then
    echo "Installing gunicorn..."
    pip install gunicorn==21.2.0
fi

# Create necessary directories
mkdir -p instance/uploads
mkdir -p logs

# Initialize database if needed
python -c "
from app import create_app, db
import os
os.environ.setdefault('FLASK_ENV', 'production')
app = create_app()
with app.app_context():
    db.create_all()
    print('Database initialized')
"

# Start the application
echo "Starting gunicorn server..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 run:app
