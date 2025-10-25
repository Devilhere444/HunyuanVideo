#!/bin/bash
# Start script for N8N Integration Service

# Set default environment variables
export N8N_API_BASE_URL=${N8N_API_BASE_URL:-"http://localhost:10000"}
export N8N_WEBHOOK_PORT=${N8N_WEBHOOK_PORT:-8080}
export N8N_WEBHOOK_HOST=${N8N_WEBHOOK_HOST:-"0.0.0.0"}

echo "========================================"
echo "HunyuanVideo N8N Integration Service"
echo "========================================"
echo "Backend API: $N8N_API_BASE_URL"
echo "Webhook Port: $N8N_WEBHOOK_PORT"
echo "Webhook Host: $N8N_WEBHOOK_HOST"
echo "========================================"

# Check if main API is running
echo "Checking if main API is running..."
if curl -s "$N8N_API_BASE_URL/health" > /dev/null; then
    echo "✓ Main API is running"
else
    echo "⚠ Warning: Main API is not responding at $N8N_API_BASE_URL"
    echo "  Make sure to start the main API server first with: ./start_api.sh"
fi

# Start N8N integration service
echo "Starting N8N Integration Service..."
python n8n_integration.py
