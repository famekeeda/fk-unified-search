#!/usr/bin/env python3
"""
Simple test for async operations without emojis
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_simple_async():
    """Simple test of async node operations"""
    
    print("Testing Async Node Operations")
    print("=" * 50)
    
    try:
        from agent.nodes import (
            policy_node,
            intent_classifier_node,
            google_search_node,
            web_unlocker_node,
            final_processing_node
        )
        
        print("Successfully imported all node functions")
        
        # Test state
        test_state = {
            "query": "test search query",
            "context": {
                "platform": {"ids": [1]},
                "geography": {"influencer": ["US"]}
            },
            "max_results": 3
        }
        
        # Test policy_node (sync)
        print("Testing policy_node...")
        result = policy_node(test_state.copy())
        print(f"policy_node completed: {result.get('query', 'N/A')}")
        
        # Test intent_classifier_node (async)
        print("Testing intent_classifier_node...")
        result = await intent_classifier_node(test_state.copy())
        print(f"intent_classifier_node completed: {result.get('intent', 'N/A')}")
        
        print("All basic async tests passed!")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    success = await test_simple_async()
    
    if success:
        print("\nSUCCESS: Async operations working correctly!")
    else:
        print("\nFAILED: Async operations have issues")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)