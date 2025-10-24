#!/usr/bin/env python3
"""
Test script to verify LangGraph API endpoints
"""
import requests
import json

def test_langgraph_endpoints():
    """Test various LangGraph API endpoints"""
    
    base_url = "http://127.0.0.1:2024"
    
    print(f"Testing LangGraph server at: {base_url}")
    
    # Test 1: Health check / root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"GET / - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"GET / - Error: {e}")
    
    # Test 2: API docs endpoint
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"GET /docs - Status: {response.status_code}")
    except Exception as e:
        print(f"GET /docs - Error: {e}")
    
    # Test 3: OpenAPI spec
    try:
        response = requests.get(f"{base_url}/openapi.json")
        print(f"GET /openapi.json - Status: {response.status_code}")
        if response.status_code == 200:
            spec = response.json()
            print(f"Available paths: {list(spec.get('paths', {}).keys())}")
    except Exception as e:
        print(f"GET /openapi.json - Error: {e}")
    
    # Test 4: List assistants/graphs
    try:
        response = requests.get(f"{base_url}/assistants")
        print(f"GET /assistants - Status: {response.status_code}")
        if response.status_code == 200:
            assistants = response.json()
            print(f"Available assistants: {assistants}")
    except Exception as e:
        print(f"GET /assistants - Error: {e}")
    
    # Test 5: Try the correct invoke endpoint
    try:
        # The correct endpoint is usually /assistants/{assistant_id}/invoke
        # or /threads/{thread_id}/runs
        test_payload = {
            "input": {
                "query": "test search query",
                "max_results": 3
            }
        }
        
        # Try different possible endpoints
        endpoints_to_try = [
            "/assistants/agent/invoke",
            "/threads/test-thread/runs", 
            "/runs",
            "/invoke",
            "/agent/invoke"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                response = requests.post(
                    f"{base_url}{endpoint}",
                    json=test_payload,
                    headers={"Content-Type": "application/json"}
                )
                print(f"POST {endpoint} - Status: {response.status_code}")
                if response.status_code != 404:
                    print(f"Response: {response.text[:200]}...")
                    break
            except Exception as e:
                print(f"POST {endpoint} - Error: {e}")
    
    except Exception as e:
        print(f"POST test - Error: {e}")

if __name__ == "__main__":
    test_langgraph_endpoints()