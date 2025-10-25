#!/usr/bin/env python
"""
Example client for HunyuanVideo API
Demonstrates how to generate videos and retrieve results
"""

import requests
import time
import argparse
from pathlib import Path


def generate_video(base_url: str, prompt: str, output_file: str, **kwargs):
    """
    Generate a video using the HunyuanVideo API
    
    Args:
        base_url: Base URL of the API (e.g., https://your-app.onrender.com)
        prompt: Text prompt for video generation
        output_file: Path to save the generated video
        **kwargs: Additional parameters (width, height, video_length, fps, etc.)
    """
    
    # Default parameters optimized for CPU
    params = {
        "prompt": prompt,
        "width": 640,
        "height": 480,
        "video_length": 61,
        "fps": 15,
        "num_inference_steps": 30,
        "guidance_scale": 1.0,
        "flow_shift": 7.0,
        "embedded_guidance_scale": 6.0,
        "seed": None
    }
    
    # Override with provided kwargs
    params.update(kwargs)
    
    print(f"\n{'='*60}")
    print("HunyuanVideo API Client")
    print(f"{'='*60}")
    print(f"API URL: {base_url}")
    print(f"Prompt: {prompt}")
    print(f"Resolution: {params['width']}x{params['height']}")
    print(f"Video Length: {params['video_length']} frames")
    print(f"FPS: {params['fps']}")
    print(f"Inference Steps: {params['num_inference_steps']}")
    print(f"{'='*60}\n")
    
    # Step 1: Submit video generation job
    print("Step 1: Submitting video generation job...")
    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json=params,
            timeout=30
        )
        response.raise_for_status()
        job_data = response.json()
        job_id = job_data["job_id"]
        
        print(f"✓ Job submitted successfully!")
        print(f"  Job ID: {job_id}")
        print(f"  Status: {job_data['status']}")
        print(f"  Check status at: {base_url}{job_data['check_status_url']}")
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to submit job: {e}")
        return None
    
    # Step 2: Poll for completion
    print(f"\nStep 2: Waiting for video generation to complete...")
    print("This may take 10-30 minutes on CPU...")
    
    max_wait = 3600  # 1 hour
    start_time = time.time()
    last_progress = -1
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{base_url}/api/status/{job_id}", timeout=10)
            response.raise_for_status()
            status_data = response.json()
            
            status = status_data["status"]
            progress = status_data["progress"]
            
            # Only print if progress changed
            if progress != last_progress:
                elapsed = int(time.time() - start_time)
                print(f"  [{elapsed}s] Status: {status} - Progress: {progress*100:.1f}%")
                last_progress = progress
            
            if status == "completed":
                print(f"\n✓ Video generation completed!")
                print(f"  Total time: {int(time.time() - start_time)} seconds")
                print(f"  Video URL: {base_url}{status_data['video_url']}")
                
                # Step 3: Download video
                print(f"\nStep 3: Downloading video...")
                video_url = f"{base_url}{status_data['video_url']}"
                
                try:
                    response = requests.get(video_url, stream=True, timeout=30)
                    response.raise_for_status()
                    
                    # Save video
                    output_path = Path(output_file)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    file_size_mb = output_path.stat().st_size / (1024 * 1024)
                    print(f"✓ Video downloaded successfully!")
                    print(f"  Saved to: {output_path}")
                    print(f"  File size: {file_size_mb:.2f} MB")
                    
                    return str(output_path)
                    
                except requests.exceptions.RequestException as e:
                    print(f"✗ Failed to download video: {e}")
                    return None
                
            elif status == "failed":
                error = status_data.get("error", "Unknown error")
                print(f"\n✗ Video generation failed!")
                print(f"  Error: {error}")
                return None
            
            # Wait before checking again
            time.sleep(10)
            
        except requests.exceptions.RequestException as e:
            print(f"  Warning: Failed to check status: {e}")
            time.sleep(10)
            continue
    
    print(f"\n⚠ Timeout: Video generation did not complete within {max_wait} seconds")
    print(f"  Job ID: {job_id}")
    print(f"  You can check the status later at: {base_url}/api/status/{job_id}")
    return None


def main():
    parser = argparse.ArgumentParser(description="HunyuanVideo API Client Example")
    
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:10000",
        help="Base URL of the API (default: http://localhost:10000)"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="A cat walks on the grass, realistic style.",
        help="Text prompt for video generation"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="generated_video.mp4",
        help="Output video file path (default: generated_video.mp4)"
    )
    parser.add_argument(
        "--width",
        type=int,
        default=640,
        help="Video width (default: 640)"
    )
    parser.add_argument(
        "--height",
        type=int,
        default=480,
        help="Video height (default: 480)"
    )
    parser.add_argument(
        "--video-length",
        type=int,
        default=61,
        help="Number of frames (default: 61)"
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=15,
        help="Frames per second (default: 15)"
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=30,
        help="Number of inference steps (default: 30)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed (default: random)"
    )
    
    args = parser.parse_args()
    
    # Generate video
    result = generate_video(
        base_url=args.url,
        prompt=args.prompt,
        output_file=args.output,
        width=args.width,
        height=args.height,
        video_length=args.video_length,
        fps=args.fps,
        num_inference_steps=args.steps,
        seed=args.seed
    )
    
    if result:
        print(f"\n{'='*60}")
        print("Success! Video generation completed.")
        print(f"{'='*60}\n")
        return 0
    else:
        print(f"\n{'='*60}")
        print("Failed to generate video.")
        print(f"{'='*60}\n")
        return 1


if __name__ == "__main__":
    exit(main())
