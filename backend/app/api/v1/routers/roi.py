"""
ROI (Return on Investment) API endpoints for YouTube analytics
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.core.firebase import get_db
from app.core.auth import get_current_user

router = APIRouter(prefix="/roi", tags=["ROI Analytics"])


@router.get("/videos")
async def get_user_roi_videos(
    current_user: dict = Depends(get_current_user),
    limit: Optional[int] = 50,
    category: Optional[str] = None
):
    """
    Get all ROI video data for the current user with optional filtering
    """
    try:
        db = get_db()
        user_email = current_user.get("email")
        
        if not user_email:
            raise HTTPException(status_code=400, detail="User email not found")
        
        # Query Firestore for user's videos
        query = db.collection('ROI').where('user_email', '==', user_email)
        
        # Apply category filter if specified
        if category:
            query = query.where('category', '==', category)
        
        # Limit results
        query = query.limit(limit)
        
        # Execute query
        docs = query.stream()
        
        videos = []
        for doc in docs:
            video_data = doc.to_dict()
            video_data['id'] = doc.id
            videos.append(video_data)
        
        # Sort by publish date (most recent first)
        videos.sort(key=lambda x: x.get('publish_date', ''), reverse=True)
        
        return {
            "success": True,
            "count": len(videos),
            "videos": videos
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching ROI data: {str(e)}")


@router.get("/analytics/summary")
async def get_roi_analytics_summary(
    current_user: dict = Depends(get_current_user),
    days: Optional[int] = 30
):
    """
    Get comprehensive ROI analytics summary for the current user
    Includes total revenue, costs, profit, ROI metrics, and trends
    """
    try:
        db = get_db()
        user_email = current_user.get("email")
        
        if not user_email:
            raise HTTPException(status_code=400, detail="User email not found")
        
        # Calculate date threshold for filtering
        date_threshold = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Query all user videos
        query = db.collection('ROI').where('user_email', '==', user_email)
        docs = query.stream()
        
        videos = [doc.to_dict() for doc in docs]
        
        if not videos:
            return {
                "success": True,
                "message": "No ROI data found",
                "analytics": None
            }
        
        # Filter videos by date range for trends
        recent_videos = [
            v for v in videos 
            if v.get('publish_date', '') >= date_threshold
        ]
        
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
        
        # Cost breakdown
        total_production_cost = sum(v['costs']['production_cost_usd'] for v in videos)
        total_promotion_cost = sum(v['costs']['promotion_cost_usd'] for v in videos)
        
        # Engagement metrics
        total_likes = sum(v['metrics']['likes'] for v in videos)
        total_comments = sum(v['metrics']['comments'] for v in videos)
        total_shares = sum(v['metrics']['shares'] for v in videos)
        total_subscribers = sum(v['metrics']['subscribers_gained'] for v in videos)
        avg_retention = sum(v['metrics']['retention_rate_percent'] for v in videos) / total_videos
        avg_ctr = sum(v['metrics']['ctr_percent'] for v in videos) / total_videos
        
        # Per video averages
        avg_views = total_views / total_videos
        avg_revenue = total_revenue / total_videos
        avg_cost = total_cost / total_videos
        avg_profit = total_profit / total_videos
        avg_roi = sum(v['roi_analysis']['roi_percent'] for v in videos) / total_videos
        
        # Find best and worst performing videos
        best_video = max(videos, key=lambda x: x['roi_analysis']['roi_percent'])
        worst_video = min(videos, key=lambda x: x['roi_analysis']['roi_percent'])
        most_viewed = max(videos, key=lambda x: x['metrics']['views'])
        
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
        
        # Calculate average ROI per category
        for category in category_stats:
            count = category_stats[category]['count']
            category_stats[category]['avg_roi'] = category_stats[category]['total_roi'] / count
            category_stats[category]['avg_revenue'] = category_stats[category]['total_revenue'] / count
            category_stats[category]['profit'] = category_stats[category]['total_revenue'] - category_stats[category]['total_cost']
        
        # Monthly trend data (last 6 months)
        monthly_data = {}
        for video in videos:
            try:
                pub_date = datetime.fromisoformat(video['publish_date'].replace('Z', '+00:00'))
                month_key = pub_date.strftime('%Y-%m')
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        'month': month_key,
                        'videos': 0,
                        'revenue': 0,
                        'cost': 0,
                        'profit': 0,
                        'views': 0
                    }
                
                monthly_data[month_key]['videos'] += 1
                monthly_data[month_key]['revenue'] += video['revenue']['total_revenue_usd']
                monthly_data[month_key]['cost'] += video['costs']['total_cost_usd']
                monthly_data[month_key]['profit'] += video['roi_analysis']['net_profit_usd']
                monthly_data[month_key]['views'] += video['metrics']['views']
            except:
                continue
        
        # Convert to sorted list
        monthly_trend = sorted(monthly_data.values(), key=lambda x: x['month'])
        
        # Recent performance (last 30 days)
        recent_metrics = {
            'videos': len(recent_videos),
            'revenue': sum(v['revenue']['total_revenue_usd'] for v in recent_videos),
            'cost': sum(v['costs']['total_cost_usd'] for v in recent_videos),
            'views': sum(v['metrics']['views'] for v in recent_videos),
        }
        recent_metrics['profit'] = recent_metrics['revenue'] - recent_metrics['cost']
        recent_metrics['roi'] = ((recent_metrics['revenue'] - recent_metrics['cost']) / recent_metrics['cost'] * 100) if recent_metrics['cost'] > 0 else 0
        
        return {
            "success": True,
            "analytics": {
                "overview": {
                    "total_videos": total_videos,
                    "total_views": total_views,
                    "total_revenue": round(total_revenue, 2),
                    "total_cost": round(total_cost, 2),
                    "total_profit": round(total_profit, 2),
                    "overall_roi": round(overall_roi, 2),
                    "avg_views_per_video": round(avg_views, 0),
                    "avg_revenue_per_video": round(avg_revenue, 2),
                    "avg_cost_per_video": round(avg_cost, 2),
                    "avg_profit_per_video": round(avg_profit, 2),
                    "avg_roi_per_video": round(avg_roi, 2),
                },
                "revenue_breakdown": {
                    "ad_revenue": round(total_ad_revenue, 2),
                    "sponsorship_revenue": round(total_sponsorship, 2),
                    "affiliate_revenue": round(total_affiliate, 2),
                    "ad_revenue_percent": round((total_ad_revenue / total_revenue * 100) if total_revenue > 0 else 0, 1),
                    "sponsorship_percent": round((total_sponsorship / total_revenue * 100) if total_revenue > 0 else 0, 1),
                    "affiliate_percent": round((total_affiliate / total_revenue * 100) if total_revenue > 0 else 0, 1),
                },
                "cost_breakdown": {
                    "production_cost": round(total_production_cost, 2),
                    "promotion_cost": round(total_promotion_cost, 2),
                    "production_percent": round((total_production_cost / total_cost * 100) if total_cost > 0 else 0, 1),
                    "promotion_percent": round((total_promotion_cost / total_cost * 100) if total_cost > 0 else 0, 1),
                },
                "engagement": {
                    "total_likes": total_likes,
                    "total_comments": total_comments,
                    "total_shares": total_shares,
                    "total_subscribers_gained": total_subscribers,
                    "avg_retention_rate": round(avg_retention, 2),
                    "avg_ctr": round(avg_ctr, 2),
                },
                "top_performers": {
                    "best_roi_video": {
                        "title": best_video['title'],
                        "roi": round(best_video['roi_analysis']['roi_percent'], 2),
                        "profit": round(best_video['roi_analysis']['net_profit_usd'], 2),
                    },
                    "worst_roi_video": {
                        "title": worst_video['title'],
                        "roi": round(worst_video['roi_analysis']['roi_percent'], 2),
                        "profit": round(worst_video['roi_analysis']['net_profit_usd'], 2),
                    },
                    "most_viewed_video": {
                        "title": most_viewed['title'],
                        "views": most_viewed['metrics']['views'],
                        "revenue": round(most_viewed['revenue']['total_revenue_usd'], 2),
                    },
                },
                "category_performance": category_stats,
                "monthly_trend": monthly_trend,
                "recent_performance": {
                    "days": days,
                    "metrics": recent_metrics
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating analytics: {str(e)}")


@router.get("/analytics/chart-data")
async def get_chart_data(
    current_user: dict = Depends(get_current_user),
    chart_type: str = "revenue_vs_cost"
):
    """
    Get formatted data specifically for charts
    Supports: revenue_vs_cost, roi_trend, category_comparison, revenue_sources
    """
    try:
        db = get_db()
        user_email = current_user.get("email")
        
        if not user_email:
            raise HTTPException(status_code=400, detail="User email not found")
        
        # Query user videos
        query = db.collection('ROI').where('user_email', '==', user_email)
        docs = query.stream()
        videos = [doc.to_dict() for doc in docs]
        
        if not videos:
            return {"success": True, "data": []}
        
        if chart_type == "revenue_vs_cost":
            # Monthly revenue vs cost comparison
            monthly_data = {}
            for video in videos:
                try:
                    pub_date = datetime.fromisoformat(video['publish_date'].replace('Z', '+00:00'))
                    month_key = pub_date.strftime('%b %Y')
                    
                    if month_key not in monthly_data:
                        monthly_data[month_key] = {'revenue': 0, 'cost': 0, 'profit': 0}
                    
                    monthly_data[month_key]['revenue'] += video['revenue']['total_revenue_usd']
                    monthly_data[month_key]['cost'] += video['costs']['total_cost_usd']
                    monthly_data[month_key]['profit'] += video['roi_analysis']['net_profit_usd']
                except:
                    continue
            
            return {
                "success": True,
                "data": [
                    {
                        "month": month,
                        "revenue": round(data['revenue'], 2),
                        "cost": round(data['cost'], 2),
                        "profit": round(data['profit'], 2)
                    }
                    for month, data in sorted(monthly_data.items())
                ]
            }
        
        elif chart_type == "roi_trend":
            # ROI percentage over time
            sorted_videos = sorted(videos, key=lambda x: x.get('publish_date', ''))
            return {
                "success": True,
                "data": [
                    {
                        "date": v['publish_date'][:10],
                        "title": v['title'][:30] + "...",
                        "roi": round(v['roi_analysis']['roi_percent'], 2),
                        "profit": round(v['roi_analysis']['net_profit_usd'], 2)
                    }
                    for v in sorted_videos[-20:]  # Last 20 videos
                ]
            }
        
        elif chart_type == "category_comparison":
            # Compare performance by category
            category_data = {}
            for video in videos:
                category = video.get('category', 'Other')
                if category not in category_data:
                    category_data[category] = {
                        'count': 0,
                        'revenue': 0,
                        'cost': 0,
                        'views': 0,
                        'roi_sum': 0
                    }
                category_data[category]['count'] += 1
                category_data[category]['revenue'] += video['revenue']['total_revenue_usd']
                category_data[category]['cost'] += video['costs']['total_cost_usd']
                category_data[category]['views'] += video['metrics']['views']
                category_data[category]['roi_sum'] += video['roi_analysis']['roi_percent']
            
            return {
                "success": True,
                "data": [
                    {
                        "category": cat,
                        "videos": data['count'],
                        "revenue": round(data['revenue'], 2),
                        "cost": round(data['cost'], 2),
                        "profit": round(data['revenue'] - data['cost'], 2),
                        "views": data['views'],
                        "avg_roi": round(data['roi_sum'] / data['count'], 2)
                    }
                    for cat, data in category_data.items()
                ]
            }
        
        elif chart_type == "revenue_sources":
            # Revenue source breakdown (pie chart data)
            total_ad = sum(v['revenue']['ad_revenue_usd'] for v in videos)
            total_sponsor = sum(v['revenue']['sponsorship_revenue_usd'] for v in videos)
            total_affiliate = sum(v['revenue']['affiliate_revenue_usd'] for v in videos)
            
            return {
                "success": True,
                "data": [
                    {"name": "Ad Revenue", "value": round(total_ad, 2)},
                    {"name": "Sponsorships", "value": round(total_sponsor, 2)},
                    {"name": "Affiliate", "value": round(total_affiliate, 2)},
                ]
            }
        
        else:
            raise HTTPException(status_code=400, detail="Invalid chart_type")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating chart data: {str(e)}")
