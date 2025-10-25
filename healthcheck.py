#!/usr/bin/env python
"""
Simple health check script for HunyuanVideo deployment.
Can be used by monitoring services or load balancers.
"""

import sys
import requests
from loguru import logger

def check_health(url="http://localhost:10000"):
    """
    Check if the Gradio server is responding.
    
    Args:
        url: The URL to check (default: http://localhost:10000)
    
    Returns:
        bool: True if healthy, False otherwise
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            logger.info("Health check passed - service is running")
            return True
        else:
            logger.error(f"Health check failed - status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Health check failed - error: {e}")
        return False

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:10000"
    is_healthy = check_health(url)
    sys.exit(0 if is_healthy else 1)
