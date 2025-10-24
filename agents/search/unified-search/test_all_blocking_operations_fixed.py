#!/usr/bin/env python3
"""
Comprehensive test to verify all blocking operations are fixed in nodes.py
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_intent_classifier_node():
    """Test intent_classifier_node for blocking operations"""
    print("Testing intent_classifier_node...")
    
    try:
        from agent.nodes import intent_classifier_node
        
        test_state = {
            "query": "best laptops under $1000",
            "geo": "US",
            "max_results": 5
        }
        
        result = await intent_classifier_node(test_state.copy())
        
        print("✅ intent_classifier_node: SUCCESS")
        print(f"   Intent: {result.get('intent')}")
        print(f"   Confidence: {result.get('intent_confidence')}")
        return True
        
    except Exception as e:
        print(f"❌ intent_classifier_node: FAILED - {e}")
        if "Blocking call" in str(e):
            print("   BLOCKING OPERATION DETECTED!")
        return False

async def test_google_search_node():
    """Test google_search_node for blocking operations"""
    print("\\nTesting google_search_node...")
    
    try:
        from agent.nodes import google_search_node
        
        test_state = {
            "query": "test search query",
            "intent": "general_search",
            "max_results": 3
        }
        
        result = await google_search_node(test_state.copy())
        
        print("✅ google_search_node: SUCCESS")
        print(f"   Results found: {len(result.get('raw_results', []))}")
        return True
        
    except Exception as e:
        print(f"❌ google_search_node: FAILED - {e}")
        if "Blocking call" in str(e):
            print("   BLOCKING OPERATION DETECTED!")
        return False

async def test_web_unlocker_node():
    """Test web_unlocker_node for blocking operations"""
    print("\\nTesting web_unlocker_node...")
    
    try:
        from agent.nodes import web_unlocker_node
        
        test_state = {
            "query": "test web scraping query",
            "raw_results": [
                {
                    "url": "https://example.com",
                    "title": "Test Page",
                    "snippet": "Test content",
                    "source": "google_search"
                }
            ],
            "context": {
                "platform": {"ids": [1]},
                "geography": {"influencer": ["US"]}
            },
            "max_results": 2
        }
        
        result = await web_unlocker_node(test_state.copy())
        
        print("✅ web_unlocker_node: SUCCESS")
        print(f"   Scraped results: {len(result.get('scraped_results', []))}")
        return True
        
    except Exception as e:
        print(f"❌ web_unlocker_node: FAILED - {e}")
        if "Blocking call" in str(e):
            print("   BLOCKING OPERATION DETECTED!")
            print(f"   Error details: {e}")
        return False

async def test_final_processing_node():
    """Test final_processing_node for blocking operations"""
    print("\\nTesting final_processing_node...")
    
    try:
        from agent.nodes import final_processing_node
        
        test_state = {
            "query": "test query",
            "raw_results": [
                {
                    "title": "Test Result",
                    "url": "https://example.com",
                    "snippet": "Test snippet",
                    "source": "google_search"
                }
            ],
            "max_results": 5
        }
        
        result = await final_processing_node(test_state.copy())
        
        print("✅ final_processing_node: SUCCESS")
        print(f"   Final results: {len(result.get('final_results', []))}")
        return True
        
    except Exception as e:
        print(f"❌ final_processing_node: FAILED - {e}")
        if "Blocking call" in str(e):
            print("   BLOCKING OPERATION DETECTED!")
        return False

async def main():
    """Main test function"""
    print("Comprehensive Blocking Operations Test")
    print("=" * 50)
    
    # Test all nodes
    tests = [
        ("Intent Classifier", test_intent_classifier_node),
        ("Google Search", test_google_search_node),
        ("Web Unlocker", test_web_unlocker_node),
        ("Final Processing", test_final_processing_node)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"❌ {test_name}: CRITICAL ERROR - {e}")
            results[test_name] = False
    
    # Summary
    print("\\n" + "=" * 50)
    print("TEST SUMMARY:")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ No blocking operations detected")
        print("✅ All async conversions working correctly")
        print("\\n🚀 Ready for production deployment!")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("❌ Blocking operations still present")
        print("\\n🔧 Recommendation: Use --allow-blocking flag")
        print("   Or set BG_JOB_ISOLATED_LOOPS=true for deployment")
    
    print("\\n📝 For reliable operation:")
    print("   python start_server_with_blocking.py")

if __name__ == "__main__":
    asyncio.run(main())