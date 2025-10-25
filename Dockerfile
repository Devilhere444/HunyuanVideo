# CPU-optimized Dockerfile for HunyuanVideo on Render.com
# Designed for Ultra plan: 8 cores, 32GB RAM, no GPU

FROM python:3.10-slim-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-api.txt requirements.txt ./

# Install CPU-optimized PyTorch
RUN pip install --no-cache-dir torch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0 --index-url https://download.pytorch.org/whl/cpu

# Install other Python dependencies
RUN pip install --no-cache-dir -r requirements-api.txt

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x start_api.sh

# Create necessary directories
RUN mkdir -p /app/ckpts /app/results /app/gradio_outputs

# Set environment variables for CPU optimization
ENV PYTHONUNBUFFERED=1
ENV OMP_NUM_THREADS=8
ENV MKL_NUM_THREADS=8
ENV OPENBLAS_NUM_THREADS=8
ENV VECLIB_MAXIMUM_THREADS=8
ENV NUMEXPR_NUM_THREADS=8
ENV TORCH_NUM_THREADS=8

# Disable CUDA
ENV CUDA_VISIBLE_DEVICES=""

# API configuration
ENV HOST=0.0.0.0
ENV PORT=10000
ENV MODEL_BASE=/app/ckpts
ENV SAVE_PATH=/app/results
ENV MAX_WORKERS=2

# Expose port
EXPOSE 10000

# Health check
# Note: Models are loaded on-demand, so initial health check will show "initializing" status
# The service is healthy if it responds, even before models are loaded
HEALTHCHECK --interval=30s --timeout=10s --start-period=5m --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:10000/health', timeout=5)" || exit 1

# Run the API server
CMD ["./start_api.sh"]
