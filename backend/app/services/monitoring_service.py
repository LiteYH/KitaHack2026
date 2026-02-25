"""
Monitoring Service for executing scheduled monitoring tasks.

This service is used by CronService to run competitor monitoring
without user interaction (no streaming, no HITL approval).
"""
import logging
from typing import List, Dict, Any, Optional

from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from app.core.config import settings
from app.core.firebase import get_db
from app.agents.competitor_monitoring.tools import (
    search_competitor,
    search_competitor_news
)

logger = logging.getLogger(__name__)


class MonitoringService:
    """
    Executes monitoring tasks using the competitor agent.
    Called by CronService for scheduled executions.
    
    Unlike interactive chat, this:
    - Runs without streaming
    - Does not require HITL approval (pre-approved configs)
    - Returns structured results
    """
    
    def __init__(self):
        self.firestore = get_db()
        self._agent = None
    
    def _ensure_init(self):
        """Lazy initialization of the agent"""
        if self._agent is not None:
            return
        
        # Create a simplified agent without HITL for execution
        # We use the tools directly instead of going through the full agent
        logger.info("Initializing monitoring service")
    
    async def execute_monitoring(
        self,
        competitor: str,
        aspects: List[str],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Execute a monitoring task for a competitor.
        
        This method:
        1. Searches for the competitor across specified aspects
        2. Analyzes the findings for significance
        3. Returns structured results
        
        Args:
            competitor: Competitor name to monitor
            aspects: List of aspects to monitor (products, pricing, social, news)
            user_id: User ID who owns this monitoring task
            
        Returns:
            dict with keys:
                - findings: Dict of search results by aspect
                - is_significant: Whether findings are significant
                - significance_score: Numerical score (0-100)
                - summary: Human-readable summary
        """
        self._ensure_init()
        
        logger.info(f"Executing monitoring for {competitor} with aspects: {aspects}")
        
        try:
            # Execute searches for each aspect
            findings = {}
            
            # Main competitor search
            if any(aspect in aspects for aspect in ['products', 'pricing', 'social']):
                try:
                    competitor_info = await self._search_competitor(
                        competitor=competitor,
                        aspects=aspects
                    )
                    findings['competitor_info'] = competitor_info
                except Exception as e:
                    logger.error(f"Error searching competitor: {e}")
                    findings['competitor_info'] = {"error": str(e)}
            
            # News search
            if 'news' in aspects or not aspects:  # Default to news if no aspects specified
                try:
                    news_results = await self._search_news(competitor=competitor)
                    findings['news'] = news_results
                except Exception as e:
                    logger.error(f"Error searching news: {e}")
                    findings['news'] = {"error": str(e)}
            
            # Analyze significance of findings
            significance_analysis = self._analyze_significance(findings)
            
            # Generate summary
            summary = self._generate_summary(
                competitor=competitor,
                findings=findings,
                significance_analysis=significance_analysis
            )
            
            return {
                'findings': findings,
                'is_significant': significance_analysis['is_significant'],
                'significance_score': significance_analysis['score'],
                'reasons': significance_analysis['reasons'],
                'summary': summary,
                'aspects': aspects
            }
            
        except Exception as e:
            logger.error(f"Monitoring execution failed for {competitor}: {e}", exc_info=True)
            # Return error but don't fail completely
            return {
                'findings': {'error': str(e)},
                'is_significant': False,
                'significance_score': 0,
                'reasons': ['Error occurred during monitoring'],
                'summary': f"Monitoring failed: {str(e)}",
                'aspects': aspects
            }
    
    async def _search_competitor(
        self,
        competitor: str,
        aspects: List[str]
    ) -> Dict[str, Any]:
        """
        Search for competitor information using the search_competitor tool.
        
        Args:
            competitor: Competitor name
            aspects: Aspects to search for
            
        Returns:
            Search results
        """
        try:
            # Invoke the tool directly
            result = await search_competitor.ainvoke({
                "competitor_name": competitor,
                "aspects": aspects
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Competitor search failed: {e}")
            return {"error": str(e), "results": []}
    
    async def _search_news(self, competitor: str) -> Dict[str, Any]:
        """
        Search for competitor news using the search_competitor_news tool.
        
        Args:
            competitor: Competitor name
            
        Returns:
            News search results
        """
        try:
            # Invoke the tool directly
            result = await search_competitor_news.ainvoke({
                "competitor_name": competitor,
                "days": 7  # Last 7 days
            })
            
            return result
            
        except Exception as e:
            logger.error(f"News search failed: {e}")
            return {"error": str(e), "articles": []}
    
    def _analyze_significance(self, findings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze if findings are significant.
        
        Uses heuristic rules to determine significance:
        - New product launches: HIGH (80-100)
        - Price changes: MEDIUM-HIGH (60-80)
        - Major news coverage: MEDIUM-HIGH (60-80)
        - Social sentiment changes: MEDIUM (40-60)
        - Minor updates: LOW (0-40)
        
        Args:
            findings: Dictionary of search results
            
        Returns:
            dict with keys:
                - is_significant: bool
                - score: int (0-100)
                - reasons: List of strings explaining why
        """
        score = 0
        reasons = []
        
        # Analyze competitor info
        competitor_info = findings.get('competitor_info', {})
        if isinstance(competitor_info, dict):
            results = competitor_info.get('results', [])
            
            # Check for product launches
            product_keywords = ['launch', 'release', 'announce', 'new product', 'unveil']
            for result in results[:5]:  # Check top 5 results
                content = result.get('content', '').lower()
                title = result.get('title', '').lower()
                
                if any(keyword in content or keyword in title for keyword in product_keywords):
                    score += 30
                    reasons.append("New product launch detected")
                    break
            
            # Check for pricing mentions
            pricing_keywords = ['price', 'pricing', 'discount', 'promotion', 'sale', 'cost']
            for result in results[:5]:
                content = result.get('content', '').lower()
                title = result.get('title', '').lower()
                
                if any(keyword in content or keyword in title for keyword in pricing_keywords):
                    score += 20
                    reasons.append("Pricing-related information found")
                    break
        
        # Analyze news
        news = findings.get('news', {})
        if isinstance(news, dict):
            articles = news.get('articles', [])
            
            if len(articles) >= 3:
                score += 25
                reasons.append(f"High news coverage ({len(articles)} articles)")
            elif len(articles) >= 1:
                score += 15
                reasons.append(f"Moderate news coverage ({len(articles)} articles)")
            
            # Check for major news indicators
            major_keywords = [
                'acquisition', 'merger', 'partnership', 'funding', 'raise',
                'expansion', 'breakthrough', 'award', 'scandal', 'lawsuit'
            ]
            
            for article in articles[:3]:  # Check top 3 articles
                title = article.get('title', '').lower()
                content = article.get('content', '').lower()
                
                for keyword in major_keywords:
                    if keyword in title or keyword in content:
                        score += 20
                        reasons.append(f"Major event detected: {keyword}")
                        break
        
        # Cap score at 100
        score = min(100, score)
        
        # Determine significance threshold
        is_significant = score >= 50
        
        if not reasons:
            reasons.append("No significant changes detected")
        
        return {
            'is_significant': is_significant,
            'score': score,
            'reasons': reasons
        }
    
    def _generate_summary(
        self,
        competitor: str,
        findings: Dict[str, Any],
        significance_analysis: Dict[str, Any]
    ) -> str:
        """
        Generate a human-readable summary of the findings.
        
        Args:
            competitor: Competitor name
            findings: Search results
            significance_analysis: Significance analysis
            
        Returns:
            Summary text
        """
        summary_parts = [
            f"# Monitoring Results for {competitor}",
            "",
            f"**Significance Score:** {significance_analysis['score']}/100",
            ""
        ]
        
        # Add significance reasons
        if significance_analysis['reasons']:
            summary_parts.append("**Key Findings:**")
            for reason in significance_analysis['reasons']:
                summary_parts.append(f"- {reason}")
            summary_parts.append("")
        
        # Add competitor info summary
        competitor_info = findings.get('competitor_info', {})
        if isinstance(competitor_info, dict) and 'results' in competitor_info:
            results = competitor_info['results'][:3]  # Top 3 results
            if results:
                summary_parts.append("**Competitor Information:**")
                for i, result in enumerate(results, 1):
                    title = result.get('title', 'No title')
                    url = result.get('url', '')
                    summary_parts.append(f"{i}. [{title}]({url})")
                summary_parts.append("")
        
        # Add news summary
        news = findings.get('news', {})
        if isinstance(news, dict) and 'articles' in news:
            articles = news['articles'][:3]  # Top 3 articles
            if articles:
                summary_parts.append("**Recent News:**")
                for i, article in enumerate(articles, 1):
                    title = article.get('title', 'No title')
                    url = article.get('url', '')
                    published = article.get('published_date', '')
                    summary_parts.append(f"{i}. [{title}]({url}) - {published}")
                summary_parts.append("")
        
        return "\n".join(summary_parts)


# Singleton instance
monitoring_service = MonitoringService()
