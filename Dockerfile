# Use NVIDIA CUDA base image
FROM nvidia/cuda:12.4.0-cudnn-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir torch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0 --index-url https://download.pytorch.org/whl/cu124
RUN pip install --no-cache-dir -r requirements.txt

# Install flash attention (optional, comment out if build fails)
RUN pip install --no-cache-dir ninja && \
    pip install --no-cache-dir "flash-attn>=2.6.3" --no-build-isolation || echo "Flash attention installation failed, continuing without it"

# Install xfuser for parallel inference (optional)
RUN pip install --no-cache-dir xfuser==0.4.0 || echo "xfuser installation failed, continuing without it"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/ckpts /app/results /app/gradio_outputs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV GRADIO_ANALYTICS_ENABLED=False
ENV SERVER_NAME=0.0.0.0
ENV SERVER_PORT=10000

# Expose port
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5m --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:10000', timeout=5)" || exit 1

# Run the application
CMD ["python", "gradio_server.py", "--flow-reverse", "--use-cpu-offload"]
