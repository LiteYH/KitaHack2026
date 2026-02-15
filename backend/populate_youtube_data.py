#!/usr/bin/env python3
"""
Sample Data Generator for YouTube ROI Metrics
Adds sample YouTube data to Firestore for testing the report generator
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

try:
    from app.core.firestore_client import firestore_client
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False
    print("❌ Firestore client not available. Please check installation.")

# Sample video titles by category
VIDEO_TITLES = {
    "Tutorial": [
        "Ultimate Guide to YouTube Marketing",
        "How to Create Viral Videos in 2026",
        "Video Editing Masterclass",
        "YouTube SEO Complete Guide",
        "Content Strategy for Beginners"
    ],
    "Product Review": [
        "Best Camera for YouTube 2026",
        "Top 10 Microphones for Content Creators",
        "Lighting Equipment Review",
        "Video Editing Software Comparison",
        "Must-Have YouTube Gear"
    ],
    "Vlog": [
        "Day in the Life of a Content Creator",
        "Behind the Scenes at Our Studio",
        "Q&A with My Audience",
        "Weekly Vlog Episode 12",
        "Travel Vlog: Exploring New Cities"
    ],
    "Educational": [
        "Understanding YouTube Algorithm",
        "Digital Marketing 101",
        "Social Media Strategy Explained",
        "Analytics Deep Dive",
        "Monetization Masterclass"
    ],
    "Entertainment": [
        "Funny Moments Compilation",
        "Challenge Video: Can We Do It?",
        "Reaction to Viral Trends",
        "Gaming Stream Highlights",
        "Comedy Sketch Series"
    ]
}

def generate_sample_youtube_data(num_records: int = 50) -> List[Dict[str, Any]]:
    """
    Generate sample YouTube ROI data
    
    Args:
        num_records: Number of sample records to generate
    
    Returns:
        List of sample YouTube ROI records
    """
    sample_data = []
    categories = list(VIDEO_TITLES.keys())
    
    # Generate data over the past 90 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    for i in range(num_records):
        # Random category
        category = random.choice(categories)
        
        # Random video title from category
        video_title = random.choice(VIDEO_TITLES[category])
        
        # Random date within range
        days_ago = random.randint(0, 90)
        created_at = end_date - timedelta(days=days_ago)
        
        # Generate realistic metrics based on category performance
        # Tutorials and Educational content typically perform well
        if category in ["Tutorial", "Educational"]:
            base_views = random.randint(50000, 200000)
            engagement_multiplier = random.uniform(0.05, 0.10)
        elif category == "Product Review":
            base_views = random.randint(30000, 150000)
            engagement_multiplier = random.uniform(0.06, 0.12)
        elif category == "Vlog":
            base_views = random.randint(40000, 180000)
            engagement_multiplier = random.uniform(0.07, 0.15)
        else:  # Entertainment
            base_views = random.randint(60000, 250000)
            engagement_multiplier = random.uniform(0.08, 0.20)
        
        views = base_views
        likes = int(views * engagement_multiplier * random.uniform(0.8, 1.2))
        comments = int(likes * random.uniform(0.10, 0.20))
        shares = int(likes * random.uniform(0.05, 0.10))
        
        # Watch time (average 40-60% of video length assumed 10 min)
        avg_watch_percentage = random.uniform(0.40, 0.60)
        watch_time_hours = (views * 10 * avg_watch_percentage) / 60  # Convert to hours
        
        # Subscribers gained (some videos perform better)
        subscriber_rate = random.uniform(0.001, 0.005)
        subscribers_gained = int(views * subscriber_rate)
        
        # Ad spend varies by campaign
        ad_spend = random.uniform(100, 1500)
        
        # Revenue calculation (CPM-based + engagement bonuses)
        cpm = random.uniform(2.5, 8.5)  # Cost per thousand views
        base_revenue = (views / 1000) * cpm
        
        # Bonus revenue from high engagement
        engagement_bonus = (likes + comments * 2 + shares * 3) * random.uniform(0.01, 0.05)
        
        revenue_generated = base_revenue + engagement_bonus
        
        record = {
            "user_id": "demo_user",
            "platform": "YouTube",
            "video_title": f"{video_title} #{i+1}",
            "content_category": category,
            "content_type": "Video",
            "views": views,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "subscribers_gained": subscribers_gained,
            "watch_time_hours": round(watch_time_hours, 2),
            "ad_spend": round(ad_spend, 2),
            "revenue_generated": round(revenue_generated, 2),
            "created_at": created_at.isoformat()
        }
        
        sample_data.append(record)
    
    return sample_data


async def add_sample_data_to_firestore(num_records: int = 50):
    """
    Add sample YouTube data to Firestore
    
    Args:
        num_records: Number of records to generate and add
    """
    if not FIRESTORE_AVAILABLE:
        print("❌ Firestore client not available")
        return False
    
    if not firestore_client.firebase_available or not firestore_client.db:
        print("❌ Firestore not initialized. Check Firebase credentials.")
        return False
    
    try:
        print(f"🚀 Generating {num_records} sample YouTube ROI records...")
        sample_data = generate_sample_youtube_data(num_records)
        
        print("📤 Adding records to Firestore...")
        collection_ref = firestore_client.db.collection('roi_metrics')
        
        # Add records in batches
        batch_size = 10
        for i in range(0, len(sample_data), batch_size):
            batch = sample_data[i:i + batch_size]
            
            for record in batch:
                # Convert ISO date string to Firestore timestamp
                from datetime import datetime
                record['created_at'] = datetime.fromisoformat(record['created_at'])
                
                # Add document
                collection_ref.add(record)
            
            print(f"  ✅ Added batch {i//batch_size + 1}/{(len(sample_data)-1)//batch_size + 1}")
        
        print(f"\n✅ Successfully added {len(sample_data)} YouTube ROI records to Firestore!")
        print("\n📊 Summary:")
        print(f"   - Total Records: {len(sample_data)}")
        print(f"   - Categories: {len(set(r['content_category'] for r in sample_data))}")
        print(f"   - Total Views: {sum(r['views'] for r in sample_data):,}")
        print(f"   - Total Revenue: ${sum(r['revenue_generated'] for r in sample_data):,.2f}")
        print(f"   - Total Ad Spend: ${sum(r['ad_spend'] for r in sample_data):,.2f}")
        
        total_revenue = sum(r['revenue_generated'] for r in sample_data)
        total_spend = sum(r['ad_spend'] for r in sample_data)
        overall_roi = ((total_revenue - total_spend) / total_spend) * 100
        print(f"   - Overall ROI: {overall_roi:.2f}%")
        
        print("\n🎉 You can now generate YouTube reports!")
        print("   - Backend: http://localhost:8000/api/v1/youtube-report/preview")
        print("   - Frontend: http://localhost:3000/youtube-report")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding sample data: {str(e)}")
        return False


async def clear_sample_data():
    """
    Clear all sample data from Firestore (demo_user records only)
    """
    if not FIRESTORE_AVAILABLE or not firestore_client.firebase_available:
        print("❌ Firestore not available")
        return False
    
    try:
        print("🗑️  Clearing sample data from Firestore...")
        collection_ref = firestore_client.db.collection('roi_metrics')
        
        # Query for demo_user records
        query = collection_ref.where('user_id', '==', 'demo_user')
        docs = query.stream()
        
        count = 0
        for doc in docs:
            doc.reference.delete()
            count += 1
        
        print(f"✅ Deleted {count} sample records")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing sample data: {str(e)}")
        return False


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("YouTube ROI Sample Data Generator")
    print("=" * 60)
    print()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "clear":
            print("Clearing sample data...")
            asyncio.run(clear_sample_data())
            sys.exit(0)
        else:
            try:
                num_records = int(sys.argv[1])
            except ValueError:
                print("Usage: python populate_youtube_data.py [number_of_records | clear]")
                sys.exit(1)
    else:
        num_records = 50
    
    # Add sample data
    asyncio.run(add_sample_data_to_firestore(num_records))
