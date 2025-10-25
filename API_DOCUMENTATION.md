# HunyuanVideo REST API Documentation

## Overview

This REST API provides video generation capabilities using HunyuanVideo, optimized for CPU-only deployment on Render.com's Ultra plan (8 cores, 32GB RAM).

## Base URL

```
Production: https://your-service-name.onrender.com
Local: http://localhost:10000
```

## Quick Start

### 1. Generate a Video

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

### 2. Check Job Status

```bash
curl "https://your-service-name.onrender.com/api/status/550e8400-e29b-41d4-a716-446655440000"
```

Response (Processing):
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 0.5,
  "created_at": "2025-10-25T16:00:00",
  "updated_at": "2025-10-25T16:05:00",
  "video_url": null,
  "error": null,
  "estimated_time": 600
}
```

Response (Completed):
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 1.0,
  "created_at": "2025-10-25T16:00:00",
  "updated_at": "2025-10-25T16:10:00",
  "video_url": "/api/videos/550e8400-e29b-41d4-a716-446655440000.mp4",
  "error": null,
  "estimated_time": 600
}
```

### 3. Download Video

```bash
curl -O "https://your-service-name.onrender.com/api/videos/550e8400-e29b-41d4-a716-446655440000.mp4"
```

Or open in browser:
```
https://your-service-name.onrender.com/api/videos/550e8400-e29b-41d4-a716-446655440000.mp4
```

## API Endpoints

### General Endpoints

#### GET /
Root endpoint with API information
```bash
curl "https://your-service-name.onrender.com/"
```

#### GET /health
Health check endpoint
```bash
curl "https://your-service-name.onrender.com/health"
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "active_jobs": 2,
  "total_jobs": 15
}
```

#### GET /api/info
Get API capabilities and configuration
```bash
curl "https://your-service-name.onrender.com/api/info"
```

### Video Generation Endpoints

#### POST /api/generate
Submit a video generation job

**Request Body:**
```json
{
  "prompt": "A cat walks on the grass, realistic style.",
  "width": 640,
  "height": 480,
  "video_length": 61,
  "fps": 15,
  "seed": null,
  "num_inference_steps": 30,
  "guidance_scale": 1.0,
  "flow_shift": 7.0,
  "embedded_guidance_scale": 6.0
}
```

**Parameters:**

| Parameter | Type | Required | Default | Range | Description |
|-----------|------|----------|---------|-------|-------------|
| `prompt` | string | Yes | - | - | Text description of the video |
| `width` | integer | No | 640 | 256-1280 | Video width in pixels |
| `height` | integer | No | 480 | 256-1280 | Video height in pixels |
| `video_length` | integer | No | 61 | 13-129 | Number of frames |
| `fps` | integer | No | 15 | 8-30 | Frames per second |
| `seed` | integer | No | null | - | Random seed (null=random) |
| `num_inference_steps` | integer | No | 30 | 10-50 | Denoising steps (lower=faster) |
| `guidance_scale` | float | No | 1.0 | 1.0-20.0 | Guidance scale |
| `flow_shift` | float | No | 7.0 | 0.0-10.0 | Flow shift parameter |
| `embedded_guidance_scale` | float | No | 6.0 | 1.0-20.0 | Embedded guidance scale |

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Video generation job submitted successfully",
  "check_status_url": "/api/status/550e8400-e29b-41d4-a716-446655440000"
}
```

#### GET /api/status/{job_id}
Check status of a video generation job

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 1.0,
  "created_at": "2025-10-25T16:00:00",
  "updated_at": "2025-10-25T16:10:00",
  "video_url": "/api/videos/550e8400-e29b-41d4-a716-446655440000.mp4",
  "error": null,
  "estimated_time": 600
}
```

**Status Values:**
- `queued`: Job is waiting to be processed
- `processing`: Job is currently being processed
- `completed`: Job completed successfully
- `failed`: Job failed with an error

#### GET /api/videos/{filename}
Download generated video

Returns video file for download or streaming.

#### GET /api/jobs
List all jobs with optional filtering

**Query Parameters:**
- `status` (optional): Filter by status (queued, processing, completed, failed)
- `limit` (optional): Maximum number of jobs to return (1-100, default: 50)

**Example:**
```bash
curl "https://your-service-name.onrender.com/api/jobs?status=completed&limit=10"
```

#### DELETE /api/jobs/{job_id}
Delete a job and its video

Note: Cannot delete jobs that are currently processing.

## Recommended Settings for CPU Deployment

### For 60-second videos at 15 fps:

**Standard Quality (Fast):**
```json
{
  "prompt": "Your prompt here",
  "width": 480,
  "height": 360,
  "video_length": 61,
  "fps": 15,
  "num_inference_steps": 25
}
```
- **Estimated time**: 8-12 minutes
- **Quality**: Good for previews

**High Quality (Slower):**
```json
{
  "prompt": "Your prompt here",
  "width": 640,
  "height": 480,
  "video_length": 61,
  "fps": 15,
  "num_inference_steps": 30
}
```
- **Estimated time**: 12-18 minutes
- **Quality**: Recommended balance

**Maximum Quality (Very Slow):**
```json
{
  "prompt": "Your prompt here",
  "width": 720,
  "height": 480,
  "video_length": 61,
  "fps": 15,
  "num_inference_steps": 40
}
```
- **Estimated time**: 20-30 minutes
- **Quality**: Best quality on CPU

## Code Examples

### Python

```python
import requests
import time

# API base URL
BASE_URL = "https://your-service-name.onrender.com"

# 1. Submit video generation job
response = requests.post(
    f"{BASE_URL}/api/generate",
    json={
        "prompt": "A cat walks on the grass, realistic style.",
        "width": 640,
        "height": 480,
        "video_length": 61,
        "fps": 15,
        "num_inference_steps": 30
    }
)

job_data = response.json()
job_id = job_data["job_id"]
print(f"Job submitted: {job_id}")

# 2. Poll for completion
while True:
    status_response = requests.get(f"{BASE_URL}/api/status/{job_id}")
    status = status_response.json()
    
    print(f"Status: {status['status']} - Progress: {status['progress']*100:.1f}%")
    
    if status["status"] == "completed":
        video_url = status["video_url"]
        print(f"Video ready: {BASE_URL}{video_url}")
        break
    elif status["status"] == "failed":
        print(f"Generation failed: {status['error']}")
        break
    
    time.sleep(10)  # Check every 10 seconds

# 3. Download video
if status["status"] == "completed":
    video_response = requests.get(f"{BASE_URL}{video_url}")
    with open("generated_video.mp4", "wb") as f:
        f.write(video_response.content)
    print("Video downloaded: generated_video.mp4")
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');
const fs = require('fs');

const BASE_URL = 'https://your-service-name.onrender.com';

async function generateVideo() {
  // 1. Submit job
  const submitResponse = await axios.post(`${BASE_URL}/api/generate`, {
    prompt: 'A cat walks on the grass, realistic style.',
    width: 640,
    height: 480,
    video_length: 61,
    fps: 15,
    num_inference_steps: 30
  });
  
  const jobId = submitResponse.data.job_id;
  console.log(`Job submitted: ${jobId}`);
  
  // 2. Poll for completion
  while (true) {
    const statusResponse = await axios.get(`${BASE_URL}/api/status/${jobId}`);
    const status = statusResponse.data;
    
    console.log(`Status: ${status.status} - Progress: ${(status.progress * 100).toFixed(1)}%`);
    
    if (status.status === 'completed') {
      console.log(`Video ready: ${BASE_URL}${status.video_url}`);
      
      // 3. Download video
      const videoResponse = await axios.get(
        `${BASE_URL}${status.video_url}`,
        { responseType: 'arraybuffer' }
      );
      
      fs.writeFileSync('generated_video.mp4', videoResponse.data);
      console.log('Video downloaded: generated_video.mp4');
      break;
    } else if (status.status === 'failed') {
      console.error(`Generation failed: ${status.error}`);
      break;
    }
    
    await new Promise(resolve => setTimeout(resolve, 10000)); // Wait 10 seconds
  }
}

generateVideo().catch(console.error);
```

### cURL Script

```bash
#!/bin/bash

BASE_URL="https://your-service-name.onrender.com"

# 1. Submit job
JOB_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A cat walks on the grass, realistic style.",
    "width": 640,
    "height": 480,
    "video_length": 61,
    "fps": 15,
    "num_inference_steps": 30
  }')

JOB_ID=$(echo $JOB_RESPONSE | jq -r '.job_id')
echo "Job submitted: $JOB_ID"

# 2. Poll for completion
while true; do
  STATUS_RESPONSE=$(curl -s "${BASE_URL}/api/status/${JOB_ID}")
  STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')
  PROGRESS=$(echo $STATUS_RESPONSE | jq -r '.progress')
  
  echo "Status: $STATUS - Progress: $(echo "$PROGRESS * 100" | bc)%"
  
  if [ "$STATUS" = "completed" ]; then
    VIDEO_URL=$(echo $STATUS_RESPONSE | jq -r '.video_url')
    echo "Video ready: ${BASE_URL}${VIDEO_URL}"
    
    # 3. Download video
    curl -o generated_video.mp4 "${BASE_URL}${VIDEO_URL}"
    echo "Video downloaded: generated_video.mp4"
    break
  elif [ "$STATUS" = "failed" ]; then
    ERROR=$(echo $STATUS_RESPONSE | jq -r '.error')
    echo "Generation failed: $ERROR"
    break
  fi
  
  sleep 10
done
```

## Error Handling

### Common Errors

**503 Service Unavailable**
```json
{
  "detail": "Model not initialized yet. Please try again in a few moments."
}
```
- **Solution**: Wait for the model to finish loading (check `/health` endpoint)

**404 Not Found**
```json
{
  "detail": "Job not found"
}
```
- **Solution**: Verify the job ID is correct

**400 Bad Request**
```json
{
  "detail": "Cannot delete job that is currently processing"
}
```
- **Solution**: Wait for job to complete before deleting

## Performance Expectations

### CPU Deployment (8 cores, 32GB RAM)

| Resolution | Frames | Steps | Estimated Time |
|------------|--------|-------|----------------|
| 480x360 | 61 | 25 | 8-12 min |
| 640x480 | 61 | 30 | 12-18 min |
| 720x480 | 61 | 35 | 18-25 min |
| 960x544 | 61 | 40 | 25-35 min |

**Note**: Times are estimates and may vary based on:
- Server load
- Prompt complexity
- Concurrent jobs

### Optimization Tips

1. **Lower resolution**: Use 640x480 or smaller for faster generation
2. **Fewer steps**: 25-30 steps provide good quality with acceptable speed
3. **Batch processing**: Queue multiple jobs and process overnight
4. **Monitor load**: Check `/health` to see active jobs

## Rate Limiting

Currently, the API supports:
- **Max concurrent jobs**: 2 (configurable via `MAX_WORKERS`)
- **Queue size**: Unlimited (but watch memory usage)
- **File retention**: Videos remain until manually deleted

**Recommendation**: Implement your own rate limiting on the client side to avoid overwhelming the server.

## Interactive API Documentation

Visit the interactive Swagger UI documentation at:
```
https://your-service-name.onrender.com/docs
```

Or ReDoc format at:
```
https://your-service-name.onrender.com/redoc
```

## Support

- **GitHub Issues**: Report bugs and feature requests
- **API Status**: Check `/health` endpoint
- **Documentation**: This file and `/docs` endpoint

## License

See [LICENSE.txt](LICENSE.txt) for details.
