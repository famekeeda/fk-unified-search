#!/usr/bin/env python3
"""
Start LangGraph server with blocking operations allowed.

This script handles the deep blocking operations in LangChain Google GenAI
that occur when the library reads metadata files during client initialization.
"""
import subprocess
import sys
import os

def main():
    """Start the LangGraph server with blocking operations allowed."""
    
    print("🚀 Starting LangGraph Server with Blocking Operations Support")
    print("=" * 60)
    print()
    print("This server allows blocking operations to handle:")
    print("- LangChain Google GenAI metadata file reads")
    print("- MCP client subprocess management")
    print("- Deep library file system operations")
    print()
    print("All application-level operations are still async-optimized!")
    print()
    
    # Set environment variables for better performance
    env = os.environ.copy()
    env.update({
        "PYTHONUNBUFFERED": "1",
        "LANGCHAIN_TRACING_V2": "false",  # Disable tracing to reduce I/O
        "LANGCHAIN_ENDPOINT": "",
        "LANGCHAIN_API_KEY": "",
    })
    
    try:
        # Start LangGraph dev server with blocking operations allowed
        cmd = [
            sys.executable, "-m", "langgraph", "dev", 
            "--allow-blocking",
            "--host", "0.0.0.0",
            "--port", "8123"
        ]
        
        print(f"Executing: {' '.join(cmd)}")
        print("=" * 60)
        
        # Run the server
        result = subprocess.run(cmd, env=env, cwd=os.path.dirname(__file__))
        
        return result.returncode
        
    except KeyboardInterrupt:
        print("\\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)