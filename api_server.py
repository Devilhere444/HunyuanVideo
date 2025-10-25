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
job_queue = {}
executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)


class VideoGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for video generation", example="A cat walks on the grass, realistic style.")
    width: int = Field(default=640, description="Video width in pixels", ge=256, le=1280)
    height: int = Field(default=480, description="Video height in pixels", ge=256, le=1280)
    video_length: int = Field(default=61, description="Number of frames (60 sec at 15fps = 900 frames, but we'll use 61 for compatibility)", ge=13, le=129)
    fps: int = Field(default=15, description="Frames per second", ge=8, le=30)
    seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")
    num_inference_steps: int = Field(default=30, description="Number of denoising steps (lower=faster)", ge=10, le=50)
    guidance_scale: float = Field(default=1.0, description="Guidance scale for generation", ge=1.0, le=20.0)
    flow_shift: float = Field(default=7.0, description="Flow shift parameter", ge=0.0, le=10.0)
    embedded_guidance_scale: float = Field(default=6.0, description="Embedded guidance scale", ge=1.0, le=20.0)


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
    global model_sampler
    
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
        raise


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
    """Initialize model on startup"""
    try:
        initialize_model()
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        # Don't fail startup - allow healthcheck to indicate unhealthy state


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
            "generate": "/api/generate",
            "status": "/api/status/{job_id}",
            "video": "/api/videos/{filename}",
            "jobs": "/api/jobs"
        }
    }


@app.get("/health", tags=["General"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if model_sampler is not None else "initializing",
        "model_loaded": model_sampler is not None,
        "active_jobs": len([j for j in job_queue.values() if j["status"] in ["queued", "processing"]]),
        "total_jobs": len(job_queue)
    }


@app.post("/api/generate", response_model=JobResponse, tags=["Video Generation"])
async def generate_video(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit a video generation job
    
    Returns a job ID that can be used to check status and retrieve the video
    """
    if model_sampler is None:
        raise HTTPException(status_code=503, detail="Model not initialized yet. Please try again in a few moments.")
    
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


@app.get("/api/info", tags=["General"])
async def get_info():
    """
    Get API information and supported parameters
    """
    return {
        "model": "HunyuanVideo",
        "deployment": "CPU-optimized for Render.com",
        "supported_resolutions": {
            "low": "480x360 (4:3)",
            "medium": "640x480 (4:3)",
            "high": "960x544 (16:9)",
            "recommended": "640x480 for CPU deployment"
        },
        "video_length": {
            "min_frames": 13,
            "max_frames": 129,
            "recommended_60sec_15fps": 61,
            "note": "Lower frame counts generate faster on CPU"
        },
        "fps_options": [8, 15, 24, 30],
        "inference_steps": {
            "min": 10,
            "max": 50,
            "recommended_cpu": 30,
            "note": "Lower steps = faster generation but lower quality"
        },
        "estimated_generation_time": {
            "30_steps_cpu": "10-15 minutes",
            "50_steps_cpu": "15-25 minutes",
            "note": "Times vary based on resolution and server load"
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
