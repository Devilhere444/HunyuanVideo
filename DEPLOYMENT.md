# HunyuanVideo Deployment Guide for Render.com

This guide provides step-by-step instructions to deploy HunyuanVideo on Render.com.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Important Notes](#important-notes)
- [Deployment Steps](#deployment-steps)
- [Configuration](#configuration)
- [Model Setup](#model-setup)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying to Render.com, ensure you have:

1. **A Render.com account** with access to GPU-enabled services
2. **GitHub repository** with this code
3. **Sufficient resources**: HunyuanVideo requires:
   - **GPU**: NVIDIA GPU with CUDA support (minimum 45-60GB VRAM)
   - **Storage**: At least 100GB for model checkpoints
   - **Memory**: 32GB+ RAM recommended

## Important Notes

⚠️ **Critical Considerations:**

1. **GPU Requirements**: HunyuanVideo is a large model requiring substantial GPU resources:
   - Minimum: 45GB VRAM for 544x960x129f
   - Recommended: 60GB+ VRAM for 720x1280x129f (720p)
   
2. **Cost**: GPU instances on Render.com are expensive. Ensure you understand the pricing before deployment.

3. **Model Storage**: Model checkpoints are large (~40GB+). You'll need:
   - Persistent disk storage on Render.com
   - Or external storage solution (S3, Google Cloud Storage, etc.)

4. **Cold Start Time**: First deployment will be slow due to:
   - Docker image build time
   - Model download/initialization
   - CUDA library setup

## Deployment Steps

### Option 1: Deploy via Render Dashboard (Recommended)

1. **Fork/Clone this repository** to your GitHub account

2. **Sign in to Render.com** and click "New +" → "Web Service"

3. **Connect your GitHub repository**

4. **Configure the service:**
   - **Name**: `hunyuan-video` (or your preferred name)
   - **Environment**: Docker
   - **Region**: Choose a region with GPU support
   - **Instance Type**: Select a GPU instance with at least 60GB VRAM
   - **Dockerfile Path**: `./Dockerfile`

5. **Add Environment Variables:**
   ```
   SERVER_NAME=0.0.0.0
   SERVER_PORT=10000
   MODEL_BASE=/opt/render/project/src/ckpts
   SAVE_PATH=/opt/render/project/src/results
   GRADIO_ANALYTICS_ENABLED=False
   PYTHONUNBUFFERED=1
   ```

6. **Add Persistent Disk:**
   - Name: `model-storage`
   - Mount Path: `/opt/render/project/src/ckpts`
   - Size: 100GB (adjust based on your needs)

7. **Deploy**: Click "Create Web Service"

### Option 2: Deploy via render.yaml (Infrastructure as Code)

1. **Push this repository** to GitHub (with the included `render.yaml`)

2. **In Render Dashboard**, click "New +" → "Blueprint"

3. **Connect your repository** and select the repository

4. **Render will auto-detect** the `render.yaml` file

5. **Review and approve** the configuration

6. **Deploy** the service

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_NAME` | `0.0.0.0` | Server bind address |
| `SERVER_PORT` | `10000` | Server port (Render uses 10000) |
| `MODEL_BASE` | `/app/ckpts` | Directory containing model checkpoints |
| `SAVE_PATH` | `/app/results` | Directory for generated videos |
| `GRADIO_ANALYTICS_ENABLED` | `False` | Disable Gradio analytics |

### Render.yaml Configuration

The `render.yaml` file includes:
- Web service configuration
- Environment variables
- Persistent disk for model storage
- Docker environment setup

You can customize the plan type, disk size, and other settings in `render.yaml`.

## Model Setup

### Downloading Model Checkpoints

HunyuanVideo requires pre-trained model checkpoints. You have several options:

#### Option 1: Download Models Before Deployment

1. **Download locally** using Hugging Face CLI:
   ```bash
   pip install huggingface-hub
   huggingface-cli download tencent/HunyuanVideo --local-dir ./ckpts
   ```

2. **Upload to cloud storage** (S3, Google Cloud Storage, etc.)

3. **Configure your deployment** to download from cloud storage on startup

#### Option 2: Download During First Deploy (Not Recommended)

⚠️ This will significantly increase cold start time (hours).

Add to your startup script:
```bash
huggingface-cli download tencent/HunyuanVideo --local-dir /opt/render/project/src/ckpts
```

#### Option 3: Use Render SSH (After Deployment)

1. **Deploy the service** first
2. **Enable SSH** in Render dashboard
3. **SSH into the instance** and download models:
   ```bash
   cd /opt/render/project/src/ckpts
   pip install huggingface-hub
   huggingface-cli download tencent/HunyuanVideo --local-dir .
   ```

### Required Model Structure

Your `ckpts` directory should have this structure:
```
ckpts/
├── hunyuan-video-t2v-720p/
│   ├── transformers/
│   │   └── mp_rank_00_model_states.pt
│   ├── vae/
│   └── text_encoder/
└── ...
```

See the [official documentation](https://github.com/Tencent-Hunyuan/HunyuanVideo/blob/main/ckpts/README.md) for detailed model download instructions.

## Usage

### Accessing the Application

Once deployed, your application will be available at:
```
https://your-service-name.onrender.com
```

### Input Parameters

The Gradio interface accepts:

1. **Prompt**: Text description of the video you want to generate
   - Example: "A cat walks on the grass, realistic style."

2. **Resolution**: Choose from predefined resolutions
   - 720p options: 1280x720, 720x1280, 1104x832, 832x1104, 960x960
   - 540p options: 960x544, 544x960, 832x624, 624x832, 720x720

3. **Video Length**: 
   - 2s (65 frames)
   - 5s (129 frames) - recommended

4. **Number of Inference Steps**: 1-100 (default: 50)
   - Higher = better quality but slower

5. **Advanced Options**:
   - **Seed**: Random seed for reproducibility (-1 for random)
   - **Guidance Scale**: CFG scale (default: 1.0)
   - **Flow Shift**: Flow matching shift factor (default: 7.0)
   - **Embedded Guidance Scale**: Embedded CFG scale (default: 6.0)

### API Usage

You can also interact with the deployment programmatically using Gradio's API:

```python
from gradio_client import Client

client = Client("https://your-service-name.onrender.com")
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
print(result)
```

## Troubleshooting

### Common Issues

#### 1. "Model not found" Error

**Problem**: Model checkpoints are not available in the `ckpts` directory.

**Solution**:
- Ensure models are downloaded to the persistent disk
- Check the `MODEL_BASE` environment variable
- Verify the model directory structure

#### 2. Out of Memory (OOM) Error

**Problem**: GPU runs out of memory during inference.

**Solutions**:
- Use a smaller resolution (544x960 instead of 720x1280)
- Reduce the number of inference steps
- Ensure `--use-cpu-offload` flag is enabled
- Upgrade to a larger GPU instance

#### 3. Slow Generation Speed

**Problem**: Video generation takes too long.

**Solutions**:
- Reduce inference steps (try 30-40 instead of 50)
- Use lower resolution
- Ensure you're using a GPU instance (not CPU)
- Check GPU utilization

#### 4. Application Won't Start

**Problem**: Service fails to start or crashes on startup.

**Solutions**:
- Check Render logs for error messages
- Verify all environment variables are set correctly
- Ensure persistent disk is mounted properly
- Check if CUDA/GPU drivers are available

#### 5. Docker Build Fails

**Problem**: Docker image build fails during deployment.

**Solutions**:
- Check if flash-attention installation is causing issues (it's optional)
- Review Dockerfile and comment out problematic dependencies
- Ensure base image is compatible with Render's GPU instances

### Checking Logs

View logs in Render Dashboard:
1. Go to your service
2. Click on "Logs" tab
3. Look for errors or warnings

### Health Checks

The Dockerfile includes a health check that pings the service every 30 seconds. If the service is unhealthy, Render will attempt to restart it.

## Performance Optimization

### Reduce Cold Start Time

1. **Pre-build Docker images**: Use Render's image caching
2. **Minimize dependencies**: Only install required packages
3. **Use persistent disk**: Keep models on persistent storage

### Improve Generation Speed

1. **Use FP8 weights**: Download FP8 quantized models (saves ~10GB memory)
   ```bash
   # Add to gradio_server.py command:
   python gradio_server.py --flow-reverse --use-cpu-offload --use-fp8
   ```

2. **Parallel inference**: If using multiple GPUs (requires code changes)
   ```bash
   torchrun --nproc_per_node=2 gradio_server.py --ulysses-degree 2
   ```

3. **Lower default settings**: Modify default parameters in UI for faster generation

## Cost Considerations

### Estimated Costs

Render.com GPU pricing varies by region and GPU type. As of 2024:
- GPU instances: $0.50 - $3.00+ per hour
- Persistent disk: ~$0.25/GB/month

**Example monthly cost for 24/7 deployment:**
- GPU instance (mid-tier): ~$1,000-$2,000/month
- Persistent disk (100GB): ~$25/month
- **Total**: ~$1,025-$2,025/month

### Cost Optimization Tips

1. **Use auto-scaling**: Configure to scale down during low usage
2. **Implement rate limiting**: Prevent abuse and excessive usage
3. **Use lower-tier GPU**: If acceptable quality/speed trade-off
4. **Consider spot instances**: If available on Render

## Support and Resources

- **HunyuanVideo GitHub**: https://github.com/Tencent-Hunyuan/HunyuanVideo
- **Render Documentation**: https://render.com/docs
- **Model Weights**: https://huggingface.co/tencent/HunyuanVideo
- **Issues**: Report issues on the GitHub repository

## License

This deployment guide is provided as-is. HunyuanVideo has its own license. Please review the [LICENSE](LICENSE.txt) file in the repository.
