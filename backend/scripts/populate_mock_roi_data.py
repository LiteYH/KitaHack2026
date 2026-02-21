"""
Script to populate mock YouTube video ROI data for testing purposes.
This creates sample video performance data that can be used for ROI calculations.
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta
import random
from app.core.firebase import initialize_firebase

def generate_mock_youtube_videos(user_email: str, num_videos: int = 10):
    """
    Generate mock YouTube video data with ROI metrics for a specific user.
    
    Args:
        user_email: Email of the user who owns these videos
        num_videos: Number of mock videos to generate
    """
    
    # Initialize Firebase
    app, db = initialize_firebase()
    
    if db is None:
        print("❌ Firebase not initialized. Cannot populate data.")
        return
    
    # Video title templates for variety
    video_titles = [
        "Ultimate Guide to Digital Marketing in 2026",
        "10 Productivity Hacks That Changed My Life",
        "How I Built a SaaS Product in 30 Days",
        "AI Tools Every Business Owner Needs",
        "Behind the Scenes: Growing My YouTube Channel",
        "Passive Income Strategies That Actually Work",
        "Tech Review: Latest Gadgets Worth Buying",
        "Morning Routine of Successful Entrepreneurs",
        "Web Development Tutorial: Next.js Complete Course",
        "Financial Freedom: My Investment Portfolio Revealed",
        "Content Creation Tips for Beginners",
        "Building a Personal Brand on Social Media",
        "Crypto Trading Strategy That Made $50K",
        "Home Office Setup Tour 2026",
        "Time Management Secrets of Top Performers"
    ]
    
    # Video categories
    categories = [
        "Education",
        "Technology",
        "Business",
        "Lifestyle",
        "Finance",
        "Tutorial"
    ]
    
    video_data_list = []
    
    for i in range(num_videos):
        # Generate date (videos from the last 30 days for recent analysis)
        days_ago = random.randint(1, 30)
        publish_date = datetime.now() - timedelta(days=days_ago)
        
        # Generate realistic metrics based on video age
        # Older videos typically have more views
        age_multiplier = (30 - days_ago) / 30
        base_views = random.randint(5000, 100000)
        views = int(base_views * (1 + age_multiplier))
        
        # Engagement metrics (with realistic ratios)
        likes = int(views * random.uniform(0.02, 0.08))  # 2-8% like rate
        comments = int(views * random.uniform(0.001, 0.01))  # 0.1-1% comment rate
        shares = int(views * random.uniform(0.005, 0.02))  # 0.5-2% share rate
        
        # Watch time metrics
        avg_view_duration = random.uniform(180, 600)  # 3-10 minutes
        video_length = random.uniform(300, 900)  # 5-15 minutes
        watch_time_hours = (views * avg_view_duration) / 3600
        retention_rate = (avg_view_duration / video_length) * 100
        
        # Subscriber growth from this video
        subscribers_gained = int(views * random.uniform(0.005, 0.03))  # 0.5-3% conversion
        
        # Cost data (production + promotion)
        production_cost = random.uniform(100, 1000)  # Equipment, editing, etc.
        promotion_cost = random.uniform(50, 500)  # Ads, influencer promotion, etc.
        total_cost = production_cost + promotion_cost
        
        # Revenue data
        # CPM (Cost Per Mille) typically ranges from $1-$10 for most content
        cpm = random.uniform(2, 8)
        ad_revenue = (views / 1000) * cpm
        
        # Sponsorship revenue (not all videos have sponsors)
        has_sponsorship = random.random() < 0.3  # 30% chance
        sponsorship_revenue = random.uniform(500, 5000) if has_sponsorship else 0
        
        # Affiliate revenue (some videos have affiliate links)
        has_affiliate = random.random() < 0.4  # 40% chance
        affiliate_revenue = random.uniform(100, 2000) if has_affiliate else 0
        
        total_revenue = ad_revenue + sponsorship_revenue + affiliate_revenue
        
        # Calculate ROI
        roi = ((total_revenue - total_cost) / total_cost) * 100 if total_cost > 0 else 0
        net_profit = total_revenue - total_cost
        
        # Click-through rate (CTR) for thumbnails
        impressions = views * random.randint(10, 50)  # Impressions to views ratio
        ctr = (views / impressions) * 100
        
        video_data = {
            "user_email": user_email,
            "video_id": f"VIDEO_{i+1:03d}_{random.randint(1000, 9999)}",
            "title": random.choice(video_titles),
            "category": random.choice(categories),
            "publish_date": publish_date.isoformat(),
            "created_at": datetime.now().isoformat(),
            
            # Performance Metrics
            "metrics": {
                "views": views,
                "likes": likes,
                "dislikes": int(likes * random.uniform(0.02, 0.1)),  # Small dislike count
                "comments": comments,
                "shares": shares,
                "watch_time_hours": round(watch_time_hours, 2),
                "avg_view_duration_seconds": round(avg_view_duration, 2),
                "video_length_seconds": round(video_length, 2),
                "retention_rate_percent": round(retention_rate, 2),
                "subscribers_gained": subscribers_gained,
                "impressions": impressions,
                "ctr_percent": round(ctr, 2),
            },
            
            # Cost Breakdown
            "costs": {
                "production_cost_usd": round(production_cost, 2),
                "promotion_cost_usd": round(promotion_cost, 2),
                "total_cost_usd": round(total_cost, 2),
            },
            
            # Revenue Breakdown
            "revenue": {
                "ad_revenue_usd": round(ad_revenue, 2),
                "sponsorship_revenue_usd": round(sponsorship_revenue, 2),
                "affiliate_revenue_usd": round(affiliate_revenue, 2),
                "total_revenue_usd": round(total_revenue, 2),
                "cpm_usd": round(cpm, 2),
            },
            
            # ROI Calculations
            "roi_analysis": {
                "roi_percent": round(roi, 2),
                "net_profit_usd": round(net_profit, 2),
                "revenue_per_view_usd": round(total_revenue / views, 4) if views > 0 else 0,
                "cost_per_view_usd": round(total_cost / views, 4) if views > 0 else 0,
                "profit_per_view_usd": round(net_profit / views, 4) if views > 0 else 0,
            },
            
            # Additional metadata
            "status": "published",
            "is_monetized": True,
            "tags": ["business", "entrepreneurship", "marketing", "growth"],
        }
        
        video_data_list.append(video_data)
    
    # Add videos to Firestore
    try:
        roi_collection = db.collection('ROI')
        
        print(f"\n📊 Adding {num_videos} mock YouTube videos to Firestore...")
        print(f"👤 User: {user_email}")
        print("-" * 60)
        
        for idx, video in enumerate(video_data_list, 1):
            # Add document to Firestore
            doc_ref = roi_collection.add(video)
            doc_id = doc_ref[1].id
            
            print(f"\n✅ Video {idx}/{num_videos} added successfully!")
            print(f"   Document ID: {doc_id}")
            print(f"   Title: {video['title']}")
            print(f"   Views: {video['metrics']['views']:,}")
            print(f"   Revenue: ${video['revenue']['total_revenue_usd']:,.2f}")
            print(f"   Cost: ${video['costs']['total_cost_usd']:,.2f}")
            print(f"   ROI: {video['roi_analysis']['roi_percent']:.2f}%")
            print(f"   Net Profit: ${video['roi_analysis']['net_profit_usd']:,.2f}")
        
        # Calculate summary statistics
        total_views = sum(v['metrics']['views'] for v in video_data_list)
        total_revenue = sum(v['revenue']['total_revenue_usd'] for v in video_data_list)
        total_cost = sum(v['costs']['total_cost_usd'] for v in video_data_list)
        total_profit = total_revenue - total_cost
        avg_roi = sum(v['roi_analysis']['roi_percent'] for v in video_data_list) / num_videos
        
        print("\n" + "=" * 60)
        print("📈 SUMMARY STATISTICS")
        print("=" * 60)
        print(f"Total Videos: {num_videos}")
        print(f"Total Views: {total_views:,}")
        print(f"Total Revenue: ${total_revenue:,.2f}")
        print(f"Total Cost: ${total_cost:,.2f}")
        print(f"Total Net Profit: ${total_profit:,.2f}")
        print(f"Average ROI: {avg_roi:.2f}%")
        print(f"Overall ROI: {((total_revenue - total_cost) / total_cost * 100):.2f}%")
        print("=" * 60)
        
        print(f"\n✅ Successfully populated ROI collection for {user_email}")
        print(f"📁 Collection: ROI")
        print(f"🔢 Total documents: {num_videos}")
        
    except Exception as e:
        print(f"\n❌ Error adding data to Firestore: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # User email to populate data for
    USER_EMAIL = "limjl0130@gmail.com"
    
    # Number of mock videos to generate (default: 10)
    NUM_VIDEOS = 15
    
    print("=" * 60)
    print("🎬 YouTube ROI Data Generator")
    print("=" * 60)
    
    generate_mock_youtube_videos(USER_EMAIL, NUM_VIDEOS)
    
    print("\n✨ Done! You can now use this data for ROI calculations.")
