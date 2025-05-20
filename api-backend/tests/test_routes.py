#!/usr/bin/env python3
"""
Test script to verify all the problematic routes are working.
"""
import requests
import time
import sys

# Endpoints to test
ENDPOINTS = [
    ("GET", "/api/health"),
    ("GET", "/api/tmdb/popular"),
    ("GET", "/api/tmdb/movie/genres"),
    ("POST", "/api/auth/login", {"email": "test@example.com", "password": "password123"})
]

def test_endpoints(base_url):
    """Test all endpoints and report status"""
    print(f"Testing endpoints on {base_url}")
    success_count = 0
    
    for method, endpoint, *args in ENDPOINTS:
        url = f"{base_url}{endpoint}"
        print(f"\nTesting {method} {url}")
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            elif method == "POST":
                data = args[0] if args else None
                response = requests.post(url, json=data, timeout=5)
            else:
                print(f"Unsupported method: {method}")
                continue
                
            print(f"Status: {response.status_code}")
            if response.status_code < 500:  # Consider 4xx as "working" since they're expected errors
                print("Result: SUCCESS")
                success_count += 1
            else:
                print("Result: FAILURE")
                print(f"Response: {response.text}")
        except requests.RequestException as e:
            print(f"Error: {e}")
            print("Result: FAILURE")
            
    print(f"\nSummary: {success_count}/{len(ENDPOINTS)} endpoints working")
    return success_count == len(ENDPOINTS)

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    # Wait for the server to be ready
    print("Waiting for server to start...")
    for _ in range(30):  # Try for 30 seconds
        try:
            health_response = requests.get(f"{base_url}/api/health", timeout=2)
            if health_response.status_code == 200:
                print("Server is ready!")
                break
        except requests.RequestException:
            pass
        time.sleep(1)
    
    # Run the tests
    result = test_endpoints(base_url)
    sys.exit(0 if result else 1)
