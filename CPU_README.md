# HunyuanVideo - CPU-Optimized Setup

## Overview

This is a CPU-optimized version of HunyuanVideo designed to run on systems with 8 CPU cores and 32GB RAM, without requiring GPU acceleration. This setup is ideal for cloud deployments, CI/CD pipelines, and development environments without GPU access.

## Key Features

- ✅ **CPU-Only Operation**: No GPU required
- ✅ **Portrait & Landscape Support**: 9:16 and 16:9 aspect ratios
- ✅ **60+ Second Videos**: Generate up to ~60 seconds of video (129 frames at 24fps)
- ✅ **N8N Integration**: Ready-to-use webhook endpoints for automation
- ✅ **REST API**: FastAPI-based REST API for easy integration
- ✅ **Optimized Performance**: Tuned for 8-core CPUs with 32GB RAM

## System Requirements

### Minimum Requirements
- **CPU**: 8 cores (Intel or AMD)
- **RAM**: 32GB
- **Storage**: 50GB+ free space for models and outputs
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.8+

### Recommended Configuration
- **CPU**: 16 cores
- **RAM**: 64GB
- **Storage**: 100GB+ SSD
- **OS**: Ubuntu 22.04 LTS

## Quick Start

### 1. Install Dependencies

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv ffmpeg

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install CPU-optimized PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install application dependencies
pip install -r requirements-api.txt
```

### 2. Download Models

Download the HunyuanVideo models to the `ckpts` directory:

```bash
# Create models directory
mkdir -p ckpts

# Download models (follow official instructions)
# Model files should be placed in:
# ckpts/hunyuan-video-t2v-720p/transformers/
# ckpts/text_encoder/
# ckpts/text_encoder_2/
# ckpts/vae/
```

### 3. Start API Server

```bash
# Start the main API server
./start_api.sh
```

The API server will start on `http://localhost:10000`

### 4. (Optional) Start N8N Integration Service

```bash
# Start the N8N integration service
./start_n8n.sh
```

The N8N service will start on `http://localhost:8080`

## Usage

### Using the API Directly

```bash
# Generate a portrait video (60 seconds)
curl -X POST http://localhost:10000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A cat walks on the grass, realistic style",
    "preset": "portrait_60s"
  }'
```

### Using the Python Client

```bash
python example_client.py \
  --url http://localhost:10000 \
  --prompt "A cat walks on the grass, realistic style" \
  --output generated_video.mp4
```

### Using N8N Integration

See [N8N_INTEGRATION.md](N8N_INTEGRATION.md) for detailed N8N workflow setup.

## Available Presets

| Preset | Resolution | Aspect Ratio | Duration | Use Case |
|--------|-----------|--------------|----------|----------|
| `portrait_60s` | 544x960 | 9:16 | ~60s | TikTok, Instagram Reels |
| `portrait_30s` | 544x960 | 9:16 | ~30s | Quick social media |
| `landscape_60s` | 960x544 | 16:9 | ~60s | YouTube, TV |
| `landscape_30s` | 960x544 | 16:9 | ~30s | Quick landscape |

## Performance

### Expected Generation Times (8-core CPU, 32GB RAM)

| Configuration | Time |
|--------------|------|
| Portrait 60s (30 steps) | 15-25 minutes |
| Portrait 30s (30 steps) | 8-15 minutes |
| Landscape 60s (30 steps) | 15-25 minutes |
| Landscape 30s (30 steps) | 8-15 minutes |
| Portrait 60s (40 steps) | 20-35 minutes |

### Quality vs Speed

- **10-20 steps**: Fast, lower quality (testing only)
- **30 steps**: Good quality (recommended)
- **40 steps**: High quality
- **50 steps**: Best quality (slower)

## API Endpoints

### Main API (Port 10000)

- `POST /api/generate` - Submit video generation job
- `GET /api/status/{job_id}` - Check job status
- `GET /api/videos/{filename}` - Download video
- `GET /api/jobs` - List all jobs
- `DELETE /api/jobs/{job_id}` - Delete job
- `GET /api/info` - Get API information
- `GET /health` - Health check

### N8N Integration (Port 8080)

- `POST /webhook/generate` - Submit via webhook
- `GET /webhook/status/{job_id}` - Check status via webhook
- `GET /webhook/download/{job_id}` - Download via webhook
- `GET /webhook/info` - Get preset information
- `POST /webhook/test` - Test webhook connection

## Configuration

### Environment Variables

```bash
# Main API Server
export MODEL_BASE="/path/to/ckpts"
export SAVE_PATH="/path/to/results"
export MAX_WORKERS=2
export PORT=10000
export HOST=0.0.0.0

# N8N Integration Service
export N8N_API_BASE_URL="http://localhost:10000"
export N8N_WEBHOOK_PORT=8080
export N8N_WEBHOOK_HOST="0.0.0.0"
```

### CPU Optimization Tips

1. **Set OMP Threads**: `export OMP_NUM_THREADS=8`
2. **Use CPU Offloading**: Enabled by default with `--use-cpu-offload`
3. **Batch Size**: Keep at 1 for CPU
4. **Precision**: Use fp32 (default for CPU)
5. **Memory**: Close other applications to free RAM

## Troubleshooting

### Out of Memory

**Symptom**: Process killed or OOM errors

**Solutions**:
- Reduce video_length (fewer frames)
- Enable CPU offloading (already default)
- Close other applications
- Increase swap space

### Slow Generation

**Symptom**: Takes longer than expected

**Solutions**:
- This is normal for CPU (15-25 minutes)
- Reduce num_inference_steps (trade-off with quality)
- Use shorter video_length
- Ensure no other CPU-intensive processes

### Model Not Loading

**Symptom**: "Model not initialized" error

**Solutions**:
- Check model files exist in `ckpts/` directory
- Verify file permissions
- Check available disk space
- Review server logs

### API Connection Errors

**Symptom**: Cannot connect to API

**Solutions**:
- Verify server is running: `curl http://localhost:10000/health`
- Check firewall settings
- Verify PORT environment variable
- Review server logs

## File Structure

```
HunyuanVideo/
├── api_server.py           # Main FastAPI server
├── n8n_integration.py      # N8N webhook integration
├── example_client.py       # Example Python client
├── sample_video.py         # CLI video generation
├── start_api.sh           # Start API server
├── start_n8n.sh           # Start N8N service
├── requirements.txt        # Core dependencies
├── requirements-api.txt    # API dependencies
├── N8N_INTEGRATION.md     # N8N integration guide
├── hyvideo/               # Core library
│   ├── inference.py       # CPU-optimized inference
│   ├── config.py          # Configuration
│   └── ...
└── ckpts/                 # Model checkpoints
    └── hunyuan-video-t2v-720p/
```

## Differences from GPU Version

### Removed Components

- ❌ GPU/CUDA dependencies
- ❌ Multi-GPU support (xfuser)
- ❌ FP8/FP16 precision (CPU uses FP32)
- ❌ Distributed training code
- ❌ Gradio UI (optional, removed to simplify)

### CPU Optimizations

- ✅ CPU-only inference path
- ✅ Sequential CPU offloading
- ✅ FP32 precision
- ✅ Simplified memory management
- ✅ Optimized batch processing

## Known Limitations

1. **Speed**: CPU generation is slower than GPU (15-25 min vs 2-5 min)
2. **Max Frames**: Limited to 129 frames (~60s at 24fps) for memory constraints
3. **Batch Size**: Only batch_size=1 supported on CPU
4. **Parallel Processing**: No multi-GPU or distributed support

## Best Practices

1. **Use Presets**: Start with presets for reliable results
2. **Monitor Memory**: Watch RAM usage during generation
3. **Queue Jobs**: Process one video at a time
4. **Storage**: Download and backup videos promptly
5. **Cleanup**: Delete old jobs to free disk space

## Production Deployment

### Docker Deployment

Use the CPU-optimized Dockerfile:

```bash
docker build -f Dockerfile.cpu -t hunyuanvideo-cpu .
docker run -p 10000:10000 -v ./ckpts:/app/ckpts hunyuanvideo-cpu
```

### Cloud Deployment

See [CPU_DEPLOYMENT_GUIDE.md](CPU_DEPLOYMENT_GUIDE.md) for cloud deployment instructions (Render.com, AWS, GCP, Azure).

### Load Balancing

For high volume, deploy multiple instances behind a load balancer:

```
Load Balancer
├── Instance 1 (API Server)
├── Instance 2 (API Server)
└── Instance 3 (API Server)
```

## Documentation

- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Complete API reference
- [N8N_INTEGRATION.md](N8N_INTEGRATION.md) - N8N workflow integration
- [CPU_DEPLOYMENT_GUIDE.md](CPU_DEPLOYMENT_GUIDE.md) - Cloud deployment guide

## Support

For issues, questions, or contributions:

1. Check the troubleshooting section above
2. Review the documentation
3. Check server logs
4. Test with `example_client.py`
5. Verify with `/health` endpoint

## License

See [LICENSE.txt](LICENSE.txt) for license information.

## Acknowledgments

Based on HunyuanVideo by Tencent, optimized for CPU-only operation.
