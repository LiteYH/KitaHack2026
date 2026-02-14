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
    CAMPAIGN_KEYWORDS = [
        "campaign", "campaigns", "marketing", "ad", "ads", "advertisement",
        "optimize", "optimization", "performance", "roi", "roas", "ctr", "cvr",
        "budget", "spending", "spend", "conversion", "clicks", "impressions",
        "ongoing", "paused", "active", "running", "current"
    ]
    
    # Status keywords
    STATUS_KEYWORDS = {
        "ongoing": ["ongoing", "active", "running", "current", "live"],
        "paused": ["paused", "stopped", "inactive", "ended", "finished"]
    }
    
    # Platform keywords
    PLATFORM_KEYWORDS = {
        "instagram": ["instagram", "ig", "insta"],
        "facebook": ["facebook", "fb"],
        "kol": ["kol", "influencer", "influencers"],
        "e-commerce": ["ecommerce", "e-commerce", "online store", "shop"]
    }
    
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
                "intent_type": str  # e.g., "optimization", "analysis", "comparison", "general"
            }
        """
        message_lower = user_message.lower()
        
        # Check if message mentions campaigns
        needs_campaign_data = any(keyword in message_lower for keyword in self.CAMPAIGN_KEYWORDS)
        
        # Determine status filter
        status_filter = None
        for status, keywords in self.STATUS_KEYWORDS.items():
            if any(keyword in message_lower for keyword in keywords):
                status_filter = status
                break
        
        # Determine platform filter
        platform_filter = None
        for platform, keywords in self.PLATFORM_KEYWORDS.items():
            if any(keyword in message_lower for keyword in keywords):
                # Capitalize first letter for Firestore query
                platform_filter = platform.title() if platform != "kol" else "KOL"
                if platform == "e-commerce":
                    platform_filter = "E-commerce"
                break
        
        # Determine intent type
        intent_type = "general"
        if any(word in message_lower for word in ["optimize", "optimization", "improve", "enhance", "better"]):
            intent_type = "optimization"
        elif any(word in message_lower for word in ["analyze", "analysis", "performance", "how", "doing"]):
            intent_type = "analysis"
        elif any(word in message_lower for word in ["compare", "comparison", "vs", "versus", "difference"]):
            intent_type = "comparison"
        
        return {
            "needs_campaign_data": needs_campaign_data,
            "status_filter": status_filter,
            "platform_filter": platform_filter,
            "intent_type": intent_type
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
        
        # Add specific instructions based on intent
        context_parts.append("\n# INSTRUCTIONS:")
        if intent["intent_type"] == "optimization":
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
