#!/usr/bin/env python
"""
N8N Integration Script for HunyuanVideo API
============================================

This script provides a webhook-compatible interface for N8N automation workflows.
It can be used as a standalone service or integrated into N8N using HTTP Request nodes.

Features:
- Simple JSON request/response format
- Webhook-compatible endpoints
- Support for portrait and landscape video generation
- Preset configurations for common use cases (60-second portrait videos)
- Progress tracking and status updates
- Direct video download URLs

N8N Workflow Setup:
1. Use HTTP Request node to call this service
2. Parse JSON response for job_id
3. Use polling loop to check status
4. Download video when completed

Example N8N HTTP Request Configuration:
- Method: POST
- URL: http://your-server:8080/webhook/generate
- Body Type: JSON
- Body: {"prompt": "Your video prompt", "preset": "portrait_60s"}
"""

import os
import json
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from loguru import logger
import requests

# N8N Integration Configuration
N8N_API_BASE_URL = os.getenv("N8N_API_BASE_URL", "http://localhost:10000")
N8N_WEBHOOK_PORT = int(os.getenv("N8N_WEBHOOK_PORT", "8080"))
N8N_WEBHOOK_HOST = os.getenv("N8N_WEBHOOK_HOST", "0.0.0.0")

app = FastAPI(
    title="HunyuanVideo N8N Integration",
    description="Webhook-compatible API for N8N workflow automation",
    version="1.0.0"
)

# CORS middleware for N8N
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class N8NVideoRequest(BaseModel):
    """
    N8N-compatible video generation request
    
    Simple JSON format optimized for N8N workflows
    """
    prompt: str = Field(..., description="Text prompt for video generation")
    preset: Optional[str] = Field(
        default="portrait_60s",
        description="Preset: portrait_60s, portrait_30s, landscape_60s, landscape_30s"
    )
    width: Optional[int] = Field(default=None, description="Custom width (overrides preset)")
    height: Optional[int] = Field(default=None, description="Custom height (overrides preset)")
    video_length: Optional[int] = Field(default=None, description="Custom frame count (overrides preset)")
    fps: Optional[int] = Field(default=None, description="Custom FPS (overrides preset)")
    seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")
    num_inference_steps: Optional[int] = Field(default=None, description="Inference steps (quality)")
    webhook_url: Optional[str] = Field(default=None, description="N8N webhook URL to call when complete")


class N8NVideoResponse(BaseModel):
    """N8N-compatible video generation response"""
    success: bool
    job_id: str
    status: str
    message: str
    status_url: str
    estimated_time_seconds: int
    timestamp: str


class N8NStatusResponse(BaseModel):
    """N8N-compatible status check response"""
    success: bool
    job_id: str
    status: str  # queued, processing, completed, failed
    progress_percent: float
    video_url: Optional[str] = None
    download_url: Optional[str] = None
    error: Optional[str] = None
    timestamp: str


def build_api_request(n8n_request: N8NVideoRequest) -> Dict[str, Any]:
    """Convert N8N request to HunyuanVideo API request format"""
    api_request = {
        "prompt": n8n_request.prompt,
        "preset": n8n_request.preset
    }
    
    # Override preset with custom values if provided
    if n8n_request.width is not None:
        api_request["width"] = n8n_request.width
    if n8n_request.height is not None:
        api_request["height"] = n8n_request.height
    if n8n_request.video_length is not None:
        api_request["video_length"] = n8n_request.video_length
    if n8n_request.fps is not None:
        api_request["fps"] = n8n_request.fps
    if n8n_request.seed is not None:
        api_request["seed"] = n8n_request.seed
    if n8n_request.num_inference_steps is not None:
        api_request["num_inference_steps"] = n8n_request.num_inference_steps
    
    return api_request


@app.get("/", tags=["General"])
async def root():
    """Root endpoint with N8N integration information"""
    return {
        "service": "HunyuanVideo N8N Integration",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "generate": "/webhook/generate (POST)",
            "status": "/webhook/status/{job_id} (GET)",
            "download": "/webhook/download/{job_id} (GET)",
            "info": "/webhook/info (GET)"
        },
        "n8n_setup": {
            "step_1": "Create HTTP Request node in N8N",
            "step_2": "Set method to POST",
            "step_3": f"Set URL to http://your-server:{N8N_WEBHOOK_PORT}/webhook/generate",
            "step_4": "Set body type to JSON",
            "step_5": "Add prompt and preset to body",
            "step_6": "Use polling loop to check status endpoint",
            "step_7": "Download video when status is 'completed'"
        }
    }


@app.get("/webhook/info", tags=["N8N Webhooks"])
async def webhook_info():
    """
    Get information about available presets and configurations
    
    Use this in N8N to show users available options
    """
    try:
        response = requests.get(f"{N8N_API_BASE_URL}/api/info", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to get API info: {e}")
        raise HTTPException(status_code=503, detail="Backend API not available")


@app.post("/webhook/generate", response_model=N8NVideoResponse, tags=["N8N Webhooks"])
async def webhook_generate(request: N8NVideoRequest):
    """
    Generate video via N8N webhook
    
    This is the main endpoint for N8N workflows.
    
    Example N8N HTTP Request Body:
    {
        "prompt": "A cat walks on the grass, realistic style",
        "preset": "portrait_60s"
    }
    
    Returns job_id and status_url for tracking progress.
    """
    try:
        # Build API request
        api_request = build_api_request(request)
        
        # Submit to HunyuanVideo API
        logger.info(f"Submitting video generation request: {api_request}")
        response = requests.post(
            f"{N8N_API_BASE_URL}/api/generate",
            json=api_request,
            timeout=30
        )
        response.raise_for_status()
        job_data = response.json()
        
        job_id = job_data["job_id"]
        
        # If webhook_url provided, store it for later callback
        # (Implementation would require database or cache)
        
        return N8NVideoResponse(
            success=True,
            job_id=job_id,
            status=job_data["status"],
            message="Video generation started successfully",
            status_url=f"/webhook/status/{job_id}",
            estimated_time_seconds=900,  # ~15 minutes for CPU
            timestamp=datetime.now().isoformat()
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to submit video generation: {e}")
        raise HTTPException(status_code=503, detail=f"Backend API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/webhook/status/{job_id}", response_model=N8NStatusResponse, tags=["N8N Webhooks"])
async def webhook_status(job_id: str):
    """
    Check video generation status via N8N webhook
    
    Use this in N8N polling loop to track progress.
    
    Returns:
    - status: queued, processing, completed, failed
    - progress_percent: 0-100
    - download_url: Available when status is 'completed'
    """
    try:
        response = requests.get(f"{N8N_API_BASE_URL}/api/status/{job_id}", timeout=10)
        response.raise_for_status()
        status_data = response.json()
        
        download_url = None
        if status_data["status"] == "completed" and status_data.get("video_url"):
            download_url = f"/webhook/download/{job_id}"
        
        return N8NStatusResponse(
            success=True,
            job_id=status_data["job_id"],
            status=status_data["status"],
            progress_percent=status_data["progress"] * 100,
            video_url=status_data.get("video_url"),
            download_url=download_url,
            error=status_data.get("error"),
            timestamp=datetime.now().isoformat()
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get status: {e}")
        raise HTTPException(status_code=404, detail="Job not found or API unavailable")


@app.get("/webhook/download/{job_id}", tags=["N8N Webhooks"])
async def webhook_download(job_id: str):
    """
    Download generated video via N8N webhook
    
    Use this in N8N to download the final video file.
    Returns the video URL for the client to download directly.
    """
    try:
        # Validate job_id format to prevent injection attacks
        import re
        if not re.match(r'^[a-f0-9\-]{36}$', job_id):
            raise HTTPException(status_code=400, detail="Invalid job ID format")
        
        # First check if video is ready
        status_response = requests.get(f"{N8N_API_BASE_URL}/api/status/{job_id}", timeout=10)
        status_response.raise_for_status()
        status_data = status_response.json()
        
        if status_data["status"] != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Video not ready. Current status: {status_data['status']}"
            )
        
        if not status_data.get("video_url"):
            raise HTTPException(status_code=404, detail="Video URL not available")
        
        # Validate that the video_url is from our API (prevent open redirect)
        video_path = status_data['video_url']
        if not video_path.startswith('/api/videos/'):
            raise HTTPException(status_code=400, detail="Invalid video URL")
        
        # Extract just the filename for additional validation
        filename_match = re.match(r'^/api/videos/([a-f0-9\-]+\.mp4)$', video_path)
        if not filename_match:
            raise HTTPException(status_code=400, detail="Invalid video path format")
        
        # Return the validated URL for client to download
        # Client should download from: N8N_API_BASE_URL + video_path
        return JSONResponse({
            "success": True,
            "job_id": job_id,
            "download_url": f"{N8N_API_BASE_URL}{video_path}",
            "message": "Video is ready for download",
            "instructions": "Download the video from the download_url provided"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get download URL: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get download URL: {str(e)}")


@app.post("/webhook/test", tags=["N8N Webhooks"])
async def webhook_test(request: Request):
    """
    Test webhook endpoint for N8N
    
    Use this to verify N8N can reach the service.
    """
    body = await request.json() if request.headers.get("content-type") == "application/json" else {}
    
    return {
        "success": True,
        "message": "Webhook test successful!",
        "received": body,
        "timestamp": datetime.now().isoformat(),
        "service": "HunyuanVideo N8N Integration"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting N8N Integration Service on {N8N_WEBHOOK_HOST}:{N8N_WEBHOOK_PORT}")
    logger.info(f"Backend API: {N8N_API_BASE_URL}")
    
    uvicorn.run(
        app,
        host=N8N_WEBHOOK_HOST,
        port=N8N_WEBHOOK_PORT,
        log_level="info",
        access_log=True
    )
