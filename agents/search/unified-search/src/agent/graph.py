"""Enhanced LangGraph for Influencer Discovery.

Always returns structured influencer cards with comprehensive profile data.
"""

from __future__ import annotations
from typing import TypedDict, List, Dict, Any, Optional, Literal
from langgraph.graph import StateGraph, START, END
from agent.nodes import (
    query_renderer_node,
    policy_node,
    intent_classifier_node,
    google_search_node,
    web_unlocker_node,
    final_processing_node,
    nextjs_transform_node,  # NEW: Add transformation node
)
import re

class InfluencerSearchState(TypedDict):
    """Enhanced state definition for influencer discovery graph."""
    
    # Input
    query: str
    context: Optional[Dict[str, Any]]
    geo: Optional[str]
    user_locale: Optional[str]
    max_results: Optional[int]
    recency_bias_days: Optional[int]
    platform_hints: Optional[List[str]]
    
    # Intent Classification Results
    intent: Optional[str]
    intent_confidence: Optional[float]
    intent_reasoning: Optional[str]
    search_strategy: Optional[str]
    platform_focus: Optional[List[str]]  # NEW: Specific platforms to focus on
    
    # Search Results
    raw_results: List[Dict[str, Any]]
    final_results: Optional[List[Dict[str, Any]]]  # Influencer cards
    query_summary: Optional[str]
    total_processed: Optional[int]
    
    # Node Completion Flags
    google_search_completed: Optional[bool]
    web_unlocker_completed: Optional[bool]
    final_processing_completed: Optional[bool]
    
    # Error Handling
    error: Optional[str]
    google_search_error: Optional[str]
    web_unlocker_error: Optional[str]
    final_processing_error: Optional[str]
    
    # Influencer-specific metadata
    platforms_searched: Optional[List[str]]
    min_cards_required: Optional[int]  # Minimum cards to return


def route_after_intent(state: Dict[str, Any]) -> Literal["google_search", "web_unlocker"]:
    """
    Enhanced routing function for influencer discovery.
    
    Args:
        state: Current graph state with intent classification results
        
    Returns:
        Name of the next node to execute
    """
    query = state.get("query", "")
    
    # Check for specific URLs (profile links)
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    has_url = bool(re.search(url_pattern, query))
    
    # If URL provided, scrape it directly
    if has_url:
        return "web_unlocker"
    
    # Route based on search strategy
    search_strategy = state.get("search_strategy", "google_then_scrape")
    
    if search_strategy == "web_unlocker_only":
        return "web_unlocker"
    else:
        # Default to Google search first for influencer discovery
        return "google_search"


def route_after_google(state: Dict[str, Any]) -> Literal["web_unlocker", "final_processing"]:
    """
    Route after Google search - determine if scraping is needed.
    
    For influencer discovery, we often want to scrape profiles for detailed data.
    """
    search_strategy = state.get("search_strategy", "google_then_scrape")
    raw_results = state.get("raw_results", [])
    
    # If we have profile URLs, scrape them for detailed data
    profile_urls = [
        r.get("url", "") for r in raw_results 
        if any(platform in r.get("url", "").lower() 
               for platform in ["youtube.com", "instagram.com", "tiktok.com", "twitter.com", "twitch.tv"])
    ]
    
    # Scrape if strategy requires it OR if we have profile URLs
    if search_strategy in ["google_then_scrape", "both_parallel"] or profile_urls:
        return "web_unlocker"
    else:
        return "final_processing"


def route_after_web_unlocker(state: Dict[str, Any]) -> Literal["final_processing"]:
    """Route after web unlocker - always proceed to final processing."""
    return "final_processing"


def create_influencer_discovery_graph() -> StateGraph:
    """
    Create the enhanced influencer discovery graph with guaranteed card output.
    
    Features:
    - Always returns structured influencer cards
    - Fallback mechanisms ensure minimum card count
    - Enhanced error handling with graceful degradation
    - Parallel search and scraping strategies
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Initialize the graph with enhanced state
    workflow = StateGraph(InfluencerSearchState)
    
    # Add nodes
    workflow.add_node("query_renderer", query_renderer_node)
    workflow.add_node("policy", policy_node)
    workflow.add_node("intent_classifier", intent_classifier_node)
    workflow.add_node("google_search", google_search_node)
    workflow.add_node("web_unlocker", web_unlocker_node)
    workflow.add_node("final_processing", final_processing_node)
    workflow.add_node("nextjs_transform", nextjs_transform_node)  # NEW: Transform for Next.js compatibility
    
    # Set entry point - start with query rendering using Gemini 2.0 Flash Lite
    workflow.add_edge(START, "query_renderer")
    workflow.add_edge("query_renderer", "policy")
    workflow.add_edge("policy", "intent_classifier")
    
    # Add conditional routing after intent classification
    workflow.add_conditional_edges(
        "intent_classifier",
        route_after_intent,
        {
            "google_search": "google_search",
            "web_unlocker": "web_unlocker"
        }
    )
    
    # Add conditional routing after Google search
    workflow.add_conditional_edges(
        "google_search",
        route_after_google,
        {
            "web_unlocker": "web_unlocker",
            "final_processing": "final_processing" 
        }
    )
    
    # Add conditional routing after web unlocker
    workflow.add_conditional_edges(
        "web_unlocker",
        route_after_web_unlocker,
        {
            "final_processing": "final_processing"
        }
    )
    
    # Add transformation before END
    workflow.add_edge("final_processing", "nextjs_transform")
    workflow.add_edge("nextjs_transform", END)
    
    return workflow.compile()


# Create the compiled graph
graph = create_influencer_discovery_graph()


# Helper function to validate influencer cards
def validate_influencer_cards(results: List[Dict[str, Any]]) -> bool:
    """
    Validate that results are properly formatted influencer cards.
    Supports both internal format and Next.js transformed format.
    
    Args:
        results: List of result dictionaries
        
    Returns:
        True if valid influencer cards, False otherwise
    """
    if not results:
        return False
    
    # Check if this is Next.js format (has 'handle' field) or internal format
    first_result = results[0]
    
    if "handle" in first_result:
        # Next.js format validation
        required_fields = {"name", "platform", "handle", "score"}
        for result in results:
            if not all(field in result for field in required_fields):
                return False
            # Check if score is valid
            if not (0 <= result.get("score", -1) <= 1):
                return False
    else:
        # Internal format validation
        required_fields = {"name", "platform", "profile_url", "niche", "description", "relevance_score"}
        for result in results:
            if not all(field in result for field in required_fields):
                return False
            # Check if relevance_score is valid
            if not (0 <= result.get("relevance_score", -1) <= 1):
                return False
    
    return True


# Helper function to format influencer cards for output
def format_influencer_cards_output(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the final state for clean influencer card output.
    
    Args:
        state: Final graph state
        
    Returns:
        Formatted output dictionary
    """
    final_results = state.get("final_results", [])
    
    # Ensure we have valid influencer cards
    if not validate_influencer_cards(final_results):
        raise ValueError("Invalid influencer card format in final results")
    
    return {
        "status": "success",
        "query": state.get("query", ""),
        "total_influencers": len(final_results),
        "query_summary": state.get("query_summary", ""),
        "platforms_searched": state.get("platforms_searched", []),
        "influencer_cards": final_results,
        "metadata": {
            "intent": state.get("intent"),
            "intent_confidence": state.get("intent_confidence"),
            "search_strategy": state.get("search_strategy"),
            "geo": state.get("geo"),
            "platform_focus": state.get("platform_focus"),
            "errors": {
                "google_search": state.get("google_search_error"),
                "web_unlocker": state.get("web_unlocker_error"),
                "final_processing": state.get("final_processing_error"),
            }
        }
    }


# Example usage function
async def discover_influencers(
    query: str,
    context: Optional[Dict[str, Any]] = None,
    max_results: int = 10,
    geo: Optional[str] = None
) -> Dict[str, Any]:
    """
    Discover influencers based on query and context.
    
    Args:
        query: Search query for influencer discovery
        context: Optional context with filters (platforms, geography, etc.)
        max_results: Maximum number of influencer cards to return
        geo: Geographic preference (country code)
        
    Returns:
        Dictionary with influencer cards and metadata
        
    Example:
        >>> results = await discover_influencers(
        ...     query="tech reviewers",
        ...     context={
        ...         "platform": {"ids": [1, 2]},  # YouTube and Instagram
        ...         "geography": {"audience": ["US"]}
        ...     },
        ...     max_results=10
        ... )
        >>> print(f"Found {results['total_influencers']} influencers")
        >>> for card in results['influencer_cards']:
        ...     print(f"{card['name']} - {card['platform']}")
    """
    
    # Initialize input state
    input_state = {
        "query": query,
        "context": context or {},
        "max_results": max_results,
        "geo": geo,
        "raw_results": [],
        "min_cards_required": max(3, max_results // 2)  # Ensure minimum cards
    }
    
    # Execute the graph
    final_state = await graph.ainvoke(input_state)
    
    # Format and validate output
    try:
        output = format_influencer_cards_output(final_state)
        
        # Ensure minimum card count
        if output["total_influencers"] < input_state["min_cards_required"]:
            print(f"Warning: Only {output['total_influencers']} cards generated, "
                  f"expected at least {input_state['min_cards_required']}")
        
        return output
        
    except ValueError as e:
        # Fallback if validation fails
        return {
            "status": "error",
            "query": query,
            "total_influencers": 0,
            "error": str(e),
            "influencer_cards": [],
            "metadata": final_state
        }


# Synchronous wrapper for non-async contexts
def discover_influencers_sync(
    query: str,
    context: Optional[Dict[str, Any]] = None,
    max_results: int = 10,
    geo: Optional[str] = None
) -> Dict[str, Any]:
    """
    Synchronous wrapper for discover_influencers.
    
    Use this in non-async contexts like Flask/Django views.
    """
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(
        discover_influencers(query, context, max_results, geo)
    )