"""
ROI Analysis Service for Chat Integration
Analyzes user questions about ROI data and generates structured responses with chart configurations
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import re
from app.core.firebase import get_db


class ROIAnalysisService:
    """Service for analyzing ROI queries and generating chart data"""
    
    def __init__(self):
        self.db = get_db()
    
    def detect_roi_query(self, message: str) -> bool:
        """
        Detect if the user's message is asking about ROI data
        
        Args:
            message: User's message
            
        Returns:
            True if message is ROI-related
        """
        roi_keywords = [
            'roi', 'return on investment', 'revenue', 'profit', 'cost',
            'earning', 'income', 'performance', 'analytics', 'metrics',
            'views', 'video', 'youtube', 'content', 'engagement',
            'days ago', 'last week', 'last month', 'this week', 'this month'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in roi_keywords)
    
    def extract_time_period(self, message: str) -> Optional[int]:
        """
        Extract time period in days from the message
        
        Args:
            message: User's message
            
        Returns:
            Number of days or None
        """
        # Pattern: "X days ago", "last X days", "past X days"
        patterns = [
            r'(\d+)\s*days?\s*ago',
            r'last\s*(\d+)\s*days?',
            r'past\s*(\d+)\s*days?',
            r'(\d+)\s*days?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                return int(match.group(1))
        
        # Handle weeks and months
        if 'last week' in message.lower() or 'this week' in message.lower():
            return 7
        elif 'last month' in message.lower() or 'this month' in message.lower():
            return 30
        elif '2 weeks' in message.lower():
            return 14
        
        return None
    
    async def fetch_user_roi_data(
        self, 
        user_email: str, 
        days: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch ROI data for a specific user from Firebase
        
        Args:
            user_email: User's email
            days: Optional number of days to look back
            
        Returns:
            List of video ROI data
        """
        try:
            query = self.db.collection('ROI').where('user_email', '==', user_email)
            docs = query.stream()
            
            videos = []
            for doc in docs:
                video_data = doc.to_dict()
                video_data['id'] = doc.id
                videos.append(video_data)
            
            # Filter by date if specified
            if days is not None:
                date_threshold = (datetime.now() - timedelta(days=days)).isoformat()
                videos = [
                    v for v in videos 
                    if v.get('publish_date', '') >= date_threshold
                ]
            
            return videos
            
        except Exception as e:
            print(f"Error fetching ROI data: {str(e)}")
            return []
    
    def analyze_roi_data(
        self, 
        videos: List[Dict[str, Any]], 
        query_type: str = "overview"
    ) -> Dict[str, Any]:
        """
        Analyze ROI data and generate insights
        
        Args:
            videos: List of video data
            query_type: Type of analysis (overview, trends, categories, etc.)
            
        Returns:
            Analysis results with metrics and insights
        """
        if not videos:
            return {
                "found_data": False,
                "message": "No ROI data found for the specified period."
            }
        
        # Calculate overall metrics
        total_videos = len(videos)
        total_views = sum(v['metrics']['views'] for v in videos)
        total_revenue = sum(v['revenue']['total_revenue_usd'] for v in videos)
        total_cost = sum(v['costs']['total_cost_usd'] for v in videos)
        total_profit = total_revenue - total_cost
        overall_roi = ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0
        
        # Revenue breakdown
        total_ad_revenue = sum(v['revenue']['ad_revenue_usd'] for v in videos)
        total_sponsorship = sum(v['revenue']['sponsorship_revenue_usd'] for v in videos)
        total_affiliate = sum(v['revenue']['affiliate_revenue_usd'] for v in videos)
        
        # Engagement metrics
        total_likes = sum(v['metrics']['likes'] for v in videos)
        total_comments = sum(v['metrics']['comments'] for v in videos)
        avg_retention = sum(v['metrics']['retention_rate_percent'] for v in videos) / total_videos
        
        # Find best performing video
        best_video = max(videos, key=lambda x: x['roi_analysis']['roi_percent'])
        
        # Category performance
        category_stats = {}
        for video in videos:
            category = video.get('category', 'Uncategorized')
            if category not in category_stats:
                category_stats[category] = {
                    'count': 0,
                    'total_revenue': 0,
                    'total_cost': 0,
                    'total_views': 0,
                    'total_roi': 0
                }
            category_stats[category]['count'] += 1
            category_stats[category]['total_revenue'] += video['revenue']['total_revenue_usd']
            category_stats[category]['total_cost'] += video['costs']['total_cost_usd']
            category_stats[category]['total_views'] += video['metrics']['views']
            category_stats[category]['total_roi'] += video['roi_analysis']['roi_percent']
        
        # Calculate averages per category
        for category in category_stats:
            count = category_stats[category]['count']
            category_stats[category]['avg_roi'] = category_stats[category]['total_roi'] / count
            category_stats[category]['profit'] = category_stats[category]['total_revenue'] - category_stats[category]['total_cost']
        
        # Time-based trend
        videos_sorted = sorted(videos, key=lambda x: x.get('publish_date', ''))
        daily_data = {}
        for video in videos_sorted:
            try:
                pub_date = datetime.fromisoformat(video['publish_date'].replace('Z', '+00:00'))
                date_key = pub_date.strftime('%Y-%m-%d')
                
                if date_key not in daily_data:
                    daily_data[date_key] = {
                        'date': date_key,
                        'videos': 0,
                        'revenue': 0,
                        'cost': 0,
                        'profit': 0,
                        'views': 0,
                        'roi': 0
                    }
                
                daily_data[date_key]['videos'] += 1
                daily_data[date_key]['revenue'] += video['revenue']['total_revenue_usd']
                daily_data[date_key]['cost'] += video['costs']['total_cost_usd']
                daily_data[date_key]['profit'] += video['roi_analysis']['net_profit_usd']
                daily_data[date_key]['views'] += video['metrics']['views']
                daily_data[date_key]['roi'] += video['roi_analysis']['roi_percent']
            except:
                continue
        
        # Calculate average ROI per day
        for date_key in daily_data:
            video_count = daily_data[date_key]['videos']
            if video_count > 0:
                daily_data[date_key]['roi'] = daily_data[date_key]['roi'] / video_count
        
        trend_data = sorted(daily_data.values(), key=lambda x: x['date'])
        
        return {
            "found_data": True,
            "summary": {
                "total_videos": total_videos,
                "total_views": total_views,
                "total_revenue": total_revenue,
                "total_cost": total_cost,
                "total_profit": total_profit,
                "overall_roi": overall_roi,
                "ad_revenue": total_ad_revenue,
                "sponsorship_revenue": total_sponsorship,
                "affiliate_revenue": total_affiliate,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "avg_retention": avg_retention
            },
            "best_video": {
                "title": best_video.get('title', 'Unknown'),
                "roi": best_video['roi_analysis']['roi_percent'],
                "revenue": best_video['revenue']['total_revenue_usd'],
                "views": best_video['metrics']['views']
            },
            "categories": category_stats,
            "trend": trend_data,
            "videos": videos
        }
    
    def generate_chart_config(
        self, 
        analysis: Dict[str, Any], 
        chart_type: str = "auto"
    ) -> List[Dict[str, Any]]:
        """
        Generate chart configurations based on analysis
        
        Args:
            analysis: Analysis results
            chart_type: Type of chart to generate (auto, line, bar, pie)
            
        Returns:
            List of chart configurations
        """
        if not analysis.get("found_data"):
            return []
        
        charts = []
        summary = analysis.get("summary", {})
        
        # 1. Revenue vs Cost vs Profit Overview (Bar Chart)
        charts.append({
            "type": "bar",
            "title": "Revenue, Cost & Profit Overview",
            "data": [
                {
                    "name": "Total Revenue",
                    "value": round(summary.get("total_revenue", 0), 2),
                    "color": "#10b981"
                },
                {
                    "name": "Total Cost",
                    "value": round(summary.get("total_cost", 0), 2),
                    "color": "#ef4444"
                },
                {
                    "name": "Net Profit",
                    "value": round(summary.get("total_profit", 0), 2),
                    "color": "#3b82f6"
                }
            ],
            "xKey": "name",
            "yKey": "value",
            "yLabel": "Amount (USD)"
        })
        
        # 2. Revenue Breakdown (Pie Chart)
        if summary.get("ad_revenue", 0) + summary.get("sponsorship_revenue", 0) + summary.get("affiliate_revenue", 0) > 0:
            charts.append({
                "type": "pie",
                "title": "Revenue Sources Breakdown",
                "data": [
                    {
                        "name": "Ad Revenue",
                        "value": round(summary.get("ad_revenue", 0), 2),
                        "color": "#8b5cf6"
                    },
                    {
                        "name": "Sponsorships",
                        "value": round(summary.get("sponsorship_revenue", 0), 2),
                        "color": "#ec4899"
                    },
                    {
                        "name": "Affiliates",
                        "value": round(summary.get("affiliate_revenue", 0), 2),
                        "color": "#f59e0b"
                    }
                ]
            })
        
        # 3. Performance Trend Over Time (Line Chart)
        trend_data = analysis.get("trend", [])
        if len(trend_data) > 1:
            charts.append({
                "type": "line",
                "title": "ROI & Profit Trend Over Time",
                "data": [
                    {
                        "date": item["date"],
                        "ROI": round(item["roi"], 2),
                        "Profit": round(item["profit"], 2)
                    }
                    for item in trend_data
                ],
                "xKey": "date",
                "lines": [
                    {"key": "ROI", "color": "#10b981", "label": "ROI (%)"},
                    {"key": "Profit", "color": "#3b82f6", "label": "Profit (USD)"}
                ]
            })
        
        # 4. Category Performance (Bar Chart)
        categories = analysis.get("categories", {})
        if categories:
            category_data = [
                {
                    "category": cat,
                    "roi": round(stats["avg_roi"], 2),
                    "profit": round(stats["profit"], 2),
                    "videos": stats["count"]
                }
                for cat, stats in categories.items()
            ]
            category_data.sort(key=lambda x: x["roi"], reverse=True)
            
            charts.append({
                "type": "bar",
                "title": "Category Performance (Avg ROI)",
                "data": category_data,
                "xKey": "category",
                "yKey": "roi",
                "yLabel": "Average ROI (%)"
            })
        
        return charts
    
    def prepare_analysis_for_ai(
        self, 
        analysis: Dict[str, Any], 
        days: Optional[int] = None
    ) -> str:
        """
        Prepare structured analysis data for AI to interpret
        
        Args:
            analysis: Analysis results
            days: Number of days analyzed
            
        Returns:
            Structured data string for AI analysis
        """
        if not analysis.get("found_data"):
            return "No ROI data found for the specified period."
        
        summary = analysis.get("summary", {})
        best_video = analysis.get("best_video", {})
        categories = analysis.get("categories", {})
        
        period_text = f"the last {days} days" if days else "all time"
        
        # Prepare structured data for AI
        data_summary = f"""ROI Data Analysis for {period_text}:

OVERALL PERFORMANCE:
- Total Videos: {summary.get('total_videos', 0)}
- Total Views: {summary.get('total_views', 0):,}
- Total Revenue: ${summary.get('total_revenue', 0):,.2f}
- Total Cost: ${summary.get('total_cost', 0):,.2f}
- Net Profit: ${summary.get('total_profit', 0):,.2f}
- Overall ROI: {summary.get('overall_roi', 0):.2f}%

REVENUE BREAKDOWN:
- Ad Revenue: ${summary.get('ad_revenue', 0):,.2f}
- Sponsorship Revenue: ${summary.get('sponsorship_revenue', 0):,.2f}
- Affiliate Revenue: ${summary.get('affiliate_revenue', 0):,.2f}

ENGAGEMENT METRICS:
- Total Likes: {summary.get('total_likes', 0):,}
- Total Comments: {summary.get('total_comments', 0):,}
- Average Retention Rate: {summary.get('avg_retention', 0):.2f}%

BEST PERFORMING VIDEO:
- Title: {best_video.get('title', 'Unknown')}
- ROI: {best_video.get('roi', 0):.2f}%
- Revenue: ${best_video.get('revenue', 0):,.2f}
- Views: {best_video.get('views', 0):,}
"""
        
        # Add category performance if available
        if categories:
            data_summary += "\nCATEGORY PERFORMANCE:\n"
            sorted_categories = sorted(
                categories.items(), 
                key=lambda x: x[1].get('avg_roi', 0), 
                reverse=True
            )
            for cat, stats in sorted_categories[:5]:  # Top 5 categories
                data_summary += f"- {cat}: Avg ROI {stats.get('avg_roi', 0):.2f}%, {stats.get('count', 0)} videos, Profit ${stats.get('profit', 0):,.2f}\n"
        
        return data_summary
    
    async def process_roi_query(
        self, 
        user_message: str, 
        user_email: str
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Process a user's ROI query and return analysis data + charts
        
        Args:
            user_message: User's question
            user_email: User's email for data fetching
            
        Returns:
            Tuple of (analysis_dict, chart_configs)
        """
        # Extract time period
        days = self.extract_time_period(user_message)
        
        # Fetch ROI data from Firebase
        videos = await self.fetch_user_roi_data(user_email, days)
        
        # Analyze data
        analysis = self.analyze_roi_data(videos)
        
        # Prepare data for AI analysis
        data_for_ai = self.prepare_analysis_for_ai(analysis, days)
        
        # Generate charts
        charts = self.generate_chart_config(analysis)
        
        # Return structured data with AI-ready context
        return {
            "found_data": analysis.get("found_data", False),
            "data_summary": data_for_ai,
            "user_query": user_message,
            "period_days": days,
            "raw_analysis": analysis
        }, charts


# Singleton instance
roi_analysis_service = ROIAnalysisService()
