#!/usr/bin/env python3
"""
Start LangGraph server with async operations (no blocking flag needed)
"""
import subprocess
import sys
import os

def start_server_async():
    """Start the LangGraph server with proper async operations"""
    
    print("🚀 Starting LangGraph server with async operations...")
    print("📍 Server will be available at: http://127.0.0.1:2024")
    print("📚 API Documentation: http://127.0.0.1:2024/docs")
    print("")
    print("✅ Correct API endpoints:")
    print("   - POST /runs (non-streaming)")
    print("   - POST /runs/stream (streaming)")
    print("")
    print("📋 Example payload:")
    print("""{
  "assistant_id": "agent",
  "input": {
    "query": "your search query",
    "max_results": 5
  }
}""")
    print("")
    print("🔧 Note: Using async/await patterns - no --allow-blocking needed!")
    print("⚡ All blocking operations converted to asyncio.to_thread()")
    print("")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Start the server without blocking flag - async operations should work now
        subprocess.run([
            "langgraph", "dev", 
            "--port", "2024",
            "--host", "127.0.0.1"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        print("💡 If you still see blocking operation errors, use start_server_with_blocking.py as fallback")
    except FileNotFoundError:
        print("❌ Error: langgraph command not found.")
        print("💡 Try: pip install langgraph-cli")

if __name__ == "__main__":
    start_server_async()