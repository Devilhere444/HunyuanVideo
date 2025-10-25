#!/usr/bin/env python
"""
FastAPI REST API server for HunyuanVideo
Optimized for CPU-only deployment on Render.com
"""

import os
import uuid
import time
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor
import json

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from loguru import logger
import threading

from hyvideo.utils.file_utils import save_videos_grid
from hyvideo.config import parse_args
from hyvideo.inference import HunyuanVideoSampler

# Configuration
MODEL_BASE = os.getenv("MODEL_BASE", "/app/ckpts")
SAVE_PATH = os.getenv("SAVE_PATH", "/app/results")
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "2"))

# Initialize FastAPI app
app = FastAPI(
    title="HunyuanVideo API",
    description="CPU-optimized video generation API for HunyuanVideo on Render.com",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
model_sampler = None
model_init_lock = threading.Lock()
model_init_error = None
job_queue = {}
executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)


class VideoGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for video generation", example="A cat walks on the grass, realistic style.")
    width: int = Field(default=544, description="Video width in pixels (portrait: 544, landscape: 960)", ge=256, le=1280)
    height: int = Field(default=960, description="Video height in pixels (portrait: 960, landscape: 544)", ge=256, le=1280)
    video_length: int = Field(default=129, description="Number of frames (60 sec at 24fps = 1440, but we use 129 for CPU compatibility)", ge=13, le=129)
    fps: int = Field(default=24, description="Frames per second (24 recommended for quality)", ge=8, le=30)
    seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")
    num_inference_steps: int = Field(default=30, description="Number of denoising steps (lower=faster, 30-50 recommended)", ge=10, le=50)
    guidance_scale: float = Field(default=1.0, description="Guidance scale for generation", ge=1.0, le=20.0)
    flow_shift: float = Field(default=7.0, description="Flow shift parameter", ge=0.0, le=10.0)
    embedded_guidance_scale: float = Field(default=6.0, description="Embedded guidance scale", ge=1.0, le=20.0)
    preset: Optional[str] = Field(default=None, description="Preset configurations: 'portrait_60s', 'landscape_60s', 'portrait_30s', 'landscape_30s'", example="portrait_60s")


class JobStatus(BaseModel):
    job_id: str
    status: str  # queued, processing, completed, failed
    progress: float  # 0.0 to 1.0
    created_at: str
    updated_at: str
    video_url: Optional[str] = None
    error: Optional[str] = None
    estimated_time: Optional[int] = None  # seconds


class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str
    check_status_url: str


def initialize_model():
    """Initialize the HunyuanVideo model with CPU-optimized settings"""
    global model_sampler, model_init_error
    
    try:
        logger.info("Initializing HunyuanVideo model with CPU optimizations...")
        
        # Set environment variables and parse args
        # parse_args will read from sys.argv by default
        import sys
        original_argv = sys.argv.copy()
        
        # Build command-line arguments for CPU optimization
        sys.argv = [
            "api_server.py",
            "--model-base", MODEL_BASE,
            "--save-path", SAVE_PATH,
            "--precision", "fp32",  # CPU works better with fp32
            "--use-cpu-offload",
            "--flow-reverse"
        ]
        
        args = parse_args()
        
        # Restore original argv
        sys.argv = original_argv
        
        models_root_path = Path(MODEL_BASE)
        
        if not models_root_path.exists():
            logger.error(f"Model directory not found: {models_root_path}")
            raise ValueError(f"Model directory not exists: {models_root_path}")
        
        # Create save directory
        os.makedirs(SAVE_PATH, exist_ok=True)
        
        model_sampler = HunyuanVideoSampler.from_pretrained(models_root_path, args=args)
        logger.info("Model initialized successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize model: {e}")
        model_init_error = str(e)
        raise


def ensure_model_initialized():
    """Ensure model is initialized, initializing it on-demand if needed"""
    global model_sampler, model_init_error
    
    # Fast path: model already initialized
    if model_sampler is not None:
        return
    
    # Check if previous initialization failed
    if model_init_error is not None:
        raise HTTPException(
            status_code=503,
            detail=f"Model initialization failed: {model_init_error}. Please check logs and restart the service."
        )
    
    # Thread-safe initialization
    with model_init_lock:
        # Double-check after acquiring lock
        if model_sampler is not None:
            return
        
        if model_init_error is not None:
            raise HTTPException(
                status_code=503,
                detail=f"Model initialization failed: {model_init_error}. Please check logs and restart the service."
            )
        
        # Initialize model on first request
        logger.info("First request received, initializing model on-demand...")
        try:
            initialize_model()
        except Exception as e:
            model_init_error = str(e)
            raise HTTPException(
                status_code=503,
                detail=f"Failed to initialize model on demand: {str(e)}"
            )


def apply_preset(request: VideoGenerationRequest) -> VideoGenerationRequest:
    """Apply preset configurations for common use cases"""
    if request.preset == "portrait_60s":
        # 9:16 portrait, ~60 seconds
        request.width = 544
        request.height = 960
        request.video_length = 129  # Max frames for CPU
        request.fps = 24
        request.num_inference_steps = 30
    elif request.preset == "portrait_30s":
        # 9:16 portrait, ~30 seconds
        request.width = 544
        request.height = 960
        request.video_length = 65
        request.fps = 24
        request.num_inference_steps = 30
    elif request.preset == "landscape_60s":
        # 16:9 landscape, ~60 seconds
        request.width = 960
        request.height = 544
        request.video_length = 129
        request.fps = 24
        request.num_inference_steps = 30
    elif request.preset == "landscape_30s":
        # 16:9 landscape, ~30 seconds
        request.width = 960
        request.height = 544
        request.video_length = 65
        request.fps = 24
        request.num_inference_steps = 30
    return request


def generate_video_task(job_id: str, request: VideoGenerationRequest):
    """Background task to generate video"""
    global job_queue
    
    try:
        # Update job status to processing
        job_queue[job_id]["status"] = "processing"
        job_queue[job_id]["progress"] = 0.1
        job_queue[job_id]["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"Starting video generation for job {job_id}")
        
        # Generate video
        outputs = model_sampler.predict(
            prompt=request.prompt,
            height=request.height,
            width=request.width,
            video_length=request.video_length,
            seed=request.seed,
            negative_prompt="",
            infer_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
            num_videos_per_prompt=1,
            flow_shift=request.flow_shift,
            batch_size=1,
            embedded_guidance_scale=request.embedded_guidance_scale
        )
        
        job_queue[job_id]["progress"] = 0.8
        job_queue[job_id]["updated_at"] = datetime.now().isoformat()
        
        # Save video
        samples = outputs['samples']
        sample = samples[0].unsqueeze(0)
        
        video_filename = f"{job_id}.mp4"
        video_path = os.path.join(SAVE_PATH, video_filename)
        
        save_videos_grid(sample, video_path, fps=request.fps)
        
        # Update job status to completed
        job_queue[job_id]["status"] = "completed"
        job_queue[job_id]["progress"] = 1.0
        job_queue[job_id]["video_url"] = f"/api/videos/{video_filename}"
        job_queue[job_id]["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"Video generation completed for job {job_id}: {video_path}")
        
    except Exception as e:
        logger.error(f"Video generation failed for job {job_id}: {e}")
        job_queue[job_id]["status"] = "failed"
        job_queue[job_id]["error"] = str(e)
        job_queue[job_id]["updated_at"] = datetime.now().isoformat()


@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup but defer model loading"""
    try:
        logger.info("API server starting up...")
        logger.info(f"Model base path: {MODEL_BASE}")
        logger.info(f"Save path: {SAVE_PATH}")
        
        # Create necessary directories
        os.makedirs(SAVE_PATH, exist_ok=True)
        
        # Check if model directory exists
        models_root_path = Path(MODEL_BASE)
        if not models_root_path.exists():
            logger.warning(f"Model directory not found: {models_root_path}")
            logger.warning("Models will need to be downloaded before video generation can work")
        else:
            logger.info(f"Model directory found: {models_root_path}")
        
        logger.info("Startup complete. Model will be initialized on first request to save memory.")
        
    except Exception as e:
        logger.error(f"Startup configuration check failed: {e}")
        # Don't fail startup - allow service to start and show proper error messages


@app.get("/", tags=["General"])
async def root():
    """API root endpoint"""
    return {
        "name": "HunyuanVideo API",
        "version": "1.0.0",
        "status": "running",
        "description": "CPU-optimized video generation API",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "warmup": "/api/warmup",
            "generate": "/api/generate",
            "status": "/api/status/{job_id}",
            "video": "/api/videos/{filename}",
            "jobs": "/api/jobs"
        },
        "note": "Models are loaded on-demand to save memory. Use /api/warmup to pre-load models."
    }


@app.get("/health", tags=["General"])
async def health_check():
    """Health check endpoint"""
    is_ready = model_sampler is not None
    has_error = model_init_error is not None
    
    status = "healthy" if is_ready else ("error" if has_error else "initializing")
    
    response = {
        "status": status,
        "model_loaded": is_ready,
        "active_jobs": len([j for j in job_queue.values() if j["status"] in ["queued", "processing"]]),
        "total_jobs": len(job_queue)
    }
    
    if has_error:
        response["error"] = model_init_error
        response["message"] = "Model initialization failed. Please check logs."
    elif not is_ready:
        response["message"] = "Model will be loaded on first request to save memory during startup."
    
    return response


@app.post("/api/generate", response_model=JobResponse, tags=["Video Generation"])
async def generate_video(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit a video generation job
    
    Returns a job ID that can be used to check status and retrieve the video
    """
    # Ensure model is initialized before accepting requests
    ensure_model_initialized()
    
    # Apply preset if specified
    request = apply_preset(request)
    
    # Create unique job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job status
    job_queue[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0.0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "request": request.dict(),
        "video_url": None,
        "error": None,
        "estimated_time": request.num_inference_steps * 20  # Rough estimate: 20 seconds per step on CPU
    }
    
    # Add background task
    background_tasks.add_task(generate_video_task, job_id, request)
    
    logger.info(f"Video generation job created: {job_id}")
    
    return JobResponse(
        job_id=job_id,
        status="queued",
        message="Video generation job submitted successfully",
        check_status_url=f"/api/status/{job_id}"
    )


@app.get("/api/status/{job_id}", response_model=JobStatus, tags=["Video Generation"])
async def get_job_status(job_id: str):
    """
    Get the status of a video generation job
    
    Returns current status, progress, and video URL when completed
    """
    if job_id not in job_queue:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = job_queue[job_id]
    
    return JobStatus(
        job_id=job["job_id"],
        status=job["status"],
        progress=job["progress"],
        created_at=job["created_at"],
        updated_at=job["updated_at"],
        video_url=job.get("video_url"),
        error=job.get("error"),
        estimated_time=job.get("estimated_time")
    )


@app.get("/api/videos/{filename}", tags=["Video Generation"])
async def get_video(filename: str):
    """
    Download a generated video
    
    Returns the video file for download
    """
    video_path = os.path.join(SAVE_PATH, filename)
    
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=filename
    )


@app.get("/api/jobs", tags=["Video Generation"])
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by status: queued, processing, completed, failed"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of jobs to return")
):
    """
    List all video generation jobs
    
    Optionally filter by status and limit results
    """
    jobs = list(job_queue.values())
    
    # Filter by status if provided
    if status:
        jobs = [j for j in jobs if j["status"] == status]
    
    # Sort by created_at (newest first)
    jobs.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Limit results
    jobs = jobs[:limit]
    
    return {
        "total": len(jobs),
        "jobs": jobs
    }


@app.delete("/api/jobs/{job_id}", tags=["Video Generation"])
async def delete_job(job_id: str):
    """
    Delete a job and its associated video file
    
    Note: Cannot delete jobs that are currently processing
    """
    if job_id not in job_queue:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = job_queue[job_id]
    
    if job["status"] == "processing":
        raise HTTPException(status_code=400, detail="Cannot delete job that is currently processing")
    
    # Delete video file if it exists
    if job.get("video_url"):
        filename = job["video_url"].split("/")[-1]
        video_path = os.path.join(SAVE_PATH, filename)
        if os.path.exists(video_path):
            os.remove(video_path)
            logger.info(f"Deleted video file: {video_path}")
    
    # Remove from job queue
    del job_queue[job_id]
    
    logger.info(f"Deleted job: {job_id}")
    
    return {"message": "Job deleted successfully", "job_id": job_id}


@app.post("/api/warmup", tags=["General"])
async def warmup_model():
    """
    Pre-load the model to warm up the service
    
    This endpoint can be called to load the model into memory before making
    actual video generation requests. Useful for reducing latency on the first request.
    
    Returns the current model status after attempting to load.
    """
    try:
        ensure_model_initialized()
        return {
            "status": "success",
            "message": "Model is loaded and ready",
            "model_loaded": True
        }
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "status": "error",
                "message": e.detail,
                "model_loaded": False
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "model_loaded": False
            }
        )


@app.get("/api/info", tags=["General"])
async def get_info():
    """
    Get API information and supported parameters
    """
    return {
        "model": "HunyuanVideo",
        "deployment": "CPU-optimized (8 cores, 32GB RAM)",
        "presets": {
            "portrait_60s": "544x960 (9:16), ~60 seconds, 24fps",
            "portrait_30s": "544x960 (9:16), ~30 seconds, 24fps",
            "landscape_60s": "960x544 (16:9), ~60 seconds, 24fps",
            "landscape_30s": "960x544 (16:9), ~30 seconds, 24fps"
        },
        "supported_resolutions": {
            "portrait_9_16": "544x960 (Recommended for TikTok, Instagram Reels)",
            "landscape_16_9": "960x544 (Recommended for YouTube, TV)",
            "custom": "256-1280 width/height, must be divisible by 8"
        },
        "video_length": {
            "min_frames": 13,
            "max_frames": 129,
            "recommended_60sec": "129 frames at 24fps",
            "note": "Frame count must be 4n+1 for VAE compatibility"
        },
        "fps_options": [8, 15, 24, 30],
        "inference_steps": {
            "min": 10,
            "max": 50,
            "recommended_cpu": 30,
            "quality": "30-40 steps for good quality, 40-50 for best quality",
            "note": "Lower steps = faster generation but lower quality"
        },
        "estimated_generation_time": {
            "30_steps_portrait_60s": "15-25 minutes on 8-core CPU",
            "30_steps_landscape_60s": "15-25 minutes on 8-core CPU",
            "40_steps_portrait_60s": "20-35 minutes on 8-core CPU",
            "note": "Times vary based on resolution and CPU performance"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "10000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting HunyuanVideo API server on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )
