#!/bin/bash
set -e

echo "Starting HunyuanVideo deployment setup..."

# Create necessary directories
mkdir -p /app/ckpts /app/results /app/gradio_outputs

# Check if models are already downloaded
MODEL_DIR="${MODEL_BASE:-/app/ckpts}"
if [ ! -d "$MODEL_DIR/hunyuan-video-t2v-720p" ]; then
    echo "Models not found. Please download models manually."
    echo "Visit: https://github.com/Tencent-Hunyuan/HunyuanVideo/blob/main/ckpts/README.md"
    echo ""
    echo "You can download models using:"
    echo "  huggingface-cli download tencent/HunyuanVideo --local-dir $MODEL_DIR"
    echo ""
    echo "Note: Models are large (>40GB) and require significant download time."
    echo "Consider using Render's persistent disk feature to store models."
fi

# Set default values for environment variables
export SERVER_NAME="${SERVER_NAME:-0.0.0.0}"
export SERVER_PORT="${SERVER_PORT:-10000}"
export MODEL_BASE="${MODEL_BASE:-/app/ckpts}"
export SAVE_PATH="${SAVE_PATH:-/app/results}"
export GRADIO_ANALYTICS_ENABLED="${GRADIO_ANALYTICS_ENABLED:-False}"

echo "Configuration:"
echo "  Server: $SERVER_NAME:$SERVER_PORT"
echo "  Model Base: $MODEL_BASE"
echo "  Save Path: $SAVE_PATH"

# Start the application
echo "Starting Gradio server..."
exec python gradio_server.py --flow-reverse --use-cpu-offload
