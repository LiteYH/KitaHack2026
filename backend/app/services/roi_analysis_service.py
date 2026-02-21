"""
ROI Analysis Service for Chat Integration
Analyzes user questions about ROI data and generates structured responses with chart configurations

Implements Human-in-the-Loop (HITL) pattern for user confirmation before accessing sensitive ROI data
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import re
import uuid
from app.core.firebase import get_db


class ROIAnalysisService:
    """Service for analyzing ROI queries and generating chart data with HITL confirmation"""
    
    def __init__(self):
        self.db = get_db()
        # Store pending confirmation requests (in production, use Redis or database)
        self._pending_confirmations: Dict[str, Dict[str, Any]] = {}
    
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
    
    def create_confirmation_request(
        self,
        user_message: str,
        user_email: str,
        days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a HITL confirmation request for accessing ROI data
        
        Args:
            user_message: User's original query
            user_email: User's email
            days: Optional time period extracted from query
            
        Returns:
            Confirmation request data with unique action_id
        """
        action_id = str(uuid.uuid4())
        
        # Store pending confirmation with context
        self._pending_confirmations[action_id] = {
            "user_message": user_message,
            "user_email": user_email,
            "days": days,
            "timestamp": datetime.now().isoformat()
        }
        
        # Create user-friendly message
        period_text = f" from the last {days} days" if days else ""
        confirmation_message = f"""🔒 **Data Access Request**

I need your permission to access your ROI data from Firebase{period_text} to answer your question.

**What I'll access:**
- Video performance metrics (views, engagement)
- Revenue and cost data  
- ROI calculations and trends

**Your data privacy:**
- ✅ Only your data will be accessed
- ✅ No data will be shared or stored beyond this analysis
- ✅ You can cancel this request at any time

**Do you confirm access to your ROI data?**"""
        
        return {
            "action_type": "roi_data_access",
            "message": confirmation_message,
            "action_id": action_id,
            "details": {
                "period_days": days,
                "query": user_message
            }
        }
    
    def check_confirmation(self, action_id: str) -> Optional[Dict[str, Any]]:
        """
        Check if a pending confirmation exists
        
        Args:
            action_id: Unique action identifier
            
        Returns:
            Pending confirmation data or None
        """
        return self._pending_confirmations.get(action_id)
    
    def cancel_confirmation(self, action_id: str) -> bool:
        """
        Cancel a pending confirmation request
        
        Args:
            action_id: Unique action identifier
            
        Returns:
            True if cancelled, False if not found
        """
        if action_id in self._pending_confirmations:
            del self._pending_confirmations[action_id]
            return True
        return False
    
    def cleanup_old_confirmations(self, max_age_minutes: int = 30):
        """
        Clean up old pending confirmations (prevent memory leaks)
        
        Args:
            max_age_minutes: Maximum age of confirmations to keep
        """
        now = datetime.now()
        expired_ids = []
        
        for action_id, data in self._pending_confirmations.items():
            timestamp = datetime.fromisoformat(data["timestamp"])
            age = (now - timestamp).total_seconds() / 60
            
            if age > max_age_minutes:
                expired_ids.append(action_id)
        
        for action_id in expired_ids:
            del self._pending_confirmations[action_id]
        
        if expired_ids:
            print(f"🧹 Cleaned up {len(expired_ids)} expired confirmation requests")
    
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
            # Check if database is initialized
            if self.db is None:
                return []
            
            # Build and execute query
            collection_ref = self.db.collection('ROI')
            query = collection_ref.where('user_email', '==', user_email)
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
            import traceback
            traceback.print_exc()
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
        
        try:
            # Calculate overall metrics
            total_videos = len(videos)
            total_views = sum(v['metrics']['views'] for v in videos)
            total_revenue = sum(v['revenue']['total_revenue_usd'] for v in videos)
            total_cost = sum(v['costs']['total_cost_usd'] for v in videos)
            total_profit = total_revenue - total_cost
            overall_roi = ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0
            
        except KeyError as e:
            return {
                "found_data": False,
                "error": f"Data structure mismatch: missing field {e}",
                "message": "ROI data found but has incorrect structure. Please check Firebase data format.",
                "debug_info": {
                    "found_videos": len(videos),
                    "available_fields": list(videos[0].keys()) if videos else [],
                    "missing_field": str(e)
                }
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "found_data": False,
                "error": f"Analysis failed: {str(e)}",
                "message": "An error occurred while analyzing ROI data."
            }
        
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
        user_email: str,
        skip_confirmation: bool = False
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Process a user's ROI query with HITL confirmation
        
        Args:
            user_message: User's question
            user_email: User's email for data fetching
            skip_confirmation: If True, skip confirmation (for confirmed requests)
            
        Returns:
            Tuple of (analysis_dict, chart_configs, confirmation_request)
            If confirmation_request is not None, user confirmation is required
        """
        # Extract time period
        days = self.extract_time_period(user_message)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # HUMAN-IN-THE-LOOP: Request confirmation before accessing data
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        if not skip_confirmation:
            print(f"🔒 [HITL] User confirmation required for data access")
            confirmation_request = self.create_confirmation_request(
                user_message=user_message,
                user_email=user_email,
                days=days
            )
            
            # Return empty analysis with confirmation request
            return {
                "found_data": False,
                "pending_confirmation": True,
                "message": "Waiting for user confirmation..."
            }, [], confirmation_request
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Confirmation granted - proceed with data access
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        print(f"\n{'='*60}")
        print(f"✅ [HITL] User confirmed - processing ROI query")
        print(f"{'='*60}")
        print(f"   User: {user_email}")
        print(f"   Query: {user_message}")
        print(f"   Period: {f'{days} days' if days else 'All time'}")
        print(f"{'='*60}\n")
        
        # Fetch ROI data from Firebase
        videos = await self.fetch_user_roi_data(user_email, days)
        
        print(f"📤 [PROCESS] Fetched {len(videos)} video(s) from Firebase")
        
        # Analyze data
        analysis = self.analyze_roi_data(videos)
        
        print(f"📈 [PROCESS] Analysis completed: found_data = {analysis.get('found_data', False)}")
        
        # Prepare data for AI analysis
        data_for_ai = self.prepare_analysis_for_ai(analysis, days)
        
        # Generate charts
        charts = self.generate_chart_config(analysis)
        
        print(f"📊 [PROCESS] Generated {len(charts)} chart configuration(s)")
        print(f"{'='*60}\n")
        
        # Return structured data with AI-ready context
        return {
            "found_data": analysis.get("found_data", False),
            "data_summary": data_for_ai,
            "user_query": user_message,
            "period_days": days,
            "raw_analysis": analysis
        }, charts, None
    
    async def process_confirmed_roi_query(
        self,
        action_id: str
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Process a confirmed ROI query after user approval
        
        Args:
            action_id: ID of the confirmed action
            
        Returns:
            Tuple of (analysis_dict, chart_configs)
        """
        # Retrieve pending confirmation
        pending = self.check_confirmation(action_id)
        
        if not pending:
            return {
                "found_data": False,
                "error": "Confirmation request expired or not found"
            }, []
        
        # Clean up stale confirmations
        self.cleanup_old_confirmations()
        
        # Extract original request data
        user_message = pending["user_message"]
        user_email = pending["user_email"]
        
        # Remove from pending (one-time use)
        self.cancel_confirmation(action_id)
        
        # Process the query with confirmation skipped
        analysis, charts, _ = await self.process_roi_query(
            user_message=user_message,
            user_email=user_email,
            skip_confirmation=True
        )
        
        return analysis, charts


# Singleton instance
roi_analysis_service = ROIAnalysisService()
