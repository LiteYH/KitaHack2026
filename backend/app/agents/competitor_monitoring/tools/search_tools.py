"""
Search tools for competitor monitoring.

Uses Tavily Search API for web research.
Performance optimized with 'basic' search depth for 3-5x speed improvement.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from langchain.tools import tool

from app.core.config import settings

logger = logging.getLogger(__name__)


@tool
def search_competitor(
    competitor_name: str,
    aspects: List[str],
) -> dict:
    """
    Search for current, real-time competitor information using Tavily Search API.

    USE THIS TOOL when the user:
    - Asks about a specific competitor by name ("Research Nike", "What is Adidas doing?")
    - Wants to know about competitor products, pricing, strategy, or general activities
    - Needs comprehensive information about a competitor's current state
    
    DO NOT USE this tool for:
    - News or recent announcements (use search_competitor_news instead)
    - Setting up monitoring (use create_monitoring_config instead)

    Args:
        competitor_name: Name of the competitor (e.g. "Nike", "Grab", "Shopee", "Samsung")
        aspects: List of aspects to research. Choose from:
                 - "products" - Product launches, features, updates
                 - "pricing" - Pricing strategy, changes, promotions
                 - "social" - Social media activity, campaigns, engagement
                 - "general" - Company strategy, business developments
                 
                 Use multiple aspects for comprehensive research: ["products", "pricing"]
                 
    Returns:
        dict with findings for each aspect, including:
        - answer: AI-generated summary
        - results: List of search results with titles, URLs, content
        - searched_at: Timestamp of search
        
    Example:
        User: "What is Nike doing with their products?"
        → search_competitor(competitor_name="Nike", aspects=["products"])
        
        User: "Research Adidas pricing and social media"
        → search_competitor(competitor_name="Adidas", aspects=["pricing", "social"])
    """
    from tavily import TavilyClient
    import time

    start_time = time.time()
    logger.info(f"[SEARCH] Starting competitor search: {competitor_name}, aspects: {aspects}")

    api_key = settings.tavily_api_key
    if not api_key:
        return {
            "error": "TAVILY_API_KEY not configured. Please add it to your .env file.",
            "competitor": competitor_name,
        }

    client = TavilyClient(api_key=api_key)

    all_results = []
    for i, aspect in enumerate(aspects, 1):
        query = _build_query(competitor_name, aspect)
        logger.info(f"[SEARCH] {i}/{len(aspects)} - Searching aspect '{aspect}' for {competitor_name}")
        aspect_start = time.time()
        try:
            response = client.search(
                query=query,
                search_depth="basic",  # Changed from 'advanced' for 3-5x speed improvement
                max_results=3,  # Reduced from 5 for faster results
                include_answer=True,
            )
            aspect_duration = time.time() - aspect_start
            logger.info(f"[SEARCH] ✓ Aspect '{aspect}' completed in {aspect_duration:.2f}s")
            all_results.append(
                {
                    "aspect": aspect,
                    "query": query,
                    "answer": response.get("answer", ""),
                    "results": [
                        {
                            "title": r.get("title", ""),
                            "url": r.get("url", ""),
                            "content": r.get("content", "")[:500],
                            "score": r.get("score", 0),
                        }
                        for r in response.get("results", [])
                    ],
                }
            )
        except Exception as e:
            aspect_duration = time.time() - aspect_start
            logger.error(f"[SEARCH] ✗ Aspect '{aspect}' failed after {aspect_duration:.2f}s: {e}")
            all_results.append(
                {
                    "aspect": aspect,
                    "query": query,
                    "error": str(e),
                    "results": [],
                }
            )

    total_duration = time.time() - start_time
    logger.info(f"[SEARCH] ✅ Completed search for {competitor_name} in {total_duration:.2f}s ({len(aspects)} aspects)")
    
    return {
        "competitor": competitor_name,
        "aspects": aspects,
        "findings": all_results,
        "searched_at": datetime.now(timezone.utc).isoformat(),
    }


@tool
def search_competitor_news(
    competitor_name: str,
    days: int = 7,
) -> dict:
    """
    Search for recent news and announcements about a competitor.

    USE THIS TOOL when the user:
    - Asks about "recent", "latest", or "new" competitor activities
    - Wants to know about news, announcements, press releases
    - Says keywords: "news", "updates", "announcements", "what's new"
    - Needs time-sensitive information about competitor developments
    
    DO NOT USE this tool for:
    - General competitor information (use search_competitor instead)
    - Ongoing monitoring (use create_monitoring_config instead)

    Args:
        competitor_name: Name of the competitor to search for (e.g. "Nike", "Tesla", "Apple").
        days: Number of days to look back (default: 7). 
              Use 1-7 for very recent, 7-30 for recent trends.
              
    Returns:
        dict with:
        - answer: AI-generated summary of recent news
        - articles: List of news articles with titles, URLs, content, dates
        - period: Time period covered
        - searched_at: Timestamp of search
        
    Example:
        User: "What's new with Nike?"
        → search_competitor_news(competitor_name="Nike", days=7)
        
        User: "Any recent announcements from Tesla this month?"
        → search_competitor_news(competitor_name="Tesla", days=30)
    """
    from tavily import TavilyClient
    import time

    start_time = time.time()
    logger.info(f"[NEWS_SEARCH] Starting news search: {competitor_name}, last {days} days")

    api_key = settings.tavily_api_key
    if not api_key:
        return {
            "error": "TAVILY_API_KEY not configured.",
            "competitor": competitor_name,
        }

    client = TavilyClient(api_key=api_key)

    try:
        response = client.search(
            query=f"{competitor_name} latest news announcements",
            search_depth="basic",  # Changed from 'advanced' for 3-5x speed improvement
            max_results=5,  # Reduced from 8 for faster results
            include_answer=True,
            days=days,
        )
        duration = time.time() - start_time
        logger.info(f"[NEWS_SEARCH] ✅ Completed news search for {competitor_name} in {duration:.2f}s")
        
        return {
            "competitor": competitor_name,
            "period": f"last {days} days",
            "answer": response.get("answer", ""),
            "articles": [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", "")[:500],
                    "published_date": r.get("published_date", ""),
                }
                for r in response.get("results", [])
            ],
            "searched_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"[NEWS_SEARCH] ✗ Failed after {duration:.2f}s: {e}")
        return {
            "competitor": competitor_name,
            "error": str(e),
            "articles": [],
        }


def _build_query(competitor_name: str, aspect: str) -> str:
    """Build a targeted search query for a given aspect."""
    aspect_queries = {
        "products": f"{competitor_name} new product launch update feature release 2026",
        "pricing": f"{competitor_name} pricing change promotion discount offer 2026",
        "news": f"{competitor_name} latest news announcement press release",
        "social": f"{competitor_name} social media campaign marketing activity engagement",
        "general": f"{competitor_name} company update strategy business development",
    }
    return aspect_queries.get(aspect, f"{competitor_name} {aspect}")
