# HunyuanVideo REST API - Quick Reference

## 🚀 What's New

This repository now includes a **REST API** optimized for **CPU-only deployment** on Render.com's Ultra plan (8 cores, 32GB RAM, $450/month).

## 📋 Key Features

- ✅ **REST API**: Full-featured FastAPI server
- ✅ **CPU Optimized**: No GPU required - runs on CPU only
- ✅ **Async Processing**: Background job queue system
- ✅ **Video Storage**: Automatic video storage and retrieval
- ✅ **60-Second Videos**: Supports up to 60-second videos at 15 fps
- ✅ **Interactive Docs**: Built-in Swagger UI documentation
- ✅ **Health Monitoring**: Health check and status endpoints
- ✅ **Cost Effective**: ~$475/month vs $1000-2000/month for GPU

## 🎯 Quick Start

### 1. Deploy on Render.com

```bash
# Fork this repo
# Go to https://dashboard.render.com/
# Click "New +" → "Blueprint"
# Connect your repo
# Render will detect render-cpu.yaml
# Click "Apply"
```

### 2. Access Your API

```
https://your-service-name.onrender.com
```

### 3. Generate Your First Video

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

### 4. Check Status & Download

```bash
# Get job status
curl "https://your-service-name.onrender.com/api/status/YOUR_JOB_ID"

# Download video when ready
curl -O "https://your-service-name.onrender.com/api/videos/YOUR_JOB_ID.mp4"
```

## 📚 Documentation

- **[CPU Deployment Guide](CPU_DEPLOYMENT_GUIDE.md)** - Complete deployment instructions
- **[API Documentation](API_DOCUMENTATION.md)** - Full API reference with examples
- **[Interactive Docs](https://your-service-name.onrender.com/docs)** - Swagger UI (after deployment)

## 🔧 Configuration Files

### For CPU Deployment (Recommended for $450/month plan)

- **Dockerfile**: `Dockerfile.cpu` - CPU-optimized Docker image
- **Render Config**: `render-cpu.yaml` - Render.com blueprint for Ultra plan
- **Requirements**: `requirements-api.txt` - Python dependencies
- **API Server**: `api_server.py` - FastAPI REST API

### For GPU Deployment (Original)

- **Dockerfile**: `Dockerfile` - GPU-enabled Docker image
- **Render Config**: `render.yaml` - Render.com blueprint for GPU plan
- **Requirements**: `requirements.txt` - Python dependencies
- **Gradio Server**: `gradio_server.py` - Gradio UI

## 🎬 Video Generation Specs

### Render.com Ultra Plan (CPU-Only)

**Hardware:**
- 8 CPU cores
- 32GB RAM
- No GPU/VRAM
- 100GB persistent disk

**Performance:**
- Resolution: 480x360 to 960x544
- Duration: Up to 8.6 seconds (129 frames at 15fps)
- Generation time: 8-30 minutes per video
- Quality: Good to Excellent

**For 60-Second Videos:**
- Generate multiple 8.6-second segments
- Stitch together using video editing software
- Or use frame interpolation for shorter clips

**Recommended Settings:**
```json
{
  "width": 640,
  "height": 480,
  "video_length": 61,
  "fps": 15,
  "num_inference_steps": 30
}
```

## 💡 How to Get Video Links

### Method 1: Poll Status (Recommended)

```python
import requests
import time

base_url = "https://your-service-name.onrender.com"

# Submit job
response = requests.post(f"{base_url}/api/generate", json={...})
job_id = response.json()["job_id"]

# Poll until complete
while True:
    status = requests.get(f"{base_url}/api/status/{job_id}").json()
    if status["status"] == "completed":
        video_url = f"{base_url}{status['video_url']}"
        print(f"Video ready: {video_url}")
        break
    time.sleep(10)
```

### Method 2: List All Jobs

```bash
curl "https://your-service-name.onrender.com/api/jobs?status=completed"
```

### Method 3: Direct Access

Videos are accessible at:
```
https://your-service-name.onrender.com/api/videos/{job_id}.mp4
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/api/info` | GET | API capabilities |
| `/api/generate` | POST | Submit video generation job |
| `/api/status/{job_id}` | GET | Check job status |
| `/api/videos/{filename}` | GET | Download video |
| `/api/jobs` | GET | List all jobs |
| `/api/jobs/{job_id}` | DELETE | Delete job and video |
| `/docs` | GET | Interactive API docs |

## 💰 Cost Breakdown

### Monthly Costs (Render.com Ultra Plan)

- **Ultra Plan**: $450/month (8 cores, 32GB RAM)
- **Persistent Storage**: ~$25/month (100GB)
- **Total**: ~$475/month

### Cost Per Video

- ~$0.53 per video (assuming 30 videos/day)
- Much cheaper than GPU plans (~$1.50-$3.00 per video)

## 🧪 Testing

Test the API locally or in production:

```bash
# Basic test
python test_api.py http://localhost:10000

# Test with video generation (waits for completion)
python test_api.py http://localhost:10000 --wait

# Test production
python test_api.py https://your-service-name.onrender.com
```

## 🛠️ Local Development

### Using Docker (Recommended)

```bash
# Build CPU-optimized image
docker build -f Dockerfile.cpu -t hunyuan-api .

# Run
docker run -p 10000:10000 \
  -v $(pwd)/ckpts:/app/ckpts \
  -v $(pwd)/results:/app/results \
  hunyuan-api
```

### Using Python Directly

```bash
# Install dependencies
pip install -r requirements-api.txt
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Run server
python api_server.py
```

## ⚠️ Important Notes

1. **Model Download Required**: Download ~40GB of model checkpoints before deployment
2. **CPU Generation is Slow**: 10-30 minutes per video (vs 1-5 minutes on GPU)
3. **Frame Limit**: Max 129 frames per generation (~8.6 seconds at 15fps)
4. **Memory Usage**: Keep resolution at 640x480 or lower for stability
5. **Concurrent Jobs**: Limited to 2 concurrent jobs by default

## 🔒 Security Recommendations

Before going to production:

1. **Add Authentication**: Implement API keys or OAuth
2. **Rate Limiting**: Prevent abuse
3. **Input Validation**: Sanitize user prompts
4. **HTTPS Only**: Always use secure connections
5. **Monitor Usage**: Track API calls and costs

## 📝 Example Code

### Python

```python
import requests

# Generate video
response = requests.post(
    "https://your-service-name.onrender.com/api/generate",
    json={
        "prompt": "A sunset over the ocean",
        "width": 640,
        "height": 480,
        "video_length": 61,
        "fps": 15
    }
)

job_id = response.json()["job_id"]
print(f"Job ID: {job_id}")
```

### JavaScript

```javascript
const response = await fetch('https://your-service-name.onrender.com/api/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: 'A sunset over the ocean',
    width: 640,
    height: 480,
    video_length: 61,
    fps: 15
  })
});

const { job_id } = await response.json();
console.log('Job ID:', job_id);
```

### cURL

```bash
curl -X POST "https://your-service-name.onrender.com/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"A sunset over the ocean","width":640,"height":480,"video_length":61,"fps":15}'
```

## 🐛 Troubleshooting

### Model Not Loading
- Check logs in Render dashboard
- Verify models are downloaded
- Ensure persistent disk is mounted

### Out of Memory
- Reduce resolution to 480x360
- Set MAX_WORKERS=1
- Lower video_length to 13-61 frames

### Slow Generation
- **Expected** on CPU
- Reduce inference steps to 20-25
- Use lower resolution
- Smaller frame counts

## 📖 Additional Resources

- **Original README**: [README.md](README.md) - Original HunyuanVideo documentation
- **Deployment Checklist**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

See [LICENSE.txt](LICENSE.txt) for license information.

## 🙏 Acknowledgments

Based on [HunyuanVideo](https://github.com/Tencent-Hunyuan/HunyuanVideo) by Tencent.

---

**Need Help?** 
- Check the [CPU Deployment Guide](CPU_DEPLOYMENT_GUIDE.md)
- Read the [API Documentation](API_DOCUMENTATION.md)
- Visit the [Interactive Docs](https://your-service-name.onrender.com/docs)
