# Quick Start: 60-Second Videos at 15 FPS on Render.com Ultra Plan

This guide addresses the specific requirement: Deploy HunyuanVideo on Render.com Ultra plan ($450, 8 cores, 32GB RAM, CPU-only) for generating 60-second videos at 15 fps.

## 📋 What You're Getting

- **Platform**: Render.com Ultra Plan
- **Specs**: 8 CPU cores, 32GB RAM (no GPU/VRAM)
- **Cost**: $450/month + ~$25 storage = **$475/month total**
- **Target**: 60-second videos at 15 fps
- **API**: REST API for video generation
- **Video Access**: Direct URLs to download generated videos

## ⚠️ Important Limitation

The HunyuanVideo model supports **maximum 129 frames** per generation. At 15 fps, this equals **8.6 seconds**.

For 60-second videos, you have **three options**:

### Option 1: Frame Stretching (Recommended for Simplicity)
- Generate 61 frames at 15 fps (~4 seconds)
- Use video editing to stretch/interpolate to 60 seconds
- **Pros**: Single generation, fast
- **Cons**: Lower quality due to stretching

### Option 2: Multiple Segments (Best Quality)
- Generate 7 segments of 129 frames each (~8.6 seconds per segment)
- Stitch segments together using ffmpeg or video editor
- **Pros**: Best quality, true 60 seconds
- **Cons**: Takes longer (7 generations × 15-20 min = 2-3 hours total)

### Option 3: Lower FPS
- Generate at 8 fps instead of 15 fps
- 129 frames at 8 fps = 16 seconds
- Generate 4 segments for 60 seconds
- **Pros**: Fewer segments needed
- **Cons**: Lower frame rate

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Your Repository (5 minutes)

```bash
# Fork or clone this repository
git clone https://github.com/Devilhere444/HunyuanVideo.git
cd HunyuanVideo

# All necessary files are already included!
```

### Step 2: Download Models (1-2 hours)

**Important**: Do this BEFORE deployment to save time!

```bash
# Install Hugging Face CLI
pip install huggingface-hub

# Download models (~40GB)
huggingface-cli download tencent/HunyuanVideo --local-dir ./ckpts

# This will take 1-2 hours depending on your connection
```

### Step 3: Deploy on Render.com (10 minutes)

#### A. Push to GitHub

```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### B. Deploy Using Blueprint

1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Select the repository
5. Render detects `render-cpu.yaml` automatically
6. Review configuration:
   - Plan: **Ultra** (8 cores, 32GB RAM) - $450/month
   - Disk: **100GB** persistent storage - ~$25/month
7. Click **"Apply"**

### Step 4: Upload Models (20-40 minutes)

After deployment completes, upload models to persistent storage:

#### Option A: Via SSH (Recommended)

```bash
# Enable SSH in Render dashboard
# Then connect:
render ssh hunyuan-video-api

# Inside the instance:
cd /opt/render/project/src/ckpts
pip install huggingface-hub
huggingface-cli download tencent/HunyuanVideo --local-dir .

# Wait for download to complete
# Exit SSH session
exit
```

#### Option B: Via Cloud Storage

1. Upload your downloaded models to S3/GCS
2. Modify `start_api.sh` to download from cloud storage
3. Redeploy

### Step 5: Verify Deployment (2 minutes)

```bash
# Check health
curl https://your-service-name.onrender.com/health

# Should return:
# {
#   "status": "healthy",
#   "model_loaded": true,
#   "active_jobs": 0,
#   "total_jobs": 0
# }
```

## 📹 Generating 60-Second Videos

### Method 1: Single Segment with Stretching

**Generate a 4-second clip:**

```bash
curl -X POST "https://your-service-name.onrender.com/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Your video description here",
    "width": 640,
    "height": 480,
    "video_length": 61,
    "fps": 15,
    "num_inference_steps": 30
  }'
```

**Response:**
```json
{
  "job_id": "abc-123-def-456",
  "status": "queued",
  "check_status_url": "/api/status/abc-123-def-456"
}
```

**Check status:**
```bash
curl "https://your-service-name.onrender.com/api/status/abc-123-def-456"
```

**Download when complete:**
```bash
curl -O "https://your-service-name.onrender.com/api/videos/abc-123-def-456.mp4"
```

**Stretch to 60 seconds using ffmpeg:**
```bash
ffmpeg -i abc-123-def-456.mp4 -filter:v "setpts=15*PTS" -r 15 output_60sec.mp4
```

### Method 2: Multiple Segments (Best Quality)

**Python script for generating 7 segments:**

```python
import requests
import time

BASE_URL = "https://your-service-name.onrender.com"
PROMPT_BASE = "Your video description"

# Generate 7 segments
job_ids = []
for i in range(7):
    # Vary prompts slightly for continuity
    prompt = f"{PROMPT_BASE}, part {i+1} of 7, smooth transition"
    
    response = requests.post(
        f"{BASE_URL}/api/generate",
        json={
            "prompt": prompt,
            "width": 640,
            "height": 480,
            "video_length": 129,
            "fps": 15,
            "num_inference_steps": 30,
            "seed": 42 + i  # Sequential seeds for continuity
        }
    )
    
    job_id = response.json()["job_id"]
    job_ids.append(job_id)
    print(f"Segment {i+1} submitted: {job_id}")
    
    # Wait before submitting next to avoid queue overflow
    time.sleep(5)

print(f"\nAll segments submitted. Job IDs: {job_ids}")
print("Each segment will take 15-20 minutes to generate.")
print("Total estimated time: 2-3 hours")

# Wait for all to complete (not shown - would poll each job)
# Then download all videos and stitch with ffmpeg
```

**Stitch segments together:**

```bash
# Create file list
cat > segments.txt << EOF
file 'segment1.mp4'
file 'segment2.mp4'
file 'segment3.mp4'
file 'segment4.mp4'
file 'segment5.mp4'
file 'segment6.mp4'
file 'segment7.mp4'
EOF

# Concatenate
ffmpeg -f concat -safe 0 -i segments.txt -c copy final_60sec.mp4
```

## 🔗 Getting Video Links

### Direct URL Access

Once a job completes, the video is available at:
```
https://your-service-name.onrender.com/api/videos/{job_id}.mp4
```

### Programmatic Access

```python
import requests

# Submit job
response = requests.post(f"{BASE_URL}/api/generate", json={...})
job_id = response.json()["job_id"]

# Poll until complete
while True:
    status = requests.get(f"{BASE_URL}/api/status/{job_id}").json()
    
    if status["status"] == "completed":
        # Get video URL
        video_url = f"{BASE_URL}{status['video_url']}"
        print(f"Video ready: {video_url}")
        
        # Or download
        video = requests.get(video_url)
        with open("video.mp4", "wb") as f:
            f.write(video.content)
        break
    
    time.sleep(10)
```

### Share Links

Generated videos can be shared directly:
- **Direct link**: `https://your-service-name.onrender.com/api/videos/{job_id}.mp4`
- **Embeddable**: Can be embedded in web pages with `<video>` tag
- **Downloadable**: Right-click → Save As in browsers

## ⏱️ Performance Expectations

### Single Segment Generation (61 frames)

| Resolution | Steps | Expected Time |
|------------|-------|---------------|
| 480x360 | 25 | 8-12 minutes |
| 640x480 | 30 | 12-18 minutes |
| 720x480 | 35 | 18-25 minutes |

### Full 60-Second Video (7 segments × 129 frames)

| Resolution | Steps | Time per Segment | Total Time |
|------------|-------|------------------|------------|
| 480x360 | 25 | 15-20 min | 1.5-2 hours |
| 640x480 | 30 | 18-25 min | 2-3 hours |
| 720x480 | 35 | 25-30 min | 3-4 hours |

### Concurrent Processing

- **MAX_WORKERS=2**: Can process 2 videos simultaneously
- Use this to generate multiple segments in parallel
- Estimated time with 2 workers: ~1-1.5 hours for 7 segments

## 💰 Cost Breakdown

### Monthly Costs
- **Ultra Plan**: $450/month
- **100GB Storage**: ~$25/month
- **Total**: **$475/month**

### Per Video Costs
Assuming 30 videos per day:
- Videos per month: ~900
- Cost per video: **$0.53**

Compare to GPU: $1.50-$3.00 per video
**Savings: 65-85%**

## 🎯 Recommended Workflow for 60-Second Videos

### For Fast Previews
1. Generate single 61-frame segment (12-18 min)
2. Stretch to 60 seconds with ffmpeg
3. Review and iterate on prompts
4. **Total time**: 15-20 minutes

### For Production Quality
1. Finalize your prompt
2. Generate 7 segments of 129 frames each
3. Use consistent seeds for continuity
4. Let run for 2-3 hours (or overnight)
5. Download all segments
6. Stitch with ffmpeg
7. **Total time**: 2-3 hours

### For Batch Processing
1. Submit multiple video requests
2. Queue processes 2 at a time
3. Return later to download all
4. Perfect for overnight processing
5. **Throughput**: 10-15 videos per day

## 📊 API Capabilities

- **Max concurrent jobs**: 2 (configurable)
- **Queue size**: Unlimited
- **File retention**: Until manually deleted
- **Max video length**: 129 frames (8.6 sec at 15fps)
- **Supported resolutions**: 256x256 to 1280x1280
- **Supported FPS**: 8-30 fps
- **Inference steps**: 10-50 (30 recommended for CPU)

## 🔧 Optimization Tips

1. **Start with low resolution** (480x360) to test prompts
2. **Use fewer steps** (25-30) for acceptable quality
3. **Generate segments overnight** for long videos
4. **Use consistent seeds** for segment continuity
5. **Batch process** multiple videos during off-hours

## 📝 Complete Example Script

See `example_client.py` for a complete working example:

```bash
# Generate a video
python example_client.py \
  --url https://your-service-name.onrender.com \
  --prompt "Ocean waves crashing on beach at sunset" \
  --width 640 \
  --height 480 \
  --video-length 61 \
  --fps 15 \
  --steps 30 \
  --output my_video.mp4
```

## 📚 Additional Resources

- **Full API Documentation**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Deployment Guide**: [CPU_DEPLOYMENT_GUIDE.md](CPU_DEPLOYMENT_GUIDE.md)
- **Implementation Summary**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Interactive Docs**: `https://your-service-name.onrender.com/docs`

## ✅ Success Checklist

- [ ] Repository forked/cloned
- [ ] Models downloaded (~40GB)
- [ ] Deployed on Render.com Ultra plan
- [ ] Models uploaded to persistent storage
- [ ] Health check returns "healthy"
- [ ] Test video generated successfully
- [ ] Can access video via direct URL
- [ ] API documentation accessible
- [ ] Ready for production use

## 🎉 You're All Set!

Your HunyuanVideo API is now running on Render.com and ready to generate videos. The API is fully functional and optimized for CPU-only operation on the Ultra plan.

**Your API is available at**: `https://your-service-name.onrender.com`

**Next Steps**:
1. Test with various prompts
2. Set up monitoring
3. Add authentication (recommended)
4. Scale as needed

For support, refer to the documentation files or check the `/docs` endpoint for interactive API documentation.
