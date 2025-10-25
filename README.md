# HunyuanVideo - Render.com Deployment

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

This repository contains a production-ready deployment of HunyuanVideo for Render.com.

## Quick Deploy to Render.com

### Option 1: One-Click Deploy (Recommended)

1. Click the "Deploy to Render" button above
2. Connect your GitHub account
3. Configure environment variables (or use defaults)
4. Click "Create Web Service"

### Option 2: Manual Deploy

1. Fork this repository to your GitHub account
2. Sign in to [Render.com](https://render.com)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Render will auto-detect the `render.yaml` configuration
6. Review and deploy

## Configuration

The deployment uses:
- **Plan**: Ultra (8 cores, 32GB RAM - ~$450/month)
- **Environment**: Docker (CPU-optimized)
- **Storage**: 100GB persistent disk for model checkpoints

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `10000` | Server port |
| `MODEL_BASE` | `/opt/render/project/src/ckpts` | Model checkpoints directory |
| `SAVE_PATH` | `/opt/render/project/src/results` | Generated videos directory |
| `MAX_WORKERS` | `2` | API worker threads |

## Model Setup

After deployment, you need to download the HunyuanVideo models:

```bash
# Enable SSH in Render dashboard, then SSH into your instance:
pip install huggingface-hub
huggingface-cli download tencent/HunyuanVideo --local-dir /opt/render/project/src/ckpts
```

Or configure automatic download in your environment setup.

## API Usage

Once deployed, access your API at: `https://your-service-name.onrender.com`

### Health Check
```bash
curl https://your-service-name.onrender.com/health
```

### Generate Video
```bash
curl -X POST https://your-service-name.onrender.com/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A cat walking on grass, realistic style",
    "resolution": "720x1280",
    "video_length": 129,
    "seed": -1
  }'
```

### API Documentation

Visit `https://your-service-name.onrender.com/docs` for interactive API documentation (Swagger UI).

## Performance

- **Generation time**: 10-30 minutes per video (CPU)
- **Video length**: Up to 60 seconds at 15 fps
- **Resolution**: 540p to 720p
- **Cost per video**: ~$0.53 (vs $1.50-$3.00 on GPU)

## Files Structure

```
.
├── Dockerfile              # Docker configuration
├── render.yaml            # Render deployment config
├── api_server.py          # FastAPI REST API server
├── start_api.sh          # Startup script
├── healthcheck.py        # Health check endpoint
├── requirements.txt      # Python dependencies
├── requirements-api.txt  # API-specific dependencies
├── hyvideo/             # HunyuanVideo core library
└── ckpts/               # Model checkpoints (mounted from persistent disk)
```

## Support

- **Original HunyuanVideo**: [GitHub](https://github.com/Tencent-Hunyuan/HunyuanVideo)
- **Model Weights**: [HuggingFace](https://huggingface.co/tencent/HunyuanVideo)
- **Render Documentation**: [render.com/docs](https://render.com/docs)

## License

See [LICENSE.txt](LICENSE.txt) for details.
