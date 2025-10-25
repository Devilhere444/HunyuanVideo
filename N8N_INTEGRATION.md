# N8N Integration Guide for HunyuanVideo

## Overview

This guide shows you how to integrate HunyuanVideo text-to-video generation into your N8N workflows. Generate high-quality portrait and landscape videos from text prompts using simple HTTP requests.

## Quick Start

### Prerequisites

1. HunyuanVideo API server running (see API_README.md)
2. N8N Integration service running (optional, provides webhook endpoints)
3. N8N instance (cloud or self-hosted)

### Option 1: Direct API Integration (Recommended)

Use the main HunyuanVideo API directly in N8N workflows.

#### Step 1: Create HTTP Request Node - Generate Video

1. Add an **HTTP Request** node to your N8N workflow
2. Configure the node:
   - **Method**: POST
   - **URL**: `http://your-server:10000/api/generate`
   - **Authentication**: None (or add if configured)
   - **Body Type**: JSON
   - **Body**:
     ```json
     {
       "prompt": "{{$json.prompt}}",
       "preset": "portrait_60s"
     }
     ```

**Available Presets:**
- `portrait_60s` - 544x960 (9:16), ~60 seconds, 24fps (Instagram Reels, TikTok)
- `portrait_30s` - 544x960 (9:16), ~30 seconds, 24fps
- `landscape_60s` - 960x544 (16:9), ~60 seconds, 24fps (YouTube)
- `landscape_30s` - 960x544 (16:9), ~30 seconds, 24fps

#### Step 2: Extract Job ID

Add a **Set** node after the HTTP Request:
- **Name**: Extract Job ID
- **Mode**: Manual
- **Values**:
  - `job_id`: `{{$json.job_id}}`
  - `status_url`: `http://your-server:10000/api/status/{{$json.job_id}}`

#### Step 3: Wait and Check Status (Loop)

Add a **Wait** node:
- **Resume**: After Time Interval
- **Wait Amount**: 30 seconds

Add an **HTTP Request** node:
- **Method**: GET
- **URL**: `http://your-server:10000/api/status/{{$json.job_id}}`

Add an **IF** node to check completion:
- **Condition**: `{{$json.status}}` equals `completed`

#### Step 4: Download Video

Add an **HTTP Request** node (on True branch):
- **Method**: GET
- **URL**: `http://your-server:10000{{$json.video_url}}`
- **Response Format**: File
- **Download File**: Yes
- **File Name**: `generated_video_{{$json.job_id}}.mp4`

### Option 2: N8N Integration Service (Webhook Compatible)

The N8N Integration Service provides simplified webhook endpoints.

#### Running the Integration Service

```bash
# Set environment variables
export N8N_API_BASE_URL=http://localhost:10000
export N8N_WEBHOOK_PORT=8080

# Run the service
python n8n_integration.py
```

#### Using Webhook Endpoints in N8N

1. **Generate Video**:
   - **URL**: `http://your-server:8080/webhook/generate`
   - **Method**: POST
   - **Body**:
     ```json
     {
       "prompt": "A cat walks on the grass, realistic style",
       "preset": "portrait_60s"
     }
     ```

2. **Check Status**:
   - **URL**: `http://your-server:8080/webhook/status/{job_id}`
   - **Method**: GET

3. **Download Video**:
   - **URL**: `http://your-server:8080/webhook/download/{job_id}`
   - **Method**: GET

## Example Workflows

### Example 1: Generate Portrait Video from Google Sheets

**Workflow:**
1. **Google Sheets Trigger** - New row added with video prompt
2. **HTTP Request** - Generate video with prompt from sheet
3. **Wait** - 30 seconds
4. **HTTP Request (Loop)** - Check status until completed
5. **HTTP Request** - Download video
6. **Google Drive** - Upload video to folder
7. **Google Sheets** - Update row with video link

### Example 2: Social Media Content Creator

**Workflow:**
1. **Webhook Trigger** - Receive content request
2. **HTTP Request** - Generate portrait video
3. **Wait Loop** - Check status every 30 seconds
4. **HTTP Request** - Download video
5. **Cloudinary/S3** - Upload to cloud storage
6. **Webhook Response** - Return video URL

### Example 3: Batch Video Generation

**Workflow:**
1. **Schedule Trigger** - Daily at midnight
2. **Airtable** - Get list of video prompts
3. **Loop** - For each prompt:
   - **HTTP Request** - Generate video
   - **Store** - Save job_id
4. **Wait** - 2 hours
5. **Loop** - For each job_id:
   - **HTTP Request** - Check status
   - **HTTP Request** - Download if completed
   - **Email** - Send notification

## Complete Request Examples

### Basic Portrait Video (60 seconds)

```json
{
  "prompt": "A serene sunset over the ocean, with waves gently rolling onto a sandy beach. The sky is painted with vibrant orange and pink hues.",
  "preset": "portrait_60s"
}
```

### Custom Configuration

```json
{
  "prompt": "A futuristic city at night, with neon lights and flying cars",
  "width": 544,
  "height": 960,
  "video_length": 129,
  "fps": 24,
  "num_inference_steps": 40,
  "seed": 42
}
```

### Landscape Video (30 seconds)

```json
{
  "prompt": "A peaceful forest path in autumn, with colorful leaves falling from trees",
  "preset": "landscape_30s"
}
```

## Response Format

### Generate Response

```json
{
  "job_id": "uuid-string",
  "status": "queued",
  "message": "Video generation job submitted successfully",
  "check_status_url": "/api/status/{job_id}"
}
```

### Status Response

```json
{
  "job_id": "uuid-string",
  "status": "processing",
  "progress": 0.45,
  "created_at": "2025-10-25T17:00:00",
  "updated_at": "2025-10-25T17:12:30",
  "video_url": null,
  "error": null,
  "estimated_time": 900
}
```

### Completed Status

```json
{
  "job_id": "uuid-string",
  "status": "completed",
  "progress": 1.0,
  "created_at": "2025-10-25T17:00:00",
  "updated_at": "2025-10-25T17:18:45",
  "video_url": "/api/videos/uuid-string.mp4",
  "error": null
}
```

## Video Specifications

### Portrait (9:16 - TikTok/Instagram Reels)
- **Resolution**: 544x960
- **Aspect Ratio**: 9:16
- **Recommended For**: TikTok, Instagram Reels, YouTube Shorts
- **Duration**: Up to ~60 seconds (129 frames at 24fps)

### Landscape (16:9 - YouTube)
- **Resolution**: 960x544
- **Aspect Ratio**: 16:9
- **Recommended For**: YouTube, Facebook, TV
- **Duration**: Up to ~60 seconds (129 frames at 24fps)

## Performance & Timing

### CPU (8 cores, 32GB RAM)
- **Portrait 60s (30 steps)**: 15-25 minutes
- **Portrait 30s (30 steps)**: 8-15 minutes
- **Landscape 60s (30 steps)**: 15-25 minutes
- **Landscape 30s (30 steps)**: 8-15 minutes

### Quality Settings
- **10-20 steps**: Fast, lower quality (testing)
- **30 steps**: Good quality (recommended)
- **40 steps**: High quality
- **50 steps**: Best quality (slower)

## Error Handling

### Common Errors

1. **503 Service Unavailable**: Model not initialized yet
   - **Solution**: Wait a few minutes after server start

2. **404 Job Not Found**: Invalid job_id
   - **Solution**: Check job_id is correct

3. **Timeout**: Generation taking too long
   - **Solution**: Normal for CPU, wait longer (15-25 minutes)

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

## Best Practices

1. **Use Presets**: Start with presets for consistent results
2. **Poll Interval**: Check status every 30-60 seconds
3. **Timeout**: Allow at least 30 minutes for completion
4. **Error Handling**: Implement retry logic for transient errors
5. **Storage**: Download and store videos promptly after completion
6. **Cleanup**: Delete old jobs to free up server space

## Advanced Configuration

### Custom Resolution

For custom aspect ratios, ensure dimensions are divisible by 8:

```json
{
  "prompt": "Your prompt here",
  "width": 640,
  "height": 640,
  "video_length": 65,
  "fps": 24,
  "num_inference_steps": 30
}
```

### Seed for Reproducibility

Use the same seed to generate similar videos:

```json
{
  "prompt": "Your prompt here",
  "preset": "portrait_60s",
  "seed": 12345
}
```

## Troubleshooting

### Video Generation Fails

1. Check API server logs
2. Verify prompt is clear and descriptive
3. Try simpler prompts first
4. Reduce inference steps for testing

### Long Generation Times

1. Expected on CPU (15-25 minutes)
2. Reduce video_length for faster results
3. Lower num_inference_steps (with quality trade-off)
4. Use presets for optimized settings

### N8N Connection Issues

1. Verify server URL is accessible from N8N
2. Check firewall/network settings
3. Test with `/health` endpoint first
4. Use full URL including protocol (http://)

## API Endpoints Reference

### Main API (Port 10000)

- `POST /api/generate` - Submit video generation job
- `GET /api/status/{job_id}` - Check job status
- `GET /api/videos/{filename}` - Download video
- `GET /api/jobs` - List all jobs
- `DELETE /api/jobs/{job_id}` - Delete job
- `GET /api/info` - Get API information
- `GET /health` - Health check

### N8N Integration Service (Port 8080)

- `POST /webhook/generate` - Submit via webhook
- `GET /webhook/status/{job_id}` - Check status via webhook
- `GET /webhook/download/{job_id}` - Download via webhook
- `GET /webhook/info` - Get preset information
- `POST /webhook/test` - Test webhook connection

## Support

For issues or questions:
1. Check server logs
2. Review API_DOCUMENTATION.md
3. Test with example_client.py
4. Verify server is running with `/health` endpoint

## Example N8N JSON Workflow

Save this as a `.json` file and import into N8N:

```json
{
  "name": "HunyuanVideo Portrait Generator",
  "nodes": [
    {
      "parameters": {
        "method": "POST",
        "url": "http://localhost:10000/api/generate",
        "jsonParameters": true,
        "options": {},
        "bodyParametersJson": "{\n  \"prompt\": \"{{$json.prompt}}\",\n  \"preset\": \"portrait_60s\"\n}"
      },
      "name": "Generate Video",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "amount": 30,
        "unit": "seconds"
      },
      "name": "Wait",
      "type": "n8n-nodes-base.wait",
      "typeVersion": 1,
      "position": [450, 300]
    },
    {
      "parameters": {
        "url": "http://localhost:10000/api/status/{{$json.job_id}}"
      },
      "name": "Check Status",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [650, 300]
    }
  ],
  "connections": {
    "Generate Video": {
      "main": [[{"node": "Wait", "type": "main", "index": 0}]]
    },
    "Wait": {
      "main": [[{"node": "Check Status", "type": "main", "index": 0}]]
    }
  }
}
```

## Conclusion

This integration enables powerful text-to-video automation workflows in N8N. Use the presets for quick setup, or customize parameters for specific needs. The CPU-optimized backend ensures reliable generation without GPU requirements.
