from typing import Any, Dict, Optional, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent.graph import create_influencer_discovery_graph

graph = create_influencer_discovery_graph()
app = FastAPI(title="Unified Search Agent")


class RunRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None
    max_results: Optional[int] = None
    geo: Optional[str] = None
    user_locale: Optional[str] = None


class InfluencerDiscoveryRequest(BaseModel):
    """Enhanced request model for influencer discovery."""
    query: str
    max_results: Optional[int] = 10
    min_cards_required: Optional[int] = 3
    platform_focus: Optional[List[str]] = None  # ["youtube", "instagram", "tiktok"]
    geo: Optional[str] = None
    user_locale: Optional[str] = "en-US"
    search_strategy: Optional[str] = "auto"  # auto, google_only, scrape_only
    context: Optional[Dict[str, Any]] = None


@app.post("/api/run")
async def run_unified_search(request: RunRequest) -> Dict[str, Any]:
    initial_state: Dict[str, Any] = {
        "query": request.query,
        "context": request.context or {},
        "geo": request.geo,
        "user_locale": request.user_locale,
        "max_results": request.max_results or 10,  # Increased default for better discovery
        "raw_results": [],
    }

    try:
        result = await graph.ainvoke(initial_state)
        
        # Return in the new influencer discovery format
        final_results = result.get("final_results", [])
        return {
            "influencer_cards": final_results,
            "total_influencers": len(final_results),
            "query_summary": result.get("query_summary", f"Found {len(final_results)} influencers"),
            "intent": result.get("intent", "influencer_search"),
            "intent_confidence": result.get("intent_confidence", 0.8),
            "platforms_searched": result.get("platforms_searched", []),
            "metadata": {
                "search_strategy": result.get("search_strategy", "auto"),
                "google_search_completed": result.get("google_search_completed", False),
                "web_unlocker_completed": result.get("web_unlocker_completed", False),
                "final_processing_completed": result.get("final_processing_completed", False),
                "errors": {
                    "google_search_error": result.get("google_search_error"),
                    "web_unlocker_error": result.get("web_unlocker_error"),
                    "final_processing_error": result.get("final_processing_error")
                }
            }
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/discover-influencers")
async def discover_influencers(request: InfluencerDiscoveryRequest) -> Dict[str, Any]:
    """
    Dedicated endpoint for influencer discovery with enhanced features.
    Always returns structured influencer cards with fallback mechanisms.
    """
    initial_state: Dict[str, Any] = {
        "query": request.query,
        "max_results": request.max_results or 10,
        "min_cards_required": request.min_cards_required or 3,
        "geo": request.geo,
        "user_locale": request.user_locale or "en-US",
        "search_strategy": request.search_strategy or "auto",
        "context": request.context or {},
        "raw_results": [],
    }
    
    # Add platform focus if specified
    if request.platform_focus:
        if "platform" not in initial_state["context"]:
            initial_state["context"]["platform"] = {}
        initial_state["context"]["platform"]["focus"] = request.platform_focus

    try:
        result = await graph.ainvoke(initial_state)
        
        # Ensure we have the minimum required cards
        final_results = result.get("final_results", [])
        min_required = request.min_cards_required or 3
        
        if len(final_results) < min_required:
            # This should be handled by the graph, but double-check
            from agent.nodes import create_supplemental_influencer_cards
            supplemental = await create_supplemental_influencer_cards(
                request.query, result, existing_count=len(final_results)
            )
            final_results.extend(supplemental)
        
        return {
            "success": True,
            "influencer_cards": final_results[:request.max_results or 10],
            "total_influencers": len(final_results),
            "query_summary": result.get("query_summary", f"Found {len(final_results)} influencers for: {request.query}"),
            "intent": result.get("intent", "influencer_search"),
            "intent_confidence": result.get("intent_confidence", 0.8),
            "intent_reasoning": result.get("intent_reasoning", "Classified as influencer discovery"),
            "platforms_searched": result.get("platforms_searched", request.platform_focus or []),
            "search_metadata": {
                "search_strategy_used": result.get("search_strategy", "auto"),
                "google_search_completed": result.get("google_search_completed", False),
                "web_unlocker_completed": result.get("web_unlocker_completed", False),
                "final_processing_completed": result.get("final_processing_completed", False),
                "fallback_triggered": any([
                    result.get("google_search_error"),
                    result.get("web_unlocker_error"),
                    len(result.get("raw_results", [])) == 0
                ]),
                "data_completeness": sum(1 for card in final_results if card.get("follower_count", "Unknown") != "Unknown") / max(len(final_results), 1),
                "average_relevance_score": sum(card.get("relevance_score", 0.5) for card in final_results) / max(len(final_results), 1)
            },
            "errors": {
                "google_search_error": result.get("google_search_error"),
                "web_unlocker_error": result.get("web_unlocker_error"),
                "final_processing_error": result.get("final_processing_error")
            }
        }
    except Exception as exc:
        # Emergency fallback - always return something
        from agent.nodes import create_fallback_influencer_cards
        try:
            fallback_cards = await create_fallback_influencer_cards(request.query, initial_state)
            return {
                "success": False,
                "influencer_cards": fallback_cards,
                "total_influencers": len(fallback_cards),
                "query_summary": f"Generated {len(fallback_cards)} suggested influencer profiles for: {request.query}",
                "intent": "influencer_search",
                "intent_confidence": 0.5,
                "intent_reasoning": "Emergency fallback classification",
                "platforms_searched": request.platform_focus or ["youtube", "instagram"],
                "search_metadata": {
                    "search_strategy_used": "emergency_fallback",
                    "fallback_triggered": True,
                    "data_completeness": 0.3,
                    "average_relevance_score": 0.4
                },
                "errors": {
                    "system_error": str(exc)
                }
            }
        except:
            # Absolute last resort
            raise HTTPException(status_code=500, detail=f"System error: {str(exc)}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "influencer-discovery-system"}


@app.get("/api/platforms")
async def get_supported_platforms():
    """Get list of supported platforms."""
    return {
        "platforms": [
            {"id": "youtube", "name": "YouTube", "description": "Video content creators"},
            {"id": "instagram", "name": "Instagram", "description": "Photo and story content"},
            {"id": "tiktok", "name": "TikTok", "description": "Short-form video content"},
            {"id": "twitter", "name": "Twitter/X", "description": "Microblogging and commentary"},
            {"id": "twitch", "name": "Twitch", "description": "Live streaming and gaming"}
        ]
    }

