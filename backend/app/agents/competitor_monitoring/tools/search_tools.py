"""
Search tools for competitor monitoring.

Uses Tavily Search API for web research.
"""

from datetime import datetime, timezone
from typing import List, Optional

from langchain.tools import tool

from app.core.config import settings


@tool
def search_competitor(
    competitor_name: str,
    aspects: List[str],
) -> dict:
    """
    Search for competitor information using Tavily Search API.

    Use this tool to research a competitor across multiple aspects
    such as products, pricing, news, and social media activity.

    Args:
        competitor_name: Name of the competitor (e.g. "Nike", "Grab", "Shopee")
        aspects: List of aspects to research. Choose from:
                 ["products", "pricing", "news", "social", "general"]
    """
    from tavily import TavilyClient

    api_key = settings.tavily_api_key
    if not api_key:
        return {
            "error": "TAVILY_API_KEY not configured. Please add it to your .env file.",
            "competitor": competitor_name,
        }

    client = TavilyClient(api_key=api_key)

    all_results = []
    for aspect in aspects:
        query = _build_query(competitor_name, aspect)
        try:
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=5,
                include_answer=True,
            )
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
            all_results.append(
                {
                    "aspect": aspect,
                    "query": query,
                    "error": str(e),
                    "results": [],
                }
            )

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
    Search for recent news about a competitor.

    Focused search for the latest news, press releases, and media mentions
    within the specified number of days.

    Args:
        competitor_name: Name of the competitor to search for.
        days: Number of days to look back (default: 7).
    """
    from tavily import TavilyClient

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
            search_depth="advanced",
            max_results=8,
            include_answer=True,
            days=days,
        )
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
