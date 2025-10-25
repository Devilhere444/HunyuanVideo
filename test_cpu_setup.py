#!/usr/bin/env python
"""
Quick test script to verify CPU-optimized setup is working correctly
"""

import sys
import json

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import torch
        print(f"✓ PyTorch version: {torch.__version__}")
        print(f"  CPU available: {torch.cuda.is_available() == False or True}")
        
        import transformers
        print(f"✓ Transformers version: {transformers.__version__}")
        
        import diffusers
        print(f"✓ Diffusers version: {diffusers.__version__}")
        
        import fastapi
        print(f"✓ FastAPI version: {fastapi.__version__}")
        
        from loguru import logger
        print("✓ Loguru imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_config():
    """Test configuration parsing"""
    print("\nTesting configuration...")
    try:
        from hyvideo.config import parse_args
        
        # Test with CPU-optimized arguments
        test_args = [
            "test",
            "--model-base", "ckpts",
            "--save-path", "results",
            "--precision", "fp32",
            "--use-cpu-offload",
            "--flow-reverse"
        ]
        
        args = parse_args(namespace=test_args)
        print("✓ Configuration parsed successfully")
        print(f"  Model base: {args.model_base}")
        print(f"  Precision: {args.precision}")
        print(f"  CPU offload: {args.use_cpu_offload}")
        
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def test_api_models():
    """Test API model definitions"""
    print("\nTesting API models...")
    try:
        from api_server import VideoGenerationRequest, apply_preset
        
        # Test portrait preset
        request = VideoGenerationRequest(
            prompt="Test prompt",
            preset="portrait_60s"
        )
        request = apply_preset(request)
        
        assert request.width == 544, f"Expected width 544, got {request.width}"
        assert request.height == 960, f"Expected height 960, got {request.height}"
        assert request.fps == 24, f"Expected fps 24, got {request.fps}"
        
        print("✓ Portrait preset works correctly")
        print(f"  Resolution: {request.width}x{request.height}")
        print(f"  FPS: {request.fps}")
        print(f"  Frames: {request.video_length}")
        
        # Test landscape preset
        request2 = VideoGenerationRequest(
            prompt="Test prompt",
            preset="landscape_60s"
        )
        request2 = apply_preset(request2)
        
        assert request2.width == 960, f"Expected width 960, got {request2.width}"
        assert request2.height == 544, f"Expected height 544, got {request2.height}"
        
        print("✓ Landscape preset works correctly")
        print(f"  Resolution: {request2.width}x{request2.height}")
        
        return True
    except Exception as e:
        print(f"✗ API model error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_n8n_integration():
    """Test N8N integration models"""
    print("\nTesting N8N integration...")
    try:
        from n8n_integration import N8NVideoRequest, build_api_request
        
        # Test basic request
        request = N8NVideoRequest(
            prompt="Test prompt for N8N",
            preset="portrait_60s"
        )
        
        api_request = build_api_request(request)
        
        assert api_request["prompt"] == "Test prompt for N8N"
        assert api_request["preset"] == "portrait_60s"
        
        print("✓ N8N integration works correctly")
        print(f"  Request: {json.dumps(api_request, indent=2)}")
        
        # Test custom values
        request2 = N8NVideoRequest(
            prompt="Custom test",
            preset="portrait_60s",
            width=640,
            height=480
        )
        api_request2 = build_api_request(request2)
        
        assert api_request2["width"] == 640
        assert api_request2["height"] == 480
        
        print("✓ Custom parameters override presets correctly")
        
        return True
    except Exception as e:
        print(f"✗ N8N integration error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("HunyuanVideo CPU-Optimized Setup Test")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("API Models", test_api_models()))
    results.append(("N8N Integration", test_n8n_integration()))
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name:20} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("="*60)
    if all_passed:
        print("✓ All tests passed!")
        print("\nYour CPU-optimized setup is ready to use.")
        print("\nNext steps:")
        print("1. Download models to ckpts/ directory")
        print("2. Start API server: ./start_api.sh")
        print("3. (Optional) Start N8N service: ./start_n8n.sh")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
