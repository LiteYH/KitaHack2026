"""
Seed ROI mock data into Firestore for ngzhengjie888@gmail.com.

Run from backend/ directory (venv activated):
  python seed_mock_data.py
"""

import sys
import os
import uuid
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.firebase import initialize_firebase

USER_EMAIL = "ngzhengjie888@gmail.com"


def days_ago(n):
    return (datetime.utcnow() - timedelta(days=n)).isoformat()


def seed_roi(db):
    print("\n-- Seeding: ROI collection --")

    videos = [
        {
            "title": "10 AI Tools That Will Change Your Business in 2026",
            "category": "Technology",
            "publish_date": days_ago(85),
            "metrics": {"views": 142300, "likes": 8940, "comments": 612, "retention_rate_percent": 54.2},
            "revenue": {"total_revenue_usd": 3210.50, "ad_revenue_usd": 1840.00, "sponsorship_revenue_usd": 1100.00, "affiliate_revenue_usd": 270.50},
            "costs": {"total_cost_usd": 890.00, "production_cost_usd": 540.00, "marketing_cost_usd": 350.00},
            "roi_analysis": {"roi_percent": 260.73, "net_profit_usd": 2320.50},
        },
        {
            "title": "How I Built a SaaS From Scratch - Full Journey",
            "category": "Entrepreneurship",
            "publish_date": days_ago(78),
            "metrics": {"views": 89500, "likes": 6120, "comments": 435, "retention_rate_percent": 62.1},
            "revenue": {"total_revenue_usd": 2650.00, "ad_revenue_usd": 1200.00, "sponsorship_revenue_usd": 1200.00, "affiliate_revenue_usd": 250.00},
            "costs": {"total_cost_usd": 720.00, "production_cost_usd": 450.00, "marketing_cost_usd": 270.00},
            "roi_analysis": {"roi_percent": 268.06, "net_profit_usd": 1930.00},
        },
        {
            "title": "Python Automation Tutorial: Save 10 Hours/Week",
            "category": "Tutorial",
            "publish_date": days_ago(70),
            "metrics": {"views": 210400, "likes": 15300, "comments": 1102, "retention_rate_percent": 67.8},
            "revenue": {"total_revenue_usd": 4500.00, "ad_revenue_usd": 2900.00, "sponsorship_revenue_usd": 1200.00, "affiliate_revenue_usd": 400.00},
            "costs": {"total_cost_usd": 600.00, "production_cost_usd": 380.00, "marketing_cost_usd": 220.00},
            "roi_analysis": {"roi_percent": 650.00, "net_profit_usd": 3900.00},
        },
        {
            "title": "Malaysia Startup Scene 2026: What's Hot?",
            "category": "Business",
            "publish_date": days_ago(63),
            "metrics": {"views": 34200, "likes": 2100, "comments": 198, "retention_rate_percent": 48.5},
            "revenue": {"total_revenue_usd": 890.00, "ad_revenue_usd": 640.00, "sponsorship_revenue_usd": 0.00, "affiliate_revenue_usd": 250.00},
            "costs": {"total_cost_usd": 440.00, "production_cost_usd": 300.00, "marketing_cost_usd": 140.00},
            "roi_analysis": {"roi_percent": 102.27, "net_profit_usd": 450.00},
        },
        {
            "title": "I Tried Every AI Image Generator - Honest Review",
            "category": "Technology",
            "publish_date": days_ago(55),
            "metrics": {"views": 178000, "likes": 11200, "comments": 843, "retention_rate_percent": 58.3},
            "revenue": {"total_revenue_usd": 3850.00, "ad_revenue_usd": 2050.00, "sponsorship_revenue_usd": 1500.00, "affiliate_revenue_usd": 300.00},
            "costs": {"total_cost_usd": 780.00, "production_cost_usd": 480.00, "marketing_cost_usd": 300.00},
            "roi_analysis": {"roi_percent": 393.59, "net_profit_usd": 3070.00},
        },
        {
            "title": "Build a LangChain Agent in 30 Minutes",
            "category": "Tutorial",
            "publish_date": days_ago(48),
            "metrics": {"views": 95700, "likes": 7400, "comments": 520, "retention_rate_percent": 71.4},
            "revenue": {"total_revenue_usd": 2200.00, "ad_revenue_usd": 1400.00, "sponsorship_revenue_usd": 600.00, "affiliate_revenue_usd": 200.00},
            "costs": {"total_cost_usd": 420.00, "production_cost_usd": 280.00, "marketing_cost_usd": 140.00},
            "roi_analysis": {"roi_percent": 423.81, "net_profit_usd": 1780.00},
        },
        {
            "title": "Social Media Strategy That Actually Works in 2026",
            "category": "Marketing",
            "publish_date": days_ago(42),
            "metrics": {"views": 63100, "likes": 4800, "comments": 312, "retention_rate_percent": 52.0},
            "revenue": {"total_revenue_usd": 1780.00, "ad_revenue_usd": 980.00, "sponsorship_revenue_usd": 600.00, "affiliate_revenue_usd": 200.00},
            "costs": {"total_cost_usd": 560.00, "production_cost_usd": 360.00, "marketing_cost_usd": 200.00},
            "roi_analysis": {"roi_percent": 217.86, "net_profit_usd": 1220.00},
        },
        {
            "title": "How I Make $10K/Month as a Content Creator",
            "category": "Entrepreneurship",
            "publish_date": days_ago(35),
            "metrics": {"views": 245600, "likes": 18900, "comments": 1430, "retention_rate_percent": 65.9},
            "revenue": {"total_revenue_usd": 5400.00, "ad_revenue_usd": 2800.00, "sponsorship_revenue_usd": 2000.00, "affiliate_revenue_usd": 600.00},
            "costs": {"total_cost_usd": 950.00, "production_cost_usd": 600.00, "marketing_cost_usd": 350.00},
            "roi_analysis": {"roi_percent": 468.42, "net_profit_usd": 4450.00},
        },
        {
            "title": "Firebase vs Supabase: Which Should You Choose?",
            "category": "Technology",
            "publish_date": days_ago(28),
            "metrics": {"views": 52300, "likes": 3900, "comments": 289, "retention_rate_percent": 60.2},
            "revenue": {"total_revenue_usd": 1350.00, "ad_revenue_usd": 950.00, "sponsorship_revenue_usd": 0.00, "affiliate_revenue_usd": 400.00},
            "costs": {"total_cost_usd": 380.00, "production_cost_usd": 250.00, "marketing_cost_usd": 130.00},
            "roi_analysis": {"roi_percent": 255.26, "net_profit_usd": 970.00},
        },
        {
            "title": "Prompt Engineering Masterclass for Beginners",
            "category": "Tutorial",
            "publish_date": days_ago(21),
            "metrics": {"views": 129800, "likes": 10100, "comments": 748, "retention_rate_percent": 69.5},
            "revenue": {"total_revenue_usd": 2980.00, "ad_revenue_usd": 1780.00, "sponsorship_revenue_usd": 800.00, "affiliate_revenue_usd": 400.00},
            "costs": {"total_cost_usd": 500.00, "production_cost_usd": 320.00, "marketing_cost_usd": 180.00},
            "roi_analysis": {"roi_percent": 496.00, "net_profit_usd": 2480.00},
        },
        {
            "title": "My Gear Setup for YouTube in 2026 (Under $1000)",
            "category": "Vlog",
            "publish_date": days_ago(14),
            "metrics": {"views": 41800, "likes": 3200, "comments": 220, "retention_rate_percent": 44.1},
            "revenue": {"total_revenue_usd": 1020.00, "ad_revenue_usd": 620.00, "sponsorship_revenue_usd": 0.00, "affiliate_revenue_usd": 400.00},
            "costs": {"total_cost_usd": 290.00, "production_cost_usd": 190.00, "marketing_cost_usd": 100.00},
            "roi_analysis": {"roi_percent": 251.72, "net_profit_usd": 730.00},
        },
        {
            "title": "ChatGPT vs Gemini vs Claude - 2026 Benchmark",
            "category": "Technology",
            "publish_date": days_ago(10),
            "metrics": {"views": 198500, "likes": 14200, "comments": 1092, "retention_rate_percent": 61.7},
            "revenue": {"total_revenue_usd": 4100.00, "ad_revenue_usd": 2300.00, "sponsorship_revenue_usd": 1500.00, "affiliate_revenue_usd": 300.00},
            "costs": {"total_cost_usd": 820.00, "production_cost_usd": 520.00, "marketing_cost_usd": 300.00},
            "roi_analysis": {"roi_percent": 400.00, "net_profit_usd": 3280.00},
        },
        {
            "title": "How to Go Viral on YouTube Shorts in 2026",
            "category": "Marketing",
            "publish_date": days_ago(6),
            "metrics": {"views": 312000, "likes": 24000, "comments": 1820, "retention_rate_percent": 73.2},
            "revenue": {"total_revenue_usd": 6200.00, "ad_revenue_usd": 3200.00, "sponsorship_revenue_usd": 2500.00, "affiliate_revenue_usd": 500.00},
            "costs": {"total_cost_usd": 1100.00, "production_cost_usd": 700.00, "marketing_cost_usd": 400.00},
            "roi_analysis": {"roi_percent": 463.64, "net_profit_usd": 5100.00},
        },
        {
            "title": "Building My Personal Brand From Zero - Week 1 Update",
            "category": "Vlog",
            "publish_date": days_ago(2),
            "metrics": {"views": 18200, "likes": 1400, "comments": 98, "retention_rate_percent": 41.0},
            "revenue": {"total_revenue_usd": 420.00, "ad_revenue_usd": 320.00, "sponsorship_revenue_usd": 0.00, "affiliate_revenue_usd": 100.00},
            "costs": {"total_cost_usd": 240.00, "production_cost_usd": 160.00, "marketing_cost_usd": 80.00},
            "roi_analysis": {"roi_percent": 75.00, "net_profit_usd": 180.00},
        },
    ]

    for video in videos:
        doc_id = str(uuid.uuid4())
        db.collection("ROI").document(doc_id).set({
            "user_email": USER_EMAIL,
            "created_at": datetime.utcnow().isoformat(),
            **video,
        })
        print("  OK  " + video["title"][:60])

    print("\nSeeded", len(videos), "ROI documents for", USER_EMAIL)


def main():
    print("=" * 60)
    print("Seeding ROI mock data")
    print("User:", USER_EMAIL)
    print("=" * 60)

    _, db = initialize_firebase()
    if db is None:
        print("ERROR: Firebase not initialised. Check .env credentials.")
        sys.exit(1)

    seed_roi(db)
    print("\nDone.")


if __name__ == "__main__":
    main()
