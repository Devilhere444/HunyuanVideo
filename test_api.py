#!/usr/bin/env python
"""
Test script for HunyuanVideo API
Run this to verify the API is working correctly
"""

import requests
import time
import sys
from typing import Dict, Any

def test_health_check(base_url: str) -> bool:
    """Test the health check endpoint"""
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed")
            print(f"  Status: {data.get('status')}")
            print(f"  Model loaded: {data.get('model_loaded')}")
            print(f"  Active jobs: {data.get('active_jobs')}")
            return data.get('model_loaded', False)
        else:
            print(f"✗ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False


def test_root_endpoint(base_url: str) -> bool:
    """Test the root endpoint"""
    print("\n=== Testing Root Endpoint ===")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Root endpoint accessible")
            print(f"  API: {data.get('name')}")
            print(f"  Version: {data.get('version')}")
            return True
        else:
            print(f"✗ Root endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Root endpoint error: {e}")
        return False


def test_info_endpoint(base_url: str) -> bool:
    """Test the info endpoint"""
    print("\n=== Testing Info Endpoint ===")
    try:
        response = requests.get(f"{base_url}/api/info", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Info endpoint accessible")
            print(f"  Model: {data.get('model')}")
            print(f"  Deployment: {data.get('deployment')}")
            return True
        else:
            print(f"✗ Info endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Info endpoint error: {e}")
        return False


def test_video_generation(base_url: str, wait_for_completion: bool = False) -> bool:
    """Test video generation"""
    print("\n=== Testing Video Generation ===")
    
    # Submit job
    print("Submitting video generation job...")
    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "prompt": "A cat walks on the grass, realistic style.",
                "width": 480,
                "height": 360,
                "video_length": 13,  # Minimal frames for quick test
                "fps": 8,
                "num_inference_steps": 10  # Minimal steps for quick test
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"✗ Job submission failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
        
        job_data = response.json()
        job_id = job_data.get("job_id")
        print(f"✓ Job submitted successfully")
        print(f"  Job ID: {job_id}")
        print(f"  Status: {job_data.get('status')}")
        
    except Exception as e:
        print(f"✗ Job submission error: {e}")
        return False
    
    # Check status
    print("\nChecking job status...")
    try:
        response = requests.get(f"{base_url}/api/status/{job_id}", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            print(f"✓ Status check successful")
            print(f"  Status: {status_data.get('status')}")
            print(f"  Progress: {status_data.get('progress') * 100:.1f}%")
            
            if wait_for_completion:
                print("\nWaiting for job completion (this may take several minutes)...")
                max_wait = 600  # 10 minutes
                start_time = time.time()
                
                while time.time() - start_time < max_wait:
                    time.sleep(10)
                    response = requests.get(f"{base_url}/api/status/{job_id}", timeout=10)
                    status_data = response.json()
                    status = status_data.get('status')
                    progress = status_data.get('progress', 0) * 100
                    
                    print(f"  Status: {status} - Progress: {progress:.1f}%")
                    
                    if status == "completed":
                        print(f"✓ Video generation completed!")
                        print(f"  Video URL: {base_url}{status_data.get('video_url')}")
                        return True
                    elif status == "failed":
                        print(f"✗ Video generation failed: {status_data.get('error')}")
                        return False
                
                print("⚠ Timeout waiting for completion (job still running)")
                return True
            
            return True
        else:
            print(f"✗ Status check failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Status check error: {e}")
        return False


def test_list_jobs(base_url: str) -> bool:
    """Test listing jobs"""
    print("\n=== Testing List Jobs ===")
    try:
        response = requests.get(f"{base_url}/api/jobs?limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Job list retrieved")
            print(f"  Total jobs: {data.get('total', 0)}")
            return True
        else:
            print(f"✗ List jobs failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ List jobs error: {e}")
        return False


def run_tests(base_url: str, wait_for_completion: bool = False):
    """Run all tests"""
    print(f"\n{'='*60}")
    print(f"HunyuanVideo API Test Suite")
    print(f"Testing: {base_url}")
    print(f"{'='*60}")
    
    results = {}
    
    # Test basic endpoints
    results["root"] = test_root_endpoint(base_url)
    results["health"] = test_health_check(base_url)
    results["info"] = test_info_endpoint(base_url)
    results["list_jobs"] = test_list_jobs(base_url)
    
    # Only test video generation if model is loaded
    if results["health"]:
        results["video_generation"] = test_video_generation(base_url, wait_for_completion)
    else:
        print("\n⚠ Skipping video generation test - model not loaded")
        results["video_generation"] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠ Some tests failed")
        return 1


if __name__ == "__main__":
    # Get base URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:10000"
    
    # Check if we should wait for video completion
    wait = "--wait" in sys.argv
    
    if wait:
        print("Note: Will wait for video generation to complete (may take 5-10 minutes)")
    
    # Run tests
    exit_code = run_tests(base_url, wait_for_completion=wait)
    sys.exit(exit_code)
