#!/usr/bin/env python3
"""
Test script to verify the import fix works
"""

def test_imports():
    """Test the problematic imports"""
    try:
        print("Testing langchain.globals import...")
        from langchain.globals import set_debug
        print("✓ langchain.globals import successful")
        
        print("Testing mcp_use.client import...")
        from mcp_use.client import MCPClient
        print("✓ mcp_use.client import successful")
        
        print("Testing agent.nodes import...")
        from agent.nodes import policy_node
        print("✓ agent.nodes import successful")
        
        print("\n🎉 All imports successful! The fix worked.")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    test_imports()