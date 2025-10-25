#!/bin/bash
# Installation script for HunyuanVideo CPU-Optimized Setup

set -e  # Exit on error

echo "========================================"
echo "HunyuanVideo CPU-Optimized Installation"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python version: $PYTHON_VERSION"

# Check if Python 3.8+
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "✗ Error: Python 3.8 or higher required. Found: $PYTHON_VERSION"
    exit 1
fi
echo "✓ Python version OK"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "  Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
echo "✓ pip upgraded"
echo ""

# Install CPU-optimized PyTorch
echo "Installing CPU-optimized PyTorch..."
echo "  This may take a few minutes..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
echo "✓ PyTorch installed"
echo ""

# Install application dependencies
echo "Installing application dependencies..."
pip install -r requirements-api.txt
echo "✓ Application dependencies installed"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p ckpts
mkdir -p results
echo "✓ Directories created"
echo ""

# Run setup test
echo "Running setup validation test..."
python test_cpu_setup.py
TEST_RESULT=$?

echo ""
echo "========================================"
echo "Installation Summary"
echo "========================================"

if [ $TEST_RESULT -eq 0 ]; then
    echo "✓ Installation completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Download models to ckpts/ directory"
    echo "   Follow instructions at:"
    echo "   https://github.com/Tencent-Hunyuan/HunyuanVideo"
    echo ""
    echo "2. Start the API server:"
    echo "   ./start_api.sh"
    echo ""
    echo "3. (Optional) Start N8N integration service:"
    echo "   ./start_n8n.sh"
    echo ""
    echo "4. Generate your first video:"
    echo "   python example_client.py \\"
    echo "     --prompt \"A cat walks on the grass\" \\"
    echo "     --output my_video.mp4"
    echo ""
else
    echo "⚠ Installation completed with warnings"
    echo "   Some tests failed. Please review the output above."
    echo ""
fi

echo "========================================"
echo ""
echo "Documentation:"
echo "  - CPU_README.md - Complete setup guide"
echo "  - N8N_INTEGRATION.md - N8N workflow guide"
echo "  - API_DOCUMENTATION.md - API reference"
echo ""
echo "========================================"
