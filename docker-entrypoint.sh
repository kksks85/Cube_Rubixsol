#!/bin/bash

# Simple entrypoint script for Docker

echo "🚀 Starting CUBE PRO Work Order Management System..."

# Create instance directory if it doesn't exist
mkdir -p /app/instance

# Set proper permissions
chmod 755 /app/instance

echo "🌐 Starting Flask application..."
echo "📊 Database will be initialized on first access..."

# Start the Flask application
exec python run.py
