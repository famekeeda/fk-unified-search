#!/usr/bin/env python3
"""
Test the correct LangGraph API endpoints
"""
import requests
import json

def test_correct_api():
    """Test the correct LangGraph API usage"""
    
    base_url = "http://127.0.0.1:2024"
    
    print("Testing correct LangGraph API usage...")
    
    # Step 1: Get available assistants
    try:
        response = requests.get(f"{base_url}/assistants")
        print(f"GET /assistants - Status: {response.status_code}")
        
        if response.status_code == 200:
            assistants = response.json()
            print(f"Available assistants: {json.dumps(assistants, indent=2)}")
            
            # If we have assistants, use the first one
            if assistants:
                assistant_id = assistants[0].get('assistant_id', 'agent')
                print(f"Using assistant_id: {assistant_id}")
                
                # Step 2: Create a thread and run
                test_payload = {
                    "assistant_id": assistant_id,
                    "input": {
                        "query": "search for AI news",
                        "max_results": 3
                    }
                }
                
                print(f"Testing with payload: {json.dumps(test_payload, indent=2)}")
                
                # Try the runs endpoint
                response = requests.post(
                    f"{base_url}/runs",
                    json=test_payload,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"POST /runs - Status: {response.status_code}")
                print(f"Response: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"Success! Result: {json.dumps(result, indent=2)}")
                
            else:
                print("No assistants found. Let's try with 'agent' as default.")
                
                # Try with default assistant_id from langgraph.json
                test_payload = {
                    "assistant_id": "agent",
                    "input": {
                        "query": "search for AI news", 
                        "max_results": 3
                    }
                }
                
                response = requests.post(
                    f"{base_url}/runs",
                    json=test_payload,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"POST /runs with 'agent' - Status: {response.status_code}")
                print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

def test_streaming_api():
    """Test the streaming API endpoint"""
    
    base_url = "http://127.0.0.1:2024"
    
    print("\nTesting streaming API...")
    
    test_payload = {
        "assistant_id": "agent",
        "input": {
            "query": "search for Python tutorials",
            "max_results": 2
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/runs/stream",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            stream=True
        )
        
        print(f"POST /runs/stream - Status: {response.status_code}")
        
        if response.status_code == 200:
            print("Streaming response:")
            for line in response.iter_lines():
                if line:
                    print(f"Stream: {line.decode('utf-8')}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Streaming error: {e}")

if __name__ == "__main__":
    test_correct_api()
    test_streaming_api()