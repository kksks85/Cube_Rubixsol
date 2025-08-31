#!/bin/bash
# Production deployment script for UAV Service Management Tool

echo "🚀 Starting UAV Service Management Tool deployment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Build and start the application
echo "📦 Building Docker image..."
docker-compose build

echo "🏃 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are healthy
echo "🔍 Checking service health..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
    echo ""
    echo "🌐 Your UAV Service Management Tool is available at:"
    echo "   - http://localhost:5000 (Direct app access)"
    echo "   - http://localhost:80 (With Nginx - if using production profile)"
    echo ""
    echo "📊 To view logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 To stop services:"
    echo "   docker-compose down"
else
    echo "❌ Services failed to start. Check logs:"
    docker-compose logs
    exit 1
fi
