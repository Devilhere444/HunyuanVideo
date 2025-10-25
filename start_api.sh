#!/bin/bash
# Startup script for HunyuanVideo CPU API server

set -e

echo "========================================="
echo "Starting HunyuanVideo CPU API Server"
echo "========================================="

# Display configuration
echo ""
echo "Configuration:"
echo "  Host: ${HOST:-0.0.0.0}"
echo "  Port: ${PORT:-10000}"
echo "  Model Base: ${MODEL_BASE:-/app/ckpts}"
echo "  Save Path: ${SAVE_PATH:-/app/results}"
echo "  Max Workers: ${MAX_WORKERS:-2}"
echo ""

# Create necessary directories
mkdir -p "${SAVE_PATH:-/app/results}"
mkdir -p "${MODEL_BASE:-/app/ckpts}"

# Check if models exist
MODEL_DIR="${MODEL_BASE:-/app/ckpts}"
if [ ! -d "$MODEL_DIR/hunyuan-video-t2v-720p" ]; then
    echo "⚠ WARNING: Models not found in $MODEL_DIR"
    echo ""
    echo "Please download models using:"
    echo "  pip install huggingface-hub"
    echo "  huggingface-cli download tencent/HunyuanVideo --local-dir $MODEL_DIR"
    echo ""
    echo "The server will start but will not be able to generate videos until models are downloaded."
    echo ""
fi

# Display CPU optimization settings
echo "CPU Optimization Settings:"
echo "  OMP_NUM_THREADS: ${OMP_NUM_THREADS:-8}"
echo "  MKL_NUM_THREADS: ${MKL_NUM_THREADS:-8}"
echo "  TORCH_NUM_THREADS: ${TORCH_NUM_THREADS:-8}"
echo ""

# Start the API server
echo "Starting API server..."
echo "========================================="
exec python api_server.py
