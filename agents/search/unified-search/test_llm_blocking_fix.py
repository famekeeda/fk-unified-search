#!/usr/bin/env python3
"""
Specific test for LLM blocking operations fix
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_llm_creation_and_usage():
    """Test LLM creation and usage for blocking operations"""
    print("Testing LLM creation and usage...")
    
    try:
        from agent.nodes import get_cached_llm, create_llm_with_preinitialized_client
        
        # Test 1: Create LLM with pre-initialized client
        print("  1. Creating LLM with pre-initialized client...")
        llm = await create_llm_with_preinitialized_client("gemini-2.0-flash", 0.0)
        print("     ✅ LLM created successfully")
        
        # Test 2: Use cached LLM
        print("  2. Getting cached LLM...")
        cached_llm = await get_cached_llm("gemini-2.0-flash", 0.0)
        print("     ✅ Cached LLM retrieved successfully")
        
        # Test 3: Invoke LLM (this is where the io.TextIOWrapper.read error occurred)
        print("  3. Invoking LLM (critical test for io.TextIOWrapper.read error)...")
        response = await llm.ainvoke("Hello, this is a test message. Please respond briefly.")
        print(f"     ✅ LLM invocation successful: {response.content[:50]}...")
        
        # Test 4: Multiple invocations to test stability
        print("  4. Testing multiple invocations...")
        for i in range(3):
            response = await cached_llm.ainvoke(f"Test message {i+1}")
            print(f"     ✅ Invocation {i+1} successful")
        
        return True
        
    except Exception as e:
        print(f"     ❌ LLM test failed: {e}")
        if "Blocking call to io.TextIOWrapper.read" in str(e):
            print("     🔍 SPECIFIC ERROR: io.TextIOWrapper.read blocking call detected!")
            print("     💡 This indicates the LangChain Google GenAI library is still doing file reads")
        elif "Blocking call" in str(e):
            print(f"     🔍 BLOCKING OPERATION: {e}")
        
        import traceback
        traceback.print_exc()
        return False

async def test_structured_output():
    """Test structured output creation and usage"""
    print("\\nTesting structured output...")
    
    try:
        from agent.nodes import get_cached_llm
        from pydantic import BaseModel, Field
        
        class TestOutput(BaseModel):
            message: str = Field(description="A test message")
            confidence: float = Field(description="Confidence score")
        
        # Test structured output creation
        print("  1. Creating structured LLM...")
        llm = await get_cached_llm("gemini-2.0-flash", 0.0)
        
        # This is where with_structured_output might cause blocking
        print("  2. Creating structured output (potential blocking point)...")
        structured_llm = await asyncio.to_thread(lambda: llm.with_structured_output(TestOutput))
        print("     ✅ Structured output created successfully")
        
        # Test structured invocation
        print("  3. Invoking structured LLM...")
        result = await structured_llm.ainvoke("Generate a test message with confidence 0.95")
        print(f"     ✅ Structured invocation successful: {result.message}")
        
        return True
        
    except Exception as e:
        print(f"     ❌ Structured output test failed: {e}")
        if "Blocking call" in str(e):
            print(f"     🔍 BLOCKING OPERATION: {e}")
        return False

async def main():
    """Main test function"""
    print("LLM Blocking Operations Fix Test")
    print("=" * 50)
    print("Testing the fix for 'Blocking call to io.TextIOWrapper.read'")
    print()
    
    # Test LLM creation and usage
    llm_success = await test_llm_creation_and_usage()
    
    # Test structured output
    structured_success = await test_structured_output()
    
    # Summary
    print("\\n" + "=" * 50)
    print("TEST RESULTS:")
    
    if llm_success and structured_success:
        print("🎉 ALL LLM TESTS PASSED!")
        print("✅ No 'io.TextIOWrapper.read' blocking operations detected")
        print("✅ LLM creation and invocation working correctly")
        print("✅ Structured output working correctly")
        print("\\n🚀 The LangChain Google GenAI blocking issue is RESOLVED!")
    else:
        print("⚠️  SOME LLM TESTS FAILED")
        if not llm_success:
            print("❌ LLM creation/invocation issues detected")
        if not structured_success:
            print("❌ Structured output issues detected")
        print("\\n🔧 Recommendation: Use start_server_blocking_safe.py")
        print("   This handles deep library blocking operations")
    
    print("\\n📝 For production deployment:")
    print("   Option 1: python start_server_blocking_safe.py (recommended)")
    print("   Option 2: BG_JOB_ISOLATED_LOOPS=true langgraph deploy")

if __name__ == "__main__":
    asyncio.run(main())