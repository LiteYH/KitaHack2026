#!/usr/bin/env python3
"""
AI Agent for YouTube ROI Report Generation
Analyzes YouTube ROI metrics from Firestore and generates HTML reports optimized for xhtml2pdf conversion
"""

import asyncio
import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import logging

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

try:
    import google.generativeai as genai
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage, SystemMessage
    GOOGLE_GENAI_AVAILABLE = True
    print("✅ Google Generative AI available")
except ImportError:
    GOOGLE_GENAI_AVAILABLE = False
    print("❌ Google Generative AI not available")

from app.core.firestore_client import firestore_client
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubeROIReportAgent:
    """
    AI Agent that analyzes YouTube ROI metrics from Firestore and generates HTML reports
    """
    
    def __init__(self):
        self.google_genai_available = GOOGLE_GENAI_AVAILABLE
        self.model = None
        
        if self.google_genai_available:
            try:
                # Configure Google Generative AI
                if settings.google_api_key:
                    genai.configure(api_key=settings.google_api_key)
                    self.model = ChatGoogleGenerativeAI(
                        model="gemini-2.0-flash-exp",
                        temperature=0.3,  # Low temperature for consistent output
                        max_output_tokens=8192
                    )
                    logger.info("✅ Google Generative AI model initialized")
                else:
                    logger.warning("⚠️ Google API key not configured")
                    self.google_genai_available = False
            except Exception as e:
                logger.error(f"❌ Failed to initialize Google Generative AI: {e}")
                self.google_genai_available = False
    
    async def generate_html_report(self, user_id: Optional[str] = None, user_email: Optional[str] = None) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Main method to generate HTML report for YouTube ROI:
        1. Fetch YouTube ROI metrics data from Firestore
        2. Analyze the data
        3. Generate HTML optimized for xhtml2pdf
        
        Args:
            user_id: Optional user ID to filter data
            user_email: Optional user email to filter data (takes precedence)
        """
        try:
            logger.info("🚀 Starting YouTube HTML report generation...")
            logger.info(f"🤖 AI Model Available: {self.google_genai_available}")
            if self.google_genai_available:
                logger.info(f"🤖 Using: Gemini 2.0 Flash (temperature=0.3)")
            else:
                logger.info("📋 Using: Template-based generation (fallback)")
            
            # Step 1: Fetch YouTube ROI metrics data from Firestore
            logger.info("📊 Step 1: Fetching YouTube ROI metrics from Firestore...")
            youtube_data = await self._fetch_youtube_roi_data(user_id=user_id, user_email=user_email)
            
            if not youtube_data or youtube_data.get('record_count', 0) == 0:
                logger.warning("⚠️ No YouTube ROI data found, using sample data")
                youtube_data = self._get_sample_youtube_data()
            
            # Step 2: Analyze YouTube ROI data
            logger.info("🔍 Step 2: Analyzing YouTube ROI data...")
            analysis = await self._analyze_youtube_data(youtube_data)
            
            # Step 3: Generate HTML report
            logger.info("📝 Step 3: Generating HTML report...")
            html_content = await self._generate_html_report(youtube_data, analysis)
            
            if not html_content:
                raise Exception("Failed to generate HTML content")
            
            logger.info("✅ YouTube HTML report generation completed successfully!")
            logger.info(f"📊 Final HTML content: {len(html_content)} characters")
            
            return html_content, {
                "youtube_data": youtube_data,
                "analysis": analysis,
                "generated_at": datetime.now().isoformat(),
                "user_id": user_id,
                "user_email": user_email
            }
            
        except Exception as e:
            logger.error(f"❌ YouTube HTML report generation failed: {str(e)}")
            return None, None
    
    async def _fetch_youtube_roi_data(self, user_id: Optional[str] = None, user_email: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch YouTube ROI metrics data from Firestore
        
        Args:
            user_id: Optional user ID for filtering
            user_email: Optional user email for filtering (takes precedence)
        """
        try:
            logger.info("🔍 Fetching YouTube ROI metrics from Firestore...")
            
            # Query YouTube ROI data from Firestore
            raw_data = await firestore_client.get_youtube_roi_data(
                user_id=user_id, 
                user_email=user_email, 
                limit=1000
            )
            
            if not raw_data:
                logger.warning("❌ No YouTube ROI data found in Firestore")
                return None
            
            logger.info(f"✅ Retrieved {len(raw_data)} YouTube ROI records")
            
            # Process and structure the data
            processed_data = self._process_youtube_data(raw_data)
            return processed_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching YouTube ROI data: {str(e)}")
            return None
    
    def _process_youtube_data(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process raw YouTube ROI data from Firebase ROI collection into structured format.
        Handles nested structure: metrics.views, revenue.total_revenue_usd, etc.
        """
        try:
            logger.info("🔄 Processing YouTube ROI data from Firebase...")
            
            if raw_data:
                logger.info(f"📊 Sample record structure: {list(raw_data[0].keys())}")
                logger.info(f"📊 First record sample: {json.dumps(raw_data[0], indent=2, default=str)[:500]}...")
            else:
                logger.warning("⚠️ No data to process")
                return {}
            
            # Initialize totals
            totals = {
                "total_views": 0,
                "total_likes": 0,
                "total_comments": 0,
                "total_shares": 0,
                "total_subscribers": 0,
                "total_watch_time": 0,  # in hours
                "total_cost": 0,
                "total_revenue": 0,
                "total_profit": 0,
                "total_videos": 0
            }
            
            # Track content performance by category/type
            content_categories = {}
            video_performance = []
            
            for record in raw_data:
                # Extract nested metrics with default values (Firebase ROI collection structure)
                metrics = record.get("metrics", {})
                revenue_data = record.get("revenue", {})
                costs_data = record.get("costs", {})
                roi_analysis = record.get("roi_analysis", {})
                
                views = int(metrics.get("views", 0))
                likes = int(metrics.get("likes", 0))
                comments = int(metrics.get("comments", 0))
                shares = int(metrics.get("shares", 0))
                subscribers = int(metrics.get("subscribers_gained", 0))
                retention_rate = float(metrics.get("retention_rate_percent", 0))
                
                # Revenue breakdown
                total_revenue = float(revenue_data.get("total_revenue_usd", 0))
                ad_revenue = float(revenue_data.get("ad_revenue_usd", 0))
                sponsorship_revenue = float(revenue_data.get("sponsorship_revenue_usd", 0))
                affiliate_revenue = float(revenue_data.get("affiliate_revenue_usd", 0))
                
                # Costs
                total_cost = float(costs_data.get("total_cost_usd", 0))
                production_cost = float(costs_data.get("production_cost_usd", 0))
                promotion_cost = float(costs_data.get("promotion_cost_usd", 0))
                
                # ROI metrics
                roi_percent = float(roi_analysis.get("roi_percent", 0))
                net_profit = float(roi_analysis.get("net_profit_usd", 0))
                
                category = record.get("category", "General")
                video_title = record.get("title", "Untitled Video")
                
                # Accumulate totals
                totals["total_views"] += views
                totals["total_likes"] += likes
                totals["total_comments"] += comments
                totals["total_shares"] += shares
                totals["total_subscribers"] += subscribers
                totals["total_watch_time"] += retention_rate  # Using retention rate as proxy
                totals["total_cost"] += total_cost
                totals["total_revenue"] += total_revenue
                totals["total_profit"] += net_profit
                totals["total_videos"] += 1
                
                # Track by category
                if category not in content_categories:
                    content_categories[category] = {
                        "views": 0,
                        "likes": 0,
                        "comments": 0,
                        "revenue": 0,
                        "cost": 0,
                        "profit": 0,
                        "video_count": 0
                    }
                
                content_categories[category]["views"] += views
                content_categories[category]["likes"] += likes
                content_categories[category]["comments"] += comments
                content_categories[category]["revenue"] += total_revenue
                content_categories[category]["cost"] += total_cost
                content_categories[category]["profit"] += net_profit
                content_categories[category]["video_count"] += 1
                
                # Track individual video performance (top performers)
                engagement_rate = (likes + comments + shares) / max(views, 1) * 100
                video_performance.append({
                    "title": video_title,
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "shares": shares,
                    "revenue": total_revenue,
                    "cost": total_cost,
                    "profit": net_profit,
                    "roi_percent": roi_percent,
                    "engagement_rate": engagement_rate,
                    "category": category
                })
            
            # Calculate overall ROI
            overall_roi = 0
            if totals["total_cost"] > 0:
                overall_roi = (
                    (totals["total_revenue"] - totals["total_cost"]) / 
                    totals["total_cost"]
                ) * 100
            
            # Calculate category ROI
            for category_data in content_categories.values():
                if category_data["cost"] > 0:
                    category_data["roi_percentage"] = (
                        (category_data["revenue"] - category_data["cost"]) / 
                        category_data["cost"]
                    ) * 100
                else:
                    category_data["roi_percentage"] = 0
            
            # Sort videos by views (top performers)
            top_videos = sorted(video_performance, key=lambda x: x["views"], reverse=True)[:10]
            
            # Calculate engagement metrics
            overall_engagement_rate = 0
            if totals["total_views"] > 0:
                overall_engagement_rate = (
                    (totals["total_likes"] + totals["total_comments"] + totals["total_shares"]) / 
                    totals["total_views"]
                ) * 100
            
            average_watch_time = totals["total_watch_time"] / max(totals["total_videos"], 1)
            
            processed_data = {
                "content_categories": content_categories,
                "totals": totals,
                "overall_roi": overall_roi,
                "overall_engagement_rate": overall_engagement_rate,
                "average_watch_time": average_watch_time,
                "top_videos": top_videos,
                "record_count": len(raw_data),
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Processed {len(raw_data)} YouTube records into {len(content_categories)} categories")
            return processed_data
            
        except Exception as e:
            logger.error(f"❌ Error processing YouTube data: {str(e)}")
            return {}
    
    def _format_number(self, value: float) -> str:
        """Format large numbers using scientific notation (K, M, B)"""
        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.1f}B"
        elif value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.1f}K"
        else:
            return f"{value:.0f}"
    
    def _format_currency(self, value: float) -> str:
        """Format currency values using scientific notation"""
        if value >= 1_000_000_000:
            return f"${value / 1_000_000_000:.1f}B"
        elif value >= 1_000_000:
            return f"${value / 1_000_000:.1f}M"
        elif value >= 1_000:
            return f"${value / 1_000:.1f}K"
        else:
            return f"${value:.2f}"
    
    def _get_sample_youtube_data(self) -> Dict[str, Any]:
        """Return sample YouTube ROI data for testing/demo"""
        return {
            "content_categories": {
                "Tutorial": {
                    "views": 125000,
                    "likes": 8500,
                    "comments": 1200,
                    "revenue": 4500.0,
                    "cost": 1200.0,
                    "video_count": 15,
                    "roi_percentage": 275.0
                },
                "Product Review": {
                    "views": 89000,
                    "likes": 6200,
                    "comments": 890,
                    "revenue": 3800.0,
                    "cost": 980.0,
                    "video_count": 12,
                    "roi_percentage": 287.76
                },
                "Vlog": {
                    "views": 156000,
                    "likes": 12000,
                    "comments": 2100,
                    "revenue": 5200.0,
                    "cost": 1500.0,
                    "video_count": 20,
                    "roi_percentage": 246.67
                }
            },
            "totals": {
                "total_views": 370000,
                "total_likes": 26700,
                "total_comments": 4190,
                "total_shares": 1850,
                "total_subscribers": 3500,
                "total_watch_time": 15600,  # hours
                "total_cost": 3680.0,
                "total_revenue": 13500.0,
                "total_videos": 47
            },
            "overall_roi": 266.85,
            "overall_engagement_rate": 8.85,
            "average_watch_time": 332.0,  # hours per video
            "top_videos": [
                {"title": "Ultimate Guide to Video Marketing", "views": 45000, "likes": 3200, "engagement_rate": 8.2, "revenue": 1800.0},
                {"title": "Top 10 Content Creation Tips", "views": 38000, "likes": 2800, "engagement_rate": 9.1, "revenue": 1500.0},
                {"title": "How to Grow Your YouTube Channel", "views": 32000, "likes": 2400, "engagement_rate": 8.9, "revenue": 1300.0}
            ],
            "record_count": 47,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _analyze_youtube_data(self, youtube_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze YouTube ROI data and generate insights"""
        try:
            logger.info("🔍 Analyzing YouTube ROI data...")
            
            if not self.google_genai_available or not self.model:
                logger.warning("⚠️ AI not available, using basic analysis")
                return self._basic_youtube_analysis(youtube_data)
            
            # Create analysis prompt
            analysis_prompt = self._create_youtube_analysis_prompt(youtube_data)
            
            # Generate analysis using AI
            messages = [
                SystemMessage(content="You are an expert YouTube analytics specialist and ROI analyst. Provide clear, actionable insights for content creators and marketing teams."),
                HumanMessage(content=analysis_prompt)
            ]
            
            response = await self.model.ainvoke(messages)
            analysis_text = response.content
            
            # Parse the analysis response
            analysis = self._parse_ai_analysis(analysis_text, youtube_data)
            
            logger.info("✅ YouTube ROI analysis completed")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing YouTube data: {str(e)}")
            return self._basic_youtube_analysis(youtube_data)
    
    def _create_youtube_analysis_prompt(self, youtube_data: Dict[str, Any]) -> str:
        """Create analysis prompt for YouTube ROI data"""
        return f"""
        You are a YouTube analytics expert. Analyze this comprehensive YouTube channel ROI data:

        OVERALL YOUTUBE PERFORMANCE:
        - Overall ROI: {youtube_data.get('overall_roi', 0):.2f}%
        - Total Revenue: ${youtube_data.get('totals', {}).get('total_revenue', 0):,.2f}
        - Total Cost: ${youtube_data.get('totals', {}).get('total_cost', 0):,.2f}
        - Total Views: {youtube_data.get('totals', {}).get('total_views', 0):,}
        - Total Videos: {youtube_data.get('totals', {}).get('total_videos', 0)}
        - Overall Engagement Rate: {youtube_data.get('overall_engagement_rate', 0):.2f}%
        - Total Subscribers Gained: {youtube_data.get('totals', {}).get('total_subscribers', 0):,}
        - Total Watch Time: {youtube_data.get('totals', {}).get('total_watch_time', 0):,.0f} hours

        CONTENT CATEGORY BREAKDOWN:
        {json.dumps(youtube_data.get('content_categories', {}), indent=2)}

        TOP PERFORMING VIDEOS:
        {json.dumps(youtube_data.get('top_videos', [])[:5], indent=2)}

        Provide analysis as JSON with these keys:
        {{
            "executive_summary": "comprehensive YouTube channel performance summary",
            "key_insights": ["insight 1", "insight 2", "insight 3", "insight 4", "insight 5"],
            "top_category": "best performing category with reasoning",
            "content_strategy": "detailed content strategy recommendations",
            "growth_opportunities": ["opportunity 1", "opportunity 2", "opportunity 3", "opportunity 4"],
            "audience_insights": "audience engagement and behavior analysis",
            "monetization_strategy": "revenue optimization recommendations",
            "algorithm_optimization": "YouTube algorithm optimization tips",
            "future_roadmap": "30/60/90-day action plan"
        }}

        Focus on actionable YouTube-specific insights for content creators.
        """
    
    def _parse_ai_analysis(self, analysis_text: str, youtube_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI-generated analysis response"""
        try:
            import re
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            
            if json_match:
                parsed = json.loads(json_match.group())
                return parsed
            else:
                logger.warning("⚠️ Could not parse AI analysis, using basic analysis")
                return self._basic_youtube_analysis(youtube_data)
                
        except Exception as e:
            logger.error(f"❌ Error parsing AI analysis: {str(e)}")
            return self._basic_youtube_analysis(youtube_data)
    
    def _basic_youtube_analysis(self, youtube_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic YouTube ROI analysis when AI is not available"""
        categories = youtube_data.get("content_categories", {})
        totals = youtube_data.get("totals", {})
        overall_roi = youtube_data.get("overall_roi", 0)
        engagement_rate = youtube_data.get("overall_engagement_rate", 0)
        
        # Find top performing category
        top_category = max(categories.items(), key=lambda x: x[1].get("roi_percentage", 0))[0] if categories else "None"
        
        # Generate insights
        insights = []
        if overall_roi > 200:
            insights.append(f"Exceptional YouTube ROI of {overall_roi:.1f}% - content is highly profitable")
        elif overall_roi > 100:
            insights.append(f"Strong ROI of {overall_roi:.1f}% - channel is generating solid returns")
        elif overall_roi > 0:
            insights.append(f"Positive ROI of {overall_roi:.1f}% - channel is profitable with room for optimization")
        
        if engagement_rate > 5:
            insights.append(f"Above-average engagement rate of {engagement_rate:.2f}% indicates strong audience connection")
        
        if totals.get("total_subscribers", 0) > 1000:
            insights.append(f"Growing subscriber base of {totals.get('total_subscribers', 0):,} demonstrates content appeal")
        
        insights.append(f"{totals.get('total_videos', 0)} videos generated {self._format_number(totals.get('total_views', 0))} views")
        insights.append(f"Average watch time per video: {youtube_data.get('average_watch_time', 0):.1f} hours")
        
        return {
            "executive_summary": f"YouTube channel performance shows {overall_roi:.1f}% ROI with {self._format_currency(totals.get('total_revenue', 0))} in revenue from {self._format_currency(totals.get('total_cost', 0))} investment. {top_category} category is the top performer.",
            "key_insights": insights,
            "top_category": top_category,
            "content_strategy": f"Focus on {top_category} content which shows the highest ROI. Maintain consistent upload schedule and optimize for viewer engagement.",
            "growth_opportunities": [
                "Increase video frequency in high-performing categories",
                "Optimize video titles and thumbnails for better CTR",
                "Engage with comments to boost algorithmic ranking",
                "Collaborate with other creators for cross-promotion"
            ],
            "audience_insights": f"Audience shows {engagement_rate:.2f}% engagement rate, indicating strong content-viewer alignment.",
            "monetization_strategy": "Diversify revenue streams with memberships, Super Chat, and merchandise.",
            "algorithm_optimization": "Maintain watch time above 50%, improve CTR, and post during peak audience activity times.",
            "future_roadmap": "Month 1: Optimize existing content. Month 2: Scale successful formats. Month 3: Launch new series in proven categories."
        }
    
    async def _generate_html_report(self, youtube_data: Dict[str, Any], analysis: Dict[str, Any]) -> Optional[str]:
        """Generate HTML report optimized for xhtml2pdf"""
        try:
            logger.info("📝 Generating YouTube HTML report using template...")
            
            # Use template-based generation for consistency
            html_content = self._generate_youtube_template_html(youtube_data, analysis)
            
            logger.info("✅ YouTube HTML report generated successfully")
            return html_content
            
        except Exception as e:
            logger.error(f"❌ Error generating YouTube HTML: {str(e)}")
            return None
    
    def _generate_youtube_template_html(self, youtube_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Generate HTML using template for YouTube data"""
        logger.info("📋 Building YouTube HTML template...")
        
        categories = youtube_data.get("content_categories", {})
        totals = youtube_data.get("totals", {})
        overall_roi = youtube_data.get("overall_roi", 0)
        engagement_rate = youtube_data.get("overall_engagement_rate", 0)
        top_videos = youtube_data.get("top_videos", [])
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>YouTube ROI Performance Report</title>
    <style>
        * {{ box-sizing: border-box; }}
        
        body {{
            font-family: Arial, Helvetica, sans-serif;
            margin: 0;
            padding: 15px;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.4;
            max-width: 800px;
            margin: 0 auto;
        }}
        
        .container {{
            width: 100%;
            background-color: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header {{
            text-align: center;
            border-bottom: 3px solid #FF0000;
            padding-bottom: 15px;
            margin-bottom: 25px;
        }}
        
        .header h1 {{
            color: #FF0000;
            margin: 0;
            font-size: 28px;
            font-weight: bold;
        }}
        
        .header p {{
            font-size: 16px;
            color: #6c757d;
            margin: 5px 0 0 0;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 25px;
        }}
        
        .metric-card {{
            background-color: #fff3f3;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #FF0000;
        }}
        
        .metric-value {{
            font-size: 28px;
            font-weight: bold;
            color: #FF0000;
            display: block;
            margin-bottom: 8px;
        }}
        
        .metric-label {{
            color: #6c757d;
            font-size: 14px;
            font-weight: 500;
            text-transform: uppercase;
        }}
        
        .executive-summary {{
            background-color: #fff8e1;
            border: 1px solid #ffd54f;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
        }}
        
        .executive-summary h2 {{
            color: #f57c00;
            margin-top: 0;
            font-size: 20px;
        }}
        
        .section {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #4caf50;
            margin-bottom: 20px;
        }}
        
        .section h3 {{
            color: #d32f2f;
            margin-top: 0;
            font-size: 18px;
            font-weight: bold;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
            font-size: 14px;
        }}
        
        th, td {{
            border: 1px solid #dee2e6;
            padding: 10px 8px;
            text-align: left;
        }}
        
        th {{
            background-color: #FF0000;
            color: white;
            font-weight: bold;
        }}
        
        tr:nth-child(even) {{
            background-color: #fff3f3;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 25px;
            padding-top: 15px;
            border-top: 1px solid #dee2e6;
            color: #6c757d;
        }}
        
        @media print {{
            body {{ background-color: white !important; padding: 0 !important; }}
            .container {{ box-shadow: none !important; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 YouTube ROI Performance Report</h1>
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="executive-summary">
            <h2>📊 Executive Summary</h2>
            <p>{analysis.get('executive_summary', 'Comprehensive YouTube channel performance analysis.')}</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{self._format_number(overall_roi)}%</div>
                <div class="metric-label">Overall ROI</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self._format_currency(totals.get('total_revenue', 0))}</div>
                <div class="metric-label">Total Revenue</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self._format_number(totals.get('total_views', 0))}</div>
                <div class="metric-label">Total Views</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self._format_number(totals.get('total_likes', 0))}</div>
                <div class="metric-label">Total Likes</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self._format_number(engagement_rate)}%</div>
                <div class="metric-label">Engagement Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{totals.get('total_videos', 0)}</div>
                <div class="metric-label">Total Videos</div>
            </div>
        </div>
        
        <div class="section">
            <h3>📁 Content Category Performance</h3>
            <table>
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Videos</th>
                        <th>Views</th>
                        <th>Likes</th>
                        <th>Comments</th>
                        <th>Cost</th>
                        <th>Revenue</th>
                        <th>ROI %</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Add category rows
        for category, data in categories.items():
            html_content += f"""
                    <tr>
                        <td><strong>{category}</strong></td>
                        <td>{data.get('video_count', 0)}</td>
                        <td>{self._format_number(data.get('views', 0))}</td>
                        <td>{self._format_number(data.get('likes', 0))}</td>
                        <td>{self._format_number(data.get('comments', 0))}</td>
                        <td>{self._format_currency(data.get('cost', 0))}</td>
                        <td>{self._format_currency(data.get('revenue', 0))}</td>
                        <td>{self._format_number(data.get('roi_percentage', 0))}%</td>
                    </tr>
            """
        
        html_content += f"""
                    <tr style="background-color: #ffe0e0; font-weight: bold;">
                        <td><strong>Totals</strong></td>
                        <td>{totals.get('total_videos', 0)}</td>
                        <td>{self._format_number(totals.get('total_views', 0))}</td>
                        <td>{self._format_number(totals.get('total_likes', 0))}</td>
                        <td>{self._format_number(totals.get('total_comments', 0))}</td>
                        <td>{self._format_currency(totals.get('total_cost', 0))}</td>
                        <td>{self._format_currency(totals.get('total_revenue', 0))}</td>
                        <td>{self._format_number(overall_roi)}%</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h3>🏆 Top Performing Videos</h3>
            <table>
                <thead>
                    <tr>
                        <th>Video Title</th>
                        <th>Views</th>
                        <th>Likes</th>
                        <th>Engagement %</th>
                        <th>Revenue</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Add top video rows
        for video in top_videos[:5]:
            html_content += f"""
                    <tr>
                        <td>{video.get('title', 'Untitled')[:40]}</td>
                        <td>{self._format_number(video.get('views', 0))}</td>
                        <td>{self._format_number(video.get('likes', 0))}</td>
                        <td>{video.get('engagement_rate', 0):.2f}%</td>
                        <td>{self._format_currency(video.get('revenue', 0))}</td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h3>💡 Key Insights</h3>
            <ul>
        """
        
        for insight in analysis.get('key_insights', []):
            html_content += f"<li>{insight}</li>"
        
        html_content += f"""
            </ul>
        </div>
        
        <div class="section">
            <h3>🎯 Content Strategy Recommendations</h3>
            <p><strong>Top Category:</strong> {analysis.get('top_category', 'N/A')}</p>
            <p>{analysis.get('content_strategy', 'Focus on creating consistent, high-quality content.')}</p>
        </div>
        
        <div class="section">
            <h3>📈 Growth Opportunities</h3>
            <ul>
        """
        
        for opportunity in analysis.get('growth_opportunities', []):
            html_content += f"<li>{opportunity}</li>"
        
        html_content += f"""
            </ul>
        </div>
        
        <div class="section">
            <h3>🎬 YouTube Algorithm Optimization</h3>
            <p>{analysis.get('algorithm_optimization', 'Optimize for watch time and engagement.')}</p>
        </div>
        
        <div class="section">
            <h3>🗺️ Future Roadmap</h3>
            <p>{analysis.get('future_roadmap', 'Strategic growth plan for the next 90 days.')}</p>
        </div>
        
        <div class="footer">
            <p>Report generated by BOS Solution YouTube Analytics | {datetime.now().year}</p>
        </div>
    </div>
</body>
</html>
        """
        
        logger.info(f"✅ YouTube template HTML completed: {len(html_content)} characters")
        return html_content


if __name__ == "__main__":
    # Test the agent
    async def test():
        agent = YouTubeROIReportAgent()
        html_content, report_data = await agent.generate_html_report()
        print(f"HTML generated: {len(html_content) if html_content else 0} characters")
        print(f"Report data: {bool(report_data)}")
    
    asyncio.run(test())
