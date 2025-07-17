#!/bin/bash

# Render.com build script
# This script runs during the build phase on Render

echo "Starting Render build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p instance/uploads
mkdir -p logs

# Set up database (SQLite for Render)
echo "Setting up database..."
python -c "
from app import create_app, db
import os

# Set environment for production
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'render-default-key-change-me')

app = create_app('production')
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"

echo "Build completed successfully!"
