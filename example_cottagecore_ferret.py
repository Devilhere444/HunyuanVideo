#!/usr/bin/env python
"""
Example: Generate Cottagecore Ferret Video

This example demonstrates generating the cottagecore ferret video
described in the problem statement using the CPU-optimized API.
"""

import requests
import json
import time

# API configuration
API_URL = "http://localhost:10000"

# Cottagecore ferret video prompt (from problem statement)
COTTAGECORE_PROMPT = """
A whimsical cottagecore ferret habitat with magical fairy kingdom theme. 
Extreme close-up of a ferret wearing a tiny flower crown, sniffing a miniature mushroom. 
Wooden cage with linen bedding, foraging toys, and miniature accessories. 
Ferret exploring burlap sack filled with balls, digging in dried leaves. 
Close-up shots of flower crowns, tiny baskets, miniature mushrooms. 
Ferret tea party with miniature plates and ferret-safe treats.
Warm lighting, natural colors - greens, browns, creams. 
Soft, inviting, whimsical aesthetic. Playful and heartwarming mood.
Detailed textures, miniature accessories, fairy tale magic.
""".strip().replace('\n', ' ')

def generate_cottagecore_ferret_video():
    """Generate the cottagecore ferret video"""
    
    print("="*70)
    print("Cottagecore Ferret Video Generator")
    print("="*70)
    print()
    
    # Configuration for portrait 60-second video
    request_data = {
        "prompt": COTTAGECORE_PROMPT,
        "preset": "portrait_60s",  # 544x960, 9:16 aspect ratio for social media
        "num_inference_steps": 40,  # Higher quality
        "seed": 42  # For reproducibility
    }
    
    print("Video Configuration:")
    print(f"  Prompt: {COTTAGECORE_PROMPT[:100]}...")
    print(f"  Preset: {request_data['preset']}")
    print(f"  Inference Steps: {request_data['num_inference_steps']}")
    print(f"  Seed: {request_data['seed']}")
    print()
    
    # Submit generation request
    print("Step 1: Submitting video generation request...")
    try:
        response = requests.post(
            f"{API_URL}/api/generate",
            json=request_data,
            timeout=30
        )
        response.raise_for_status()
        job_data = response.json()
        
        job_id = job_data["job_id"]
        print(f"✓ Job submitted successfully!")
        print(f"  Job ID: {job_id}")
        print(f"  Status: {job_data['status']}")
        print()
        
    except Exception as e:
        print(f"✗ Failed to submit job: {e}")
        return None
    
    # Wait for completion
    print("Step 2: Waiting for video generation...")
    print("This will take approximately 20-35 minutes on an 8-core CPU...")
    print()
    
    start_time = time.time()
    last_progress = -1
    
    while True:
        try:
            response = requests.get(f"{API_URL}/api/status/{job_id}", timeout=10)
            response.raise_for_status()
            status_data = response.json()
            
            status = status_data["status"]
            progress = status_data["progress"]
            
            # Update progress if changed
            if progress != last_progress:
                elapsed = int(time.time() - start_time)
                minutes = elapsed // 60
                seconds = elapsed % 60
                print(f"  [{minutes:02d}:{seconds:02d}] Status: {status:12} Progress: {progress*100:5.1f}%")
                last_progress = progress
            
            if status == "completed":
                print()
                print("="*70)
                print("✓ Video generation completed!")
                print("="*70)
                total_time = int(time.time() - start_time)
                total_minutes = total_time // 60
                total_seconds = total_time % 60
                print(f"Total time: {total_minutes}m {total_seconds}s")
                print(f"Video URL: {API_URL}{status_data['video_url']}")
                print()
                
                # Download video
                print("Step 3: Downloading video...")
                video_url = f"{API_URL}{status_data['video_url']}"
                output_file = "cottagecore_ferret_video.mp4"
                
                try:
                    response = requests.get(video_url, stream=True, timeout=30)
                    response.raise_for_status()
                    
                    with open(output_file, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    import os
                    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
                    print(f"✓ Video downloaded successfully!")
                    print(f"  Saved to: {output_file}")
                    print(f"  File size: {file_size_mb:.2f} MB")
                    print()
                    print("="*70)
                    print("Video Details:")
                    print("  Resolution: 544x960 (9:16 portrait)")
                    print("  Duration: ~60 seconds (129 frames at 24fps)")
                    print("  Format: MP4")
                    print("  Optimized for: TikTok, Instagram Reels, YouTube Shorts")
                    print("="*70)
                    
                    return output_file
                    
                except Exception as e:
                    print(f"✗ Failed to download video: {e}")
                    return None
                
            elif status == "failed":
                error = status_data.get("error", "Unknown error")
                print()
                print(f"✗ Video generation failed: {error}")
                return None
            
            # Wait before checking again
            time.sleep(10)
            
        except Exception as e:
            print(f"  Warning: {e}")
            time.sleep(10)
            continue
    
    return None


def main():
    print()
    print("This script will generate a cottagecore ferret video as described")
    print("in the problem statement. The video will be:")
    print()
    print("  - Portrait format (544x960, 9:16 aspect ratio)")
    print("  - ~60 seconds long (129 frames at 24fps)")
    print("  - High quality (40 inference steps)")
    print("  - Ready for TikTok, Instagram Reels, YouTube Shorts")
    print()
    print("Expected generation time: 20-35 minutes on 8-core CPU")
    print()
    
    input("Press Enter to start generation, or Ctrl+C to cancel...")
    print()
    
    result = generate_cottagecore_ferret_video()
    
    if result:
        print()
        print("✓ Success! Your cottagecore ferret video is ready!")
        print()
        print("Next steps:")
        print("1. Review the video")
        print("2. Upload to your social media platforms")
        print("3. Add captions and hashtags")
        print()
        print("Suggested caption:")
        print("Cottagecore Ferret Dream! 🍄✨ Learn how to build a tiny,")
        print("mushroom-filled world for your fuzzy friend! DIY toys,")
        print("fairy tale photos, and endless cuteness! #Cottagecore")
        print("#Ferret #FerretLife #DIY #Pets #AnimalLover #CuteAnimals")
        print("#FairyCore #PetEnrichment #ViralReels")
        return 0
    else:
        print()
        print("✗ Failed to generate video. Please check:")
        print("1. API server is running (./start_api.sh)")
        print("2. Models are downloaded to ckpts/ directory")
        print("3. Check API logs for errors")
        return 1


if __name__ == "__main__":
    import sys
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        print("✗ Cancelled by user")
        sys.exit(1)
