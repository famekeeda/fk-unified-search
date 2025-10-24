#!/usr/bin/env python3
"""
Start LangGraph server with blocking operations allowed to fix MCP issues
"""
import subprocess
import sys
import os

def start_server_with_blocking():
    """Start the LangGraph server with blocking operations allowed"""
    
    print("🚀 Starting LangGraph server with blocking operations allowed...")
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
    print("⚠️  Note: Running with --allow-blocking to fix MCP connection issues")
    print("🔧 This allows synchronous operations that would otherwise fail")
    print("")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Start the server with blocking operations allowed
        subprocess.run([
            "langgraph", "dev", 
            "--allow-blocking",  # This fixes the MCP blocking operations
            "--port", "2024",
            "--host", "127.0.0.1"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
    except FileNotFoundError:
        print("❌ Error: langgraph command not found.")
        print("💡 Try: pip install langgraph-cli")

if __name__ == "__main__":
    start_server_with_blocking()