#!/bin/bash

# Database initialization and migration script for Docker

echo "🚀 Starting UAV Service Management with Integration Module..."

# Run integration database migration
echo "📊 Running integration database migration..."
python migrate_integrations.py

# Start the Flask application
echo "🌐 Starting Flask application..."
exec python run.py
