"""
Seed script to populate Firestore with 9 mock campaign data for fashion brand.
Run this script to add campaign data to the campaign_details collection.

Usage:
    python seed_campaigns.py
"""

from datetime import datetime, timezone, timedelta
from app.core.firebase import initialize_firebase

# Initialize Firebase
_, db = initialize_firebase()

if db is None:
    print("❌ Failed to initialize Firebase. Please check your credentials.")
    exit(1)

# UTC+8 offset
utc8 = timezone(timedelta(hours=8))

def parse_date(date_string):
    """
    Parse date string like "February 5, 2026 at 12:00:00 AM UTC+8" to datetime
    """
    date_part = date_string.replace(" at ", " ").replace(" UTC+8", "")
    dt = datetime.strptime(date_part, "%B %d, %Y %I:%M:%S %p")
    return dt.replace(tzinfo=utc8)

# Campaign data - all for the same user
USER_ID = "DT4DNex2L1N2rZ9kPddEzqougK22"

campaigns = [
    {
        "userID": USER_ID,
        "campaignName": "Valentine Couple Outfit Drop",
        "totalBudget": 8000,
        "amountSpent": 5200,
        "impressions": 180000,
        "clicks": 9500,
        "purchases": 210,
        "conversionValue": 31500,
        "platform": "Instagram",
        "status": "ongoing",
        "startDate": "February 5, 2026 at 12:00:00 AM UTC+8",
        "endDate": "February 28, 2026 at 12:00:00 AM UTC+8",
        "createdAt": "February 5, 2026 at 12:00:00 AM UTC+8"
    },
    {
        "userID": USER_ID,
        "campaignName": "Summer Sneakers Launch",
        "totalBudget": 12000,
        "amountSpent": 6400,
        "impressions": 240000,
        "clicks": 14000,
        "purchases": 320,
        "conversionValue": 52800,
        "platform": "Facebook",
        "status": "ongoing",
        "startDate": "February 10, 2026 at 12:00:00 AM UTC+8",
        "endDate": "March 15, 2026 at 12:00:00 AM UTC+8",
        "createdAt": "February 10, 2026 at 12:00:00 AM UTC+8"
    },
    {
        "userID": USER_ID,
        "campaignName": "Back to Uni Streetwear Push",
        "totalBudget": 7000,
        "amountSpent": 4300,
        "impressions": 150000,
        "clicks": 7200,
        "purchases": 160,
        "conversionValue": 24800,
        "platform": "E-commerce",
        "status": "ongoing",
        "startDate": "February 1, 2026 at 12:00:00 AM UTC+8",
        "endDate": "March 1, 2026 at 12:00:00 AM UTC+8",
        "createdAt": "February 1, 2026 at 12:00:00 AM UTC+8"
    },
    {
        "userID": USER_ID,
        "campaignName": "Influencer Street Style KOL Campaign",
        "totalBudget": 15000,
        "amountSpent": 9000,
        "impressions": 300000,
        "clicks": 16500,
        "purchases": 420,
        "conversionValue": 73500,
        "platform": "KOL",
        "status": "ongoing",
        "startDate": "February 8, 2026 at 12:00:00 AM UTC+8",
        "endDate": "March 10, 2026 at 12:00:00 AM UTC+8",
        "createdAt": "February 8, 2026 at 12:00:00 AM UTC+8"
    },
    {
        "userID": USER_ID,
        "campaignName": "Ramadan Modest Collection",
        "totalBudget": 9000,
        "amountSpent": 4800,
        "impressions": 200000,
        "clicks": 8800,
        "purchases": 240,
        "conversionValue": 38400,
        "platform": "Instagram",
        "status": "ongoing",
        "startDate": "February 12, 2026 at 12:00:00 AM UTC+8",
        "endDate": "March 30, 2026 at 12:00:00 AM UTC+8",
        "createdAt": "February 12, 2026 at 12:00:00 AM UTC+8"
    },
    {
        "userID": USER_ID,
        "campaignName": "Flash Sale Trendy Hoodies",
        "totalBudget": 6000,
        "amountSpent": 3700,
        "impressions": 120000,
        "clicks": 6800,
        "purchases": 150,
        "conversionValue": 21000,
        "platform": "Facebook",
        "status": "ongoing",
        "startDate": "February 14, 2026 at 12:00:00 AM UTC+8",
        "endDate": "February 20, 2026 at 12:00:00 AM UTC+8",
        "createdAt": "February 14, 2026 at 12:00:00 AM UTC+8"
    },
    {
        "userID": USER_ID,
        "campaignName": "Limited Edition Sneakers Drop",
        "totalBudget": 10000,
        "amountSpent": 8200,
        "impressions": 260000,
        "clicks": 11000,
        "purchases": 180,
        "conversionValue": 36000,
        "platform": "Instagram",
        "status": "paused",
        "startDate": "January 5, 2026 at 12:00:00 AM UTC+8",
        "endDate": "February 5, 2026 at 12:00:00 AM UTC+8",
        "createdAt": "January 5, 2026 at 12:00:00 AM UTC+8"
    },
    {
        "userID": USER_ID,
        "campaignName": "Weekend Mega Sale",
        "totalBudget": 7500,
        "amountSpent": 6900,
        "impressions": 210000,
        "clicks": 9000,
        "purchases": 170,
        "conversionValue": 25500,
        "platform": "Facebook",
        "status": "paused",
        "startDate": "January 10, 2026 at 12:00:00 AM UTC+8",
        "endDate": "January 31, 2026 at 12:00:00 AM UTC+8",
        "createdAt": "January 10, 2026 at 12:00:00 AM UTC+8"
    },
    {
        "userID": USER_ID,
        "campaignName": "Clearance Winter Jackets",
        "totalBudget": 5000,
        "amountSpent": 4500,
        "impressions": 160000,
        "clicks": 6200,
        "purchases": 130,
        "conversionValue": 19500,
        "platform": "E-commerce",
        "status": "paused",
        "startDate": "December 15, 2025 at 12:00:00 AM UTC+8",
        "endDate": "January 15, 2026 at 12:00:00 AM UTC+8",
        "createdAt": "December 15, 2025 at 12:00:00 AM UTC+8"
    }
]


def seed_campaigns():
    """
    Seed all campaign data into Firestore campaign_details collection
    """
    collection_ref = db.collection('campaign_details')
    
    print(f"\n🌱 Starting to seed {len(campaigns)} campaigns...")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for idx, campaign in enumerate(campaigns, 1):
        try:
            # Convert date strings to datetime objects
            campaign_data = campaign.copy()
            campaign_data['startDate'] = parse_date(campaign['startDate'])
            campaign_data['endDate'] = parse_date(campaign['endDate'])
            campaign_data['createdAt'] = parse_date(campaign['createdAt'])
            
            # Add document with auto-generated ID
            doc_ref = collection_ref.add(campaign_data)
            
            print(f"✅ [{idx}/9] Added: {campaign['campaignName']}")
            print(f"    Status: {campaign['status']} | Platform: {campaign['platform']}")
            print(f"    Budget: ${campaign['totalBudget']} | Spent: ${campaign['amountSpent']}")
            print(f"    Doc ID: {doc_ref[1].id}")
            print()
            
            success_count += 1
            
        except Exception as e:
            print(f"❌ [{idx}/9] Failed to add: {campaign['campaignName']}")
            print(f"    Error: {str(e)}")
            print()
            fail_count += 1
    
    print("=" * 60)
    print(f"📊 Seeding Complete!")
    print(f"   ✅ Success: {success_count}")
    print(f"   ❌ Failed: {fail_count}")
    print(f"   📈 Total: {len(campaigns)}")
    print()
    
    if success_count > 0:
        print(f"🎯 Now you can analyze:")
        print(f"   • CTR = clicks / impressions")
        print(f"   • CVR = purchases / clicks")
        print(f"   • ROAS = conversionValue / amountSpent")
        print(f"   • Budget utilization = amountSpent / totalBudget")
        print()
        print(f"🔥 Your fashion brand campaign data is ready!")
    

if __name__ == "__main__":
    seed_campaigns()
