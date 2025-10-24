#!/usr/bin/env python3
"""
Start LangGraph server with blocking operations allowed
"""
import subprocess
import sys
import os

def start_server():
    """Start the LangGraph server with proper configuration"""
    
    print("Starting LangGraph server with blocking operations allowed...")
    print("Server will be available at: http://127.0.0.1:2024")
    print("API Documentation: http://127.0.0.1:2024/docs")
    print("")
    print("Correct API endpoints:")
    print("- POST /runs (non-streaming)")
    print("- POST /runs/stream (streaming)")
    print("")
    print("Example payload:")
    print("""{
  "assistant_id": "agent",
  "input": {
    "query": "your search query",
    "max_results": 5
  }
}""")
    print("")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Start the server with blocking operations allowed
        subprocess.run([
            "langgraph", "dev", 
            "--allow-blocking",
            "--port", "2024"
        ], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
    except FileNotFoundError:
        print("Error: langgraph command not found. Make sure it's installed.")
        print("Try: pip install langgraph-cli")

if __name__ == "__main__":
    start_server()