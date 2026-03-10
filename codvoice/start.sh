#!/bin/bash

echo "Starting CODVOICE - Cloud TTS Platform"
echo "======================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Change to script directory
cd "$(dirname "$0")"

# Build and start all services
echo "Building and starting CODVOICE services..."
docker-compose up -d --build

echo ""
echo "CODVOICE is starting up..."
echo ""
echo "Services:"
echo "- API Server: http://localhost/api"
echo "- Admin Dashboard: http://localhost"
echo "- TTS Engine: Internal (codvoice-tts:8000)"
echo ""
echo "Default API Key: codvoice-default-key-123"
echo "Admin API Key: codvoice-admin-key-456"
echo ""
echo "Example API Usage:"
echo "curl -X POST http://localhost/api/tts \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -H 'Authorization: Bearer codvoice-default-key-123' \\"
echo "  -d '{\"text\": \"Hello world\", \"voice\": \"en_US-lessac-medium\"}' \\"
echo "  --output speech.wav"
echo ""
echo "Checking service health..."

# Wait for services to be ready
sleep 10

# Check if services are healthy
echo "Checking API health..."
if curl -f http://localhost/api/health > /dev/null 2>&1; then
    echo "✓ API Server is healthy"
else
    echo "✗ API Server is not responding"
fi

echo "Checking Admin Dashboard..."
if curl -f http://localhost > /dev/null 2>&1; then
    echo "✓ Admin Dashboard is accessible"
else
    echo "✗ Admin Dashboard is not responding"
fi

echo ""
echo "CODVOICE is ready!"
echo "Visit http://localhost for the admin dashboard"