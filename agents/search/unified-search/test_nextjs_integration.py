#!/usr/bin/env python3
"""
Test Next.js API integration with the influencer discovery system.
Verifies that the output format matches what the Next.js API expects.
"""
import asyncio
import sys
import os
import json

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_nextjs_transformation():
    """Test the Next.js transformation node."""
    print("🔄 Testing Next.js Transformation Node...")
    
    try:
        from agent.nodes import nextjs_transform_node
        
        # Sample influencer card data (internal format)
        test_state = {
            "final_results": [
                {
                    "name": "Marques Brownlee",
                    "platform": "YouTube",
                    "profile_url": "https://youtube.com/@mkbhd",
                    "follower_count": "18.5M",
                    "engagement_rate": "3.2%",
                    "niche": "Tech",
                    "description": "Technology reviewer and content creator",
                    "recent_content": "Latest smartphone reviews",
                    "location": "United States",
                    "contact_info": "business@mkbhd.com",
                    "verified": True,
                    "relevance_score": 0.95,
                    "metadata": {"source": "web_scraping"}
                },
                {
                    "name": "Emma Chamberlain",
                    "platform": "Instagram",
                    "profile_url": "https://instagram.com/emmachamberlain",
                    "follower_count": "15.2M",
                    "engagement_rate": "4.1%",
                    "niche": "Lifestyle",
                    "description": "Lifestyle and fashion content creator",
                    "recent_content": "Coffee and fashion posts",
                    "location": "California",
                    "contact_info": "",
                    "verified": True,
                    "relevance_score": 0.87
                }
            ]
        }
        
        # Transform to Next.js format
        result = await nextjs_transform_node(test_state)
        transformed_cards = result["final_results"]
        
        # Verify transformation
        assert len(transformed_cards) == 2, f"Expected 2 cards, got {len(transformed_cards)}"
        
        # Check first card (YouTube)
        card1 = transformed_cards[0]
        expected_fields = [
            "platform", "handle", "url", "profile_url", "profileUrl",
            "name", "title", "score", "tags", "follower_count",
            "engagement_rate", "description", "verified", "location"
        ]
        
        for field in expected_fields:
            assert field in card1, f"Missing required field: {field}"
        
        # Verify platform mapping
        assert card1["platform"] == 1, f"Expected platform 1 (YouTube), got {card1['platform']}"
        assert card1["handle"] == "mkbhd", f"Expected handle 'mkbhd', got {card1['handle']}"
        assert card1["score"] == 0.95, f"Expected score 0.95, got {card1['score']}"
        assert card1["tags"] == ["Tech"], f"Expected tags ['Tech'], got {card1['tags']}"
        
        # Check second card (Instagram)
        card2 = transformed_cards[1]
        assert card2["platform"] == 2, f"Expected platform 2 (Instagram), got {card2['platform']}"
        assert card2["handle"] == "emmachamberlain", f"Expected handle 'emmachamberlain', got {card2['handle']}"
        
        print("✅ Next.js Transformation: All fields correctly transformed")
        return True
        
    except Exception as e:
        print(f"❌ Next.js Transformation Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_handle_extraction():
    """Test handle extraction from various URL formats."""
    print("\n🔗 Testing Handle Extraction...")
    
    try:
        from agent.nodes import extract_handle_from_url
        
        test_cases = [
            # YouTube
            ("https://youtube.com/@mkbhd", "mkbhd"),
            ("https://youtube.com/channel/UCBJycsmduvYEL83R_U4JriQ", "UCBJycsmduvYEL83R_U4JriQ"),
            ("https://youtube.com/c/mkbhd", "mkbhd"),
            ("https://youtube.com/user/mkbhd", "mkbhd"),
            
            # Instagram
            ("https://instagram.com/mkbhd", "mkbhd"),
            ("https://instagram.com/@mkbhd", "mkbhd"),
            
            # TikTok
            ("https://tiktok.com/@mkbhd", "mkbhd"),
            
            # Twitter/X
            ("https://twitter.com/mkbhd", "mkbhd"),
            ("https://x.com/mkbhd", "mkbhd"),
            
            # Twitch
            ("https://twitch.tv/mkbhd", "mkbhd"),
            
            # Edge cases
            ("", ""),
            ("https://example.com", ""),
        ]
        
        for url, expected_handle in test_cases:
            actual_handle = extract_handle_from_url(url)
            assert actual_handle == expected_handle, f"URL: {url} - Expected: {expected_handle}, Got: {actual_handle}"
            print(f"   ✅ {url} → {actual_handle}")
        
        print("✅ Handle Extraction: All test cases passed")
        return True
        
    except Exception as e:
        print(f"❌ Handle Extraction Failed: {e}")
        return False

async def test_end_to_end_nextjs_format():
    """Test complete end-to-end pipeline with Next.js format output."""
    print("\n🚀 Testing End-to-End Next.js Format...")
    
    try:
        from agent.graph import create_influencer_discovery_graph
        
        graph = create_influencer_discovery_graph()
        
        # Test input
        test_state = {
            "query": "tech reviewers",
            "max_results": 3,
            "context": {"platform": {"focus": ["youtube"]}},
            "raw_results": []
        }
        
        # Execute the complete pipeline
        result = await graph.ainvoke(test_state)
        
        # Verify final_results is in Next.js format
        final_results = result.get("final_results", [])
        assert len(final_results) >= 3, f"Expected at least 3 cards, got {len(final_results)}"
        
        # Check format of first card
        card = final_results[0]
        
        # Required Next.js fields
        nextjs_fields = ["platform", "handle", "url", "name", "score", "tags"]
        for field in nextjs_fields:
            assert field in card, f"Missing Next.js required field: {field}"
        
        # Verify data types
        assert isinstance(card["platform"], (int, str)), f"Platform should be int or string, got {type(card['platform'])}"
        assert isinstance(card["handle"], str), f"Handle should be string, got {type(card['handle'])}"
        assert isinstance(card["score"], (int, float)), f"Score should be number, got {type(card['score'])}"
        assert isinstance(card["tags"], list), f"Tags should be list, got {type(card['tags'])}"
        
        # Verify score range
        assert 0 <= card["score"] <= 1, f"Score should be 0-1, got {card['score']}"
        
        print(f"✅ End-to-End: Generated {len(final_results)} Next.js compatible cards")
        print(f"   Sample card: {card['name']} ({card['platform']}) - Score: {card['score']}")
        
        return True
        
    except Exception as e:
        print(f"❌ End-to-End Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_nextjs_api_response_format():
    """Test that the response matches exactly what Next.js API expects."""
    print("\n📋 Testing Next.js API Response Format...")
    
    try:
        from agent.graph import discover_influencers
        
        # Use the helper function that should return Next.js compatible format
        result = await discover_influencers(
            query="fitness influencers",
            max_results=5,
            context={"platform": {"focus": ["instagram", "youtube"]}}
        )
        
        # Verify response structure
        required_keys = ["status", "query", "total_influencers", "influencer_cards"]
        for key in required_keys:
            assert key in result, f"Missing required response key: {key}"
        
        # Verify influencer cards format
        cards = result["influencer_cards"]
        assert isinstance(cards, list), "influencer_cards should be a list"
        assert len(cards) >= 3, f"Should have at least 3 cards, got {len(cards)}"
        
        # Check each card has Next.js format
        for i, card in enumerate(cards):
            # Required fields for Next.js
            required_fields = ["platform", "handle", "name", "score"]
            for field in required_fields:
                assert field in card, f"Card {i} missing field: {field}"
            
            # Optional but expected fields
            expected_fields = ["url", "profile_url", "profileUrl", "title", "tags"]
            for field in expected_fields:
                if field not in card:
                    print(f"   Warning: Card {i} missing optional field: {field}")
        
        print(f"✅ API Response Format: {len(cards)} cards in correct Next.js format")
        
        # Print sample for verification
        sample_card = cards[0]
        print(f"   Sample card structure:")
        for key, value in sample_card.items():
            print(f"     {key}: {type(value).__name__} = {str(value)[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ API Response Format Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run Next.js integration test suite."""
    print("🔗 Next.js API Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Next.js Transformation", test_nextjs_transformation),
        ("Handle Extraction", test_handle_extraction),
        ("End-to-End Next.js Format", test_end_to_end_nextjs_format),
        ("API Response Format", test_nextjs_api_response_format)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"❌ {test_name}: CRITICAL ERROR - {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 NEXT.JS INTEGRATION TEST RESULTS")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name:<25}: {status}")
    
    print(f"\n📈 Overall Score: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL NEXT.JS INTEGRATION TESTS PASSED!")
        print("✅ LangGraph output is fully compatible with Next.js API")
        print("✅ All required fields are present and correctly formatted")
        print("✅ Handle extraction works for all major platforms")
        print("✅ Platform mapping is correct (1=YouTube, 2=Instagram, etc.)")
        print("\n🚀 Ready for Next.js API integration!")
        
        print("\n📝 Next Steps:")
        print("1. Update Next.js API to use the new LangGraph endpoint")
        print("2. Test streaming integration with actual API calls")
        print("3. Verify error handling in production environment")
        
    else:
        print(f"\n⚠️  {total-passed} tests failed")
        print("🔧 Fix failing tests before integrating with Next.js API")
    
    print("\n🔗 Integration Architecture:")
    print("   Next.js API → LangGraph Server → Transformed Response")
    print("   Expected format: {platform: 1, handle: 'mkbhd', ...}")

if __name__ == "__main__":
    asyncio.run(main())