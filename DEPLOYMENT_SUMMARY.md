# Render.com Deployment - Summary

This document summarizes the deployment configuration added to the HunyuanVideo repository.

## Files Created

### Core Deployment Files

1. **`render.yaml`** - Render.com Blueprint configuration
   - Defines web service configuration
   - Sets environment variables
   - Configures persistent disk for model storage
   - Specifies Docker environment

2. **`Dockerfile`** - Docker container configuration
   - Based on NVIDIA CUDA 12.4 with cuDNN
   - Installs Python 3.10 and dependencies
   - Includes PyTorch with CUDA support
   - Optionally installs flash-attention and xfuser
   - Exposes port 10000 for Gradio
   - Includes health check

3. **`start.sh`** - Startup script
   - Creates necessary directories
   - Checks for model availability
   - Sets default environment variables
   - Starts Gradio server with appropriate flags

4. **`docker-compose.yml`** - Local testing configuration
   - Enables local Docker-based testing
   - Mounts local directories for models and results
   - Configures GPU access via NVIDIA runtime

### Documentation Files

5. **`DEPLOYMENT.md`** - Comprehensive deployment guide
   - Prerequisites and requirements
   - Step-by-step deployment instructions
   - Configuration details
   - Model setup guide
   - Usage examples (web and API)
   - Troubleshooting guide
   - Cost considerations
   - Performance optimization tips

6. **`QUICKSTART.md`** - Quick start guide
   - 5-minute deployment checklist
   - Simplified deployment steps
   - Input format examples
   - Example prompts
   - Common troubleshooting

7. **`.env.example`** - Environment variable template
   - Shows all configurable environment variables
   - Includes defaults and descriptions

### Supporting Files

8. **`healthcheck.py`** - Health check script
   - Verifies Gradio server is running
   - Can be used by monitoring services
   - Returns appropriate exit codes

9. **Updated `.gitignore`**
   - Excludes results, outputs, and model files
   - Prevents committing large files

10. **Updated `README.md`**
    - Added deployment section
    - Links to deployment guides
    - Updated table of contents

11. **Updated `requirements.txt`**
    - Added `requests` for health check script

## Deployment Options

### Option 1: Blueprint Deployment (Recommended)
1. Push repository to GitHub
2. In Render Dashboard: New → Blueprint
3. Select repository (render.yaml auto-detected)
4. Review and deploy

### Option 2: Manual Deployment
1. Push repository to GitHub
2. In Render Dashboard: New → Web Service
3. Select repository and configure manually
4. Set environment variables
5. Add persistent disk
6. Deploy

### Option 3: Local Testing (Docker Compose)
```bash
docker-compose up --build
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_NAME` | `0.0.0.0` | Server bind address |
| `SERVER_PORT` | `10000` | Server port |
| `MODEL_BASE` | `/app/ckpts` | Model checkpoint directory |
| `SAVE_PATH` | `/app/results` | Generated videos directory |
| `GRADIO_ANALYTICS_ENABLED` | `False` | Disable analytics |

## Model Setup Required

**Critical**: Models must be downloaded separately (40GB+)

Methods:
1. Download locally, then upload to cloud storage
2. Download via SSH after deployment
3. Download during startup (slow)

Download command:
```bash
huggingface-cli download tencent/HunyuanVideo --local-dir ./ckpts
```

## Key Features

✅ **One-click deployment** via render.yaml blueprint
✅ **GPU optimized** Docker image with CUDA 12.4
✅ **Persistent storage** configuration for models
✅ **Environment-based** configuration (no code changes needed)
✅ **Health checks** for monitoring
✅ **Local testing** support via Docker Compose
✅ **Comprehensive documentation** with examples
✅ **Cost optimization** tips included

## Input Format

### Web UI
1. Navigate to deployed URL
2. Enter prompt: "A cat walks on the grass, realistic style."
3. Select resolution and settings
4. Click Generate
5. Wait 5-10 minutes
6. Download video

### API
```python
from gradio_client import Client

client = Client("https://your-service.onrender.com")
result = client.predict(
    prompt="A cat walks on the grass, realistic style.",
    resolution="1280x720",
    video_length=129,
    seed=-1,
    num_inference_steps=50,
    guidance_scale=1.0,
    flow_shift=7.0,
    embedded_guidance_scale=6.0,
    api_name="/predict"
)
```

## System Requirements

- **GPU**: 45-60GB VRAM (NVIDIA with CUDA support)
- **Storage**: 100GB+ for models
- **Memory**: 32GB+ RAM
- **OS**: Linux (Ubuntu 22.04 recommended)

## Cost Estimates

**GPU Instance** (24/7): ~$1,000-$2,000/month
**Persistent Disk** (100GB): ~$25/month
**Total**: ~$1,025-$2,025/month

### Cost Optimization
- Use auto-scaling
- Implement rate limiting
- Scale down during low usage
- Consider spot instances

## Troubleshooting

### Models Not Found
- Check MODEL_BASE env variable
- Verify persistent disk is mounted
- Download models to correct location

### Out of Memory
- Use smaller resolution (544x960)
- Reduce inference steps
- Ensure CPU offload is enabled
- Upgrade GPU instance

### Slow Generation
- Lower resolution
- Reduce inference steps
- Check GPU utilization
- Use FP8 weights if available

## Next Steps

1. **Review** DEPLOYMENT.md for detailed instructions
2. **Check** QUICKSTART.md for quick deployment
3. **Test locally** with Docker Compose (optional)
4. **Deploy** to Render.com
5. **Download** models to persistent storage
6. **Configure** monitoring and alerts
7. **Add** authentication if needed
8. **Implement** rate limiting

## Important Notes

⚠️ **GPU Required**: This application requires substantial GPU resources

⚠️ **High Cost**: GPU instances are expensive - review pricing carefully

⚠️ **Large Models**: 40GB+ download required before use

⚠️ **Generation Time**: 5-15 minutes per video

⚠️ **Resource Intensive**: Not suitable for high-traffic deployments without optimization

## Support

- **Documentation**: See DEPLOYMENT.md and QUICKSTART.md
- **This Fork**: https://github.com/Devilhere444/HunyuanVideo
- **Original Repository**: https://github.com/Tencent-Hunyuan/HunyuanVideo
- **Render Documentation**: https://render.com/docs
- **Model Hub**: https://huggingface.co/tencent/HunyuanVideo

## Files Structure

```
HunyuanVideo/
├── .env.example              # Environment variable template
├── .gitignore               # Updated with deployment artifacts
├── DEPLOYMENT.md            # Comprehensive deployment guide
├── QUICKSTART.md            # Quick start guide
├── Dockerfile               # Docker container configuration
├── docker-compose.yml       # Local testing with Docker
├── render.yaml              # Render.com blueprint
├── start.sh                 # Startup script
├── healthcheck.py           # Health check endpoint
├── README.md                # Updated with deployment section
├── requirements.txt         # Updated with requests
├── gradio_server.py         # Gradio web interface (existing)
└── ...                      # Other project files
```

---

**Created for**: Render.com deployment
**Repository**: Devilhere444/HunyuanVideo
**Purpose**: Enable easy cloud deployment of HunyuanVideo text-to-video model
