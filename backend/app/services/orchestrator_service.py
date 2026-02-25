"""
Orchestrator Service - Analyzes user intent and coordinates data fetching and AI response generation
"""

import re
from typing import Optional, List, Dict, Any
import google.generativeai as genai
from app.core.config import settings
from app.services.campaign_service import campaign_service
from app.schemas.campaign import Campaign, CampaignMetrics
from app.schemas.chat import ChatMessage


class OrchestratorService:
    """Orchestrates the flow between intent analysis, data fetching, and response generation"""
    
    # Keywords that indicate the user wants campaign data
    # Must be specific to campaigns, not general marketing terms
    CAMPAIGN_KEYWORDS = [
        "campaign", "campaigns", "ad", "ads", "advertisement",
        "roi", "roas", "ctr", "cvr",
        "budget", "spending", "spend", "conversion", "clicks", "impressions",
    ]
    
    # Keywords that indicate a simple informational query (not deep analysis)
    SIMPLE_QUERY_KEYWORDS = [
        "how many", "count", "number of", "list", "show me", "tell me which",
        "what are", "which campaigns"
    ]
    
    # Keywords that indicate the query is NOT about user's own campaigns
    EXCLUSION_KEYWORDS = [
        "competitor", "competitors", "competition", "rival", "rivals",
        "other companies", "other brands", "market leaders", "industry"
    ]
    
    # Status keywords - these are more specific
    STATUS_KEYWORDS = {
        "ongoing": ["ongoing", "active", "running", "current", "live"],
        "paused": ["paused", "stopped", "inactive", "ended", "finished"]
    }
    
    # Platform keywords with word boundaries
    PLATFORM_KEYWORDS = {
        "Instagram": [r"\binstagram\b", r"\binsta\b"],
        "Facebook": [r"\bfacebook\b", r"\bfb\b"],
        "KOL": [r"\bkol\b", r"\binfluencer\b", r"\binfluencers\b"],
        "E-commerce": [r"\becommerce\b", r"\be-commerce\b", r"\bonline store\b", r"\bshop\b"]
    }
    
    # Modification keywords - indicate user wants to change campaign data
    MODIFICATION_KEYWORDS = [
        "change", "modify", "update", "edit", "adjust", "set",
        "increase", "decrease", "raise", "lower", "reduce",
        "pause", "stop", "resume", "start", "activate", "deactivate",
        "allocate", "reallocate", "shift", "move"
    ]
    
    # Visualization keywords - indicate user wants to see charts/graphs
    VISUALIZATION_KEYWORDS = [
        "chart", "charts", "graph", "graphs", "visual", "visualization", "visualizations",
        "visualize", "show me chart", "show me graph", "bar chart", "pie chart", "trend",
        "trends", "analytics dashboard", "illustrative", "illustrate"
    ]
    
    def __init__(self):
        """Initialize the orchestrator with Gemini API"""
        api_key = settings.google_api_key
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        
        genai.configure(api_key=api_key)
        self.intent_model = genai.GenerativeModel(model_name='gemini-2.5-flash-lite')
    
    def analyze_intent(self, user_message: str) -> Dict[str, Any]:
        """
        Analyze user message to determine intent and required data
        
        Args:
            user_message: The user's message
            
        Returns:
            Dictionary containing intent analysis:
            {
                "needs_campaign_data": bool,
                "status_filter": str | None,
                "platform_filter": str | None,
                "intent_type": str,
                "is_simple_query": bool
            }
        """
        message_lower = user_message.lower()
        
        # First check for exclusion keywords (competitor analysis, etc.)
        has_exclusion = any(keyword in message_lower for keyword in self.EXCLUSION_KEYWORDS)
        
        if has_exclusion:
            # This is NOT about user's campaigns
            return {
                "needs_campaign_data": False,
                "status_filter": None,
                "platform_filter": None,
                "intent_type": "general",
                "is_simple_query": False
            }
        
        # Check if message mentions campaigns
        needs_campaign_data = any(keyword in message_lower for keyword in self.CAMPAIGN_KEYWORDS)
        
        # Check if this is a simple informational query
        is_simple_query = any(phrase in message_lower for phrase in self.SIMPLE_QUERY_KEYWORDS)
        
        # Determine status filter - only if explicitly mentioned
        status_filter = None
        status_mentioned = False
        for status, keywords in self.STATUS_KEYWORDS.items():
            if any(re.search(rf"\b{keyword}\b", message_lower) for keyword in keywords):
                status_filter = status
                status_mentioned = True
                break
        
        # Determine platform filter - use regex for word boundaries
        platform_filter = None
        for platform, patterns in self.PLATFORM_KEYWORDS.items():
            if any(re.search(pattern, message_lower) for pattern in patterns):
                platform_filter = platform
                break
        
        # Determine intent type
        intent_type = "general"
        if any(re.search(rf"\b{word}\b", message_lower) for word in ["optimize", "optimization", "improve", "enhance", "better"]):
            intent_type = "optimization"
        elif any(re.search(rf"\b{word}\b", message_lower) for word in ["analyze", "analysis", "performance", "doing", "performing"]):
            intent_type = "analysis"
        elif any(re.search(rf"\b{word}\b", message_lower) for word in ["compare", "comparison", "versus", "difference"]):
            intent_type = "comparison"
        
        # Check if user wants to modify campaign data
        wants_to_modify = (
            needs_campaign_data and 
            any(keyword in message_lower for keyword in self.MODIFICATION_KEYWORDS)
        )
        
        # Check if user wants visualizations
        wants_visualization = (
            needs_campaign_data and 
            any(keyword in message_lower for keyword in self.VISUALIZATION_KEYWORDS)
        )
        
        return {
            "needs_campaign_data": needs_campaign_data,
            "status_filter": status_filter,
            "platform_filter": platform_filter,
            "intent_type": intent_type,
            "is_simple_query": is_simple_query,
            "wants_to_modify": wants_to_modify,
            "wants_visualization": wants_visualization
        }
    
    async def get_relevant_campaigns(
        self,
        user_id: str,
        intent: Dict[str, Any]
    ) -> tuple[List[Campaign], List[CampaignMetrics], Dict[str, Any]]:
        """
        Fetch relevant campaign data based on intent analysis
        
        Args:
            user_id: User ID to fetch campaigns for
            intent: Intent analysis result
            
        Returns:
            Tuple of (campaigns, metrics, summary)
        """
        if not intent["needs_campaign_data"]:
            return [], [], {}
        
        # Fetch campaigns with filters
        campaigns, metrics = await campaign_service.get_campaigns_with_metrics(
            user_id=user_id,
            status=intent["status_filter"],
            platform=intent["platform_filter"]
        )
        
        # Generate summary
        summary = campaign_service.generate_metrics_summary(campaigns, metrics)
        
        return campaigns, metrics, summary
    
    def build_context_prompt(
        self,
        user_message: str,
        campaigns: List[Campaign],
        metrics: List[CampaignMetrics],
        summary: Dict[str, Any],
        intent: Dict[str, Any]
    ) -> str:
        """
        Build enriched prompt with campaign data context for the AI
        
        Args:
            user_message: Original user message
            campaigns: List of relevant campaigns
            metrics: List of calculated metrics
            summary: Aggregated metrics summary
            intent: Intent analysis result
            
        Returns:
            Enriched prompt string
        """
        # If no campaign data needed, return original message
        if not campaigns:
            return user_message
        
        # Build context section
        context_parts = [
            "# CONTEXT: User's Campaign Data\n",
            f"The user has {len(campaigns)} campaign(s) in their account.\n"
        ]
        
        # Add summary statistics
        if summary:
            context_parts.append("\n## Overall Performance Summary:")
            context_parts.append(f"- Total Budget: ${summary.get('total_budget', 0):,}")
            context_parts.append(f"- Total Spent: ${summary.get('total_spent', 0):,}")
            context_parts.append(f"- Overall CTR: {summary.get('overall_ctr', 0)}%")
            context_parts.append(f"- Overall CVR: {summary.get('overall_cvr', 0)}%")
            context_parts.append(f"- Overall ROAS: {summary.get('overall_roas', 0)}x")
            context_parts.append(f"- Budget Utilization: {summary.get('overall_budget_utilization', 0)}%")
            context_parts.append(f"- Total Conversions: {summary.get('total_purchases', 0):,}")
            context_parts.append(f"- Total Revenue: ${summary.get('total_conversion_value', 0):,}\n")
        
        # Add individual campaign details
        context_parts.append("\n## Individual Campaign Details:\n")
        for i, (campaign, metric) in enumerate(zip(campaigns, metrics), 1):
            context_parts.append(f"\n### {i}. {campaign.campaignName}")
            context_parts.append(f"   - Status: **{campaign.status.upper()}**")
            context_parts.append(f"   - Platform: {campaign.platform}")
            context_parts.append(f"   - Budget: ${campaign.totalBudget:,} | Spent: ${campaign.amountSpent:,} ({metric.budget_utilization}%)")
            context_parts.append(f"   - Impressions: {campaign.impressions:,} | Clicks: {campaign.clicks:,} | Purchases: {campaign.purchases:,}")
            context_parts.append(f"   - **Metrics:**")
            context_parts.append(f"     - CTR: {metric.ctr}%")
            context_parts.append(f"     - CVR: {metric.cvr}%")
            context_parts.append(f"     - ROAS: {metric.roas}x")
            context_parts.append(f"     - Cost per Click: ${metric.cost_per_click:.2f}")
            context_parts.append(f"     - Cost per Conversion: ${metric.cost_per_conversion:.2f}")
            context_parts.append(f"     - Revenue: ${campaign.conversionValue:,}")
        
        # Add user's original question
        context_parts.append(f"\n\n# USER'S QUESTION:\n{user_message}\n")
        
        # Add specific instructions based on query type
        context_parts.append("\n# INSTRUCTIONS:")
        
        # Check if this is a modification request
        if intent.get("wants_to_modify", False):
            context_parts.append(
                "The user wants to MODIFY their campaign data (budget, status, etc.). "
                "Explain what changes you understand they want to make, then inform them that you'll display "
                "their campaigns in an interactive analytics view where they can make the changes. "
                "Tell them: 'I'll show you your campaigns below so you can make these changes directly.'\n\n"
                "Keep your response brief and focused on confirming their requested changes."
            )
        # Check if this is a simple query
        elif intent.get("is_simple_query", False):
            context_parts.append(
                "The user is asking a simple, straightforward question. Answer DIRECTLY and CONCISELY first. "
                "Provide the specific information requested (counts, names, etc.) in a clear, brief manner. \n\n"
                "After answering their question, you may optionally ask: \"Would you like me to provide "
                "a detailed analysis and optimization recommendations for these campaigns?\"\n\n"
                "Do NOT provide full analysis unless specifically requested."
            )
        elif intent["intent_type"] == "optimization":
            context_parts.append(
                "Analyze the campaign performance data above and provide specific, actionable optimization recommendations. "
                "Focus on campaigns with low CTR, CVR, or ROAS. Suggest concrete improvements for budget allocation, "
                "targeting, creative, or bidding strategies. Use the actual metrics to support your recommendations."
            )
        elif intent["intent_type"] == "analysis":
            context_parts.append(
                "Provide a detailed analysis of the campaign performance. Identify top performers and underperformers. "
                "Explain what the metrics indicate about campaign health. Be specific and reference the actual data."
            )
        elif intent["intent_type"] == "comparison":
            context_parts.append(
                "Compare the campaigns based on their performance metrics. Highlight differences in performance across "
                "platforms, identify patterns, and explain what drives the differences."
            )
        else:
            context_parts.append(
                "Use the campaign data provided above to answer the user's question accurately. "
                "Reference specific campaigns and metrics in your response."
            )
        
        return "\n".join(context_parts)
    
    async def orchestrate_response(
        self,
        user_message: str,
        user_id: Optional[str],
        conversation_history: Optional[List[ChatMessage]] = None
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        """
        Main orchestration method: analyze intent, fetch data, generate response
        
        Args:
            user_message: User's input message
            user_id: User ID for fetching campaigns
            conversation_history: Previous conversation context
            
        Returns:
            Tuple of (AI response, campaign_context dict or None)
        """
        # Step 1: Analyze intent
        intent = self.analyze_intent(user_message)
        
        # Step 2: Fetch relevant data if needed
        campaigns, metrics, summary = [], [], {}
        if intent["needs_campaign_data"] and user_id:
            campaigns, metrics, summary = await self.get_relevant_campaigns(user_id, intent)
        
        # Step 3: Build enriched prompt with context
        enriched_prompt = self.build_context_prompt(
            user_message=user_message,
            campaigns=campaigns,
            metrics=metrics,
            summary=summary,
            intent=intent
        )
        
        # Step 4: Return the enriched prompt and context data
        # The chat service will use this to generate the response
        campaign_context = None
        if campaigns:
            campaign_context = {
                "campaigns": [c.model_dump() for c in campaigns],
                "metrics": [m.model_dump() for m in metrics],
                "summary": summary,
                "intent": intent
            }
        
        return enriched_prompt, campaign_context


# Singleton instance
orchestrator_service = OrchestratorService()
