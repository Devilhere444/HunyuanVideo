# CPU Deployment Guide for Render.com

## Overview

This guide helps you deploy HunyuanVideo as a REST API on Render.com's **Ultra plan** (8 cores, 32GB RAM, $450/month) without GPU/VRAM.

## Important Notes

⚠️ **CPU Limitations**: Video generation on CPU is significantly slower than GPU (10-30 minutes per video vs 1-5 minutes on GPU).

✅ **Cost Effective**: The Ultra plan ($450/month) is much cheaper than GPU plans which can cost $1000-2000/month.

✅ **Works Well For**: Background processing, batch jobs, low-traffic applications, prototyping.

## Prerequisites

- Render.com account
- GitHub account
- Basic understanding of REST APIs
- Model checkpoints (~40GB) - see download instructions below

## Deployment Steps

### Step 1: Fork/Clone Repository

1. Fork this repository to your GitHub account
2. Clone it locally:
```bash
git clone https://github.com/YOUR_USERNAME/HunyuanVideo.git
cd HunyuanVideo
```

### Step 2: Prepare Model Checkpoints

**Option A: Download Locally Then Upload** (Recommended)

```bash
# Install Hugging Face CLI
pip install huggingface-hub

# Download models (this will take time - models are ~40GB)
huggingface-cli download tencent/HunyuanVideo --local-dir ./ckpts
```

Then upload to a cloud storage service (S3, Google Cloud Storage, etc.) for deployment.

**Option B: Download After Deployment via SSH**

1. Deploy the service first (will be in unhealthy state)
2. Enable SSH in Render dashboard
3. SSH into the instance:
   ```bash
   render ssh hunyuan-video-api
   ```
4. Download models:
   ```bash
   cd /opt/render/project/src/ckpts
   pip install huggingface-hub
   huggingface-cli download tencent/HunyuanVideo --local-dir .
   ```
5. Restart the service

### Step 3: Deploy on Render.com

#### Method A: Using Blueprint (Easiest)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Select the repository
5. Render will detect `render-cpu.yaml`
6. Review the configuration:
   - **Plan**: Ultra (8 cores, 32GB RAM)
   - **Disk**: 100GB persistent storage
   - **Environment**: Docker
7. Click **"Apply"**

#### Method B: Manual Setup

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `hunyuan-video-api`
   - **Environment**: Docker
   - **Plan**: Ultra
   - **Dockerfile Path**: `./Dockerfile.cpu`
   - **Docker Build Context**: `.`

5. Add Environment Variables:
   ```
   HOST=0.0.0.0
   PORT=10000
   MODEL_BASE=/opt/render/project/src/ckpts
   SAVE_PATH=/opt/render/project/src/results
   MAX_WORKERS=2
   PYTHONUNBUFFERED=1
   OMP_NUM_THREADS=8
   MKL_NUM_THREADS=8
   TORCH_NUM_THREADS=8
   CUDA_VISIBLE_DEVICES=
   ```

6. Add Persistent Disk:
   - **Name**: `model-storage`
   - **Mount Path**: `/opt/render/project/src/ckpts`
   - **Size**: 100GB

7. Click **"Create Web Service"**

### Step 4: Wait for Deployment

Initial deployment takes 10-20 minutes:
- Docker image build: 5-10 minutes
- Service startup: 2-5 minutes
- Model loading: 3-5 minutes

Monitor progress in the Render logs.

### Step 5: Verify Deployment

Check the health endpoint:
```bash
curl https://your-service-name.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "active_jobs": 0,
  "total_jobs": 0
}
```

If `model_loaded` is `false`, the service is still loading models.

### Step 6: Test Video Generation

Generate your first video:

```bash
curl -X POST "https://your-service-name.onrender.com/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A cat walks on the grass, realistic style.",
    "width": 640,
    "height": 480,
    "video_length": 61,
    "fps": 15,
    "num_inference_steps": 30
  }'
```

Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Video generation job submitted successfully",
  "check_status_url": "/api/status/550e8400-e29b-41d4-a716-446655440000"
}
```

Check status:
```bash
curl "https://your-service-name.onrender.com/api/status/550e8400-e29b-41d4-a716-446655440000"
```

Wait 10-20 minutes, then download:
```bash
curl -O "https://your-service-name.onrender.com/api/videos/550e8400-e29b-41d4-a716-446655440000.mp4"
```

## Configuration for 60-Second Videos at 15 FPS

### Recommended Settings

For 60-second videos at 15 fps (approximately 900 frames), we need to use a reduced frame count compatible with the model:

```json
{
  "prompt": "Your video description here",
  "width": 640,
  "height": 480,
  "video_length": 61,
  "fps": 15,
  "num_inference_steps": 30
}
```

**Note**: The model supports up to 129 frames. For a 60-second video, you can:
- Use 61 frames and stretch to 60 seconds (lower quality but faster)
- Use 129 frames for higher quality (covers ~8.6 seconds at 15fps, or full 60s at lower fps)
- Generate multiple segments and stitch them together

### Frame Calculation

| Duration | FPS | Total Frames | Model Frames | Strategy |
|----------|-----|--------------|--------------|----------|
| 60 sec | 15 | 900 | 61 | Generate + stretch/interpolate |
| 60 sec | 8 | 480 | 129 | Generate multiple 8.6s segments |
| 60 sec | 5 | 300 | 129 | Generate multiple 25.8s segments |
| 8.6 sec | 15 | 129 | 129 | Direct generation (recommended) |

### Multi-Segment Generation (For Full 60 Seconds)

To generate a full 60-second video at 15 fps:

1. Generate 7-8 segments of ~8 seconds each (129 frames at 15fps = 8.6 sec)
2. Use video editing software to stitch segments
3. Apply transitions between segments

**Python Example:**
```python
import requests
import time

BASE_URL = "https://your-service-name.onrender.com"

# Generate 7 segments for 60 seconds
segments = []
base_prompt = "A cat walks on the grass, realistic style"

for i in range(7):
    # Vary prompts slightly for continuity
    prompt = f"{base_prompt}, part {i+1} of 7"
    
    # Submit job
    response = requests.post(
        f"{BASE_URL}/api/generate",
        json={
            "prompt": prompt,
            "width": 640,
            "height": 480,
            "video_length": 129,
            "fps": 15,
            "num_inference_steps": 30,
            "seed": 42 + i  # Consistent seed for continuity
        }
    )
    
    job_id = response.json()["job_id"]
    segments.append(job_id)
    print(f"Segment {i+1} submitted: {job_id}")

# Wait for all segments (this will take a while)
# Then download and stitch using ffmpeg or video editing software
```

## CPU Optimization Tips

### 1. Reduce Resolution

Lower resolutions generate much faster:
- 480x360: ~8-12 minutes
- 640x480: ~12-18 minutes
- 720x480: ~18-25 minutes

### 2. Fewer Inference Steps

Reduce steps for faster generation:
- 20 steps: Fast but lower quality
- 30 steps: Recommended balance
- 40 steps: Higher quality but slower

### 3. Adjust MAX_WORKERS

In `render-cpu.yaml`, you can adjust concurrent jobs:
- 1 worker: Slower but more stable
- 2 workers: Recommended for Ultra plan
- 3+ workers: May cause memory issues

### 4. Use Queue System

Process videos in batches during off-peak hours to maximize throughput.

## Getting Video Links

### Method 1: Polling

```python
import requests
import time

job_id = "your-job-id"
BASE_URL = "https://your-service-name.onrender.com"

while True:
    response = requests.get(f"{BASE_URL}/api/status/{job_id}")
    status = response.json()
    
    if status["status"] == "completed":
        video_url = f"{BASE_URL}{status['video_url']}"
        print(f"Video URL: {video_url}")
        break
    
    time.sleep(10)
```

### Method 2: Webhook (Future Enhancement)

You can extend the API to support webhooks by adding a callback URL parameter.

### Method 3: List All Jobs

```bash
curl "https://your-service-name.onrender.com/api/jobs?status=completed"
```

## Performance Benchmarks (CPU)

### Ultra Plan (8 cores, 32GB RAM)

| Resolution | Frames | Steps | Time (est) | Quality |
|------------|--------|-------|------------|---------|
| 480x360 | 61 | 25 | 8-12 min | Good |
| 640x480 | 61 | 30 | 12-18 min | Better |
| 720x480 | 61 | 35 | 18-25 min | Best |
| 640x480 | 129 | 30 | 20-30 min | Better (longer) |
| 960x544 | 129 | 40 | 35-50 min | Maximum |

**Note**: These are estimates. Actual times may vary.

## Cost Analysis

### Monthly Costs (24/7 Operation)

- **Ultra Plan**: $450/month (8 cores, 32GB RAM)
- **Persistent Disk** (100GB): ~$25/month
- **Total**: ~$475/month

### Cost Per Video (Approximate)

Assuming 30 generations per day:
- Monthly cost: $475
- Videos per month: ~900
- Cost per video: ~$0.53

Compare to GPU plans: ~$1.50-$3.00 per video

### Cost Optimization

1. **Auto-scaling**: Scale down during low usage
2. **Scheduled jobs**: Process during specific hours
3. **Smaller plan for testing**: Use Starter plan during development

## Troubleshooting

### Model Not Loading

**Symptom**: `/health` shows `model_loaded: false`

**Solutions**:
1. Check logs in Render dashboard
2. Verify models are in `/opt/render/project/src/ckpts`
3. Check disk is mounted correctly
4. Ensure sufficient disk space (100GB+)

### Out of Memory

**Symptom**: Service crashes or jobs fail

**Solutions**:
1. Reduce resolution to 480x360
2. Set `MAX_WORKERS=1`
3. Enable more aggressive CPU offloading
4. Upgrade to a larger plan (if available)

### Slow Generation

**Symptom**: Videos take longer than expected

**Expected behavior** on CPU. To improve:
1. Reduce resolution
2. Lower inference steps to 25-30
3. Use smaller frame counts (61 instead of 129)
4. Ensure no other heavy processes running

### Jobs Stuck in Queue

**Symptom**: Jobs stay in "queued" status

**Solutions**:
1. Check if another job is processing
2. Restart the service
3. Check logs for errors
4. Verify `MAX_WORKERS` setting

## Monitoring

### Health Check

```bash
curl https://your-service-name.onrender.com/health
```

### List Active Jobs

```bash
curl "https://your-service-name.onrender.com/api/jobs?status=processing"
```

### View Logs

1. Go to Render Dashboard
2. Select your service
3. Click "Logs" tab
4. Monitor real-time logs

## API Usage Examples

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete examples in:
- Python
- JavaScript
- cURL
- And more

## Interactive Documentation

Access Swagger UI at:
```
https://your-service-name.onrender.com/docs
```

## Scaling

### Vertical Scaling

Upgrade to larger CPU plans if available:
- Ultra: 8 cores, 32GB RAM ($450/month)
- Pro Plus: 16 cores, 64GB RAM (if available)

### Horizontal Scaling

Deploy multiple instances:
1. Deploy multiple services
2. Use a load balancer
3. Implement a job distributor

## Security Recommendations

1. **Add Authentication**: Implement API keys or OAuth
2. **Rate Limiting**: Prevent abuse
3. **Input Validation**: Sanitize prompts
4. **HTTPS Only**: Ensure all traffic is encrypted
5. **Monitor Usage**: Track API calls and costs

## Next Steps

1. ✅ Deploy the API
2. ✅ Test video generation
3. 📝 Implement authentication (recommended)
4. 📝 Set up monitoring and alerts
5. 📝 Create a frontend interface
6. 📝 Implement webhook notifications
7. 📝 Add video stitching for longer videos

## Support

- **API Documentation**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **GitHub Issues**: Report bugs and request features
- **Render Support**: [render.com/support](https://render.com/support)

## License

See [LICENSE.txt](LICENSE.txt) for license information.
