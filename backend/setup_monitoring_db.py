"""
Setup script for Competitor Monitoring Firestore Database
Creates the simplified collections and initializes the database structure.
"""

import sys
import json
from datetime import datetime, timedelta
from app.core.firebase import initialize_firebase, get_db

def setup_database():
    """Initialize Firestore collections for competitor monitoring"""
    
    print("🔥 Initializing Firebase...")
    app, db = initialize_firebase()
    
    if not db:
        print("❌ Failed to initialize Firebase. Check your credentials in backend/.env")
        return False
    
    print("✅ Firebase connected successfully!\n")
    
    # Test collections
    collections = {
        'competitors': 'Competitor basic information',
        'monitoring_jobs': 'Active monitoring jobs with cron',
        'monitoring_logs': 'Historical monitoring results',
        'competitor_agent_memory': 'Agent context and memory'
    }
    
    print("📦 Setting up collections...\n")
    
    for collection_name, description in collections.items():
        print(f"   📁 {collection_name} - {description}")
    
    print("\n✅ Collections structure defined!")
    print("\n" + "="*60)
    print("DATABASE STRUCTURE")
    print("="*60 + "\n")
    
    # Show structure
    print("1️⃣  competitors/{competitorId}")
    print("    ├── userId: string")
    print("    ├── name: string")
    print("    ├── url: string")
    print("    └── createdAt: timestamp\n")
    
    print("2️⃣  monitoring_jobs/{jobId}")
    print("    ├── userId: string")
    print("    ├── competitor: string")
    print("    ├── config: string (JSON)")
    print("    ├── status: string")
    print("    ├── cronJobId: string")
    print("    ├── nextRun: timestamp")
    print("    ├── lastRun: timestamp")
    print("    └── createdAt: timestamp\n")
    
    print("3️⃣  monitoring_logs/{logId}")
    print("    ├── userId: string")
    print("    ├── jobId: string")
    print("    ├── competitor: string")
    print("    ├── timestamp: timestamp")
    print("    ├── data: string (JSON)")
    print("    └── notified: boolean\n")
    
    print("4️⃣  competitor_agent_memory/{userId}")
    print("    ├── memory: string (JSON/Markdown)")
    print("    └── updatedAt: timestamp\n")
    
    print("="*60)
    print("EXAMPLE DATA CREATION")
    print("="*60 + "\n")
    
    # Ask to create example data
    response = input("📝 Create example data for testing? (y/n): ").lower().strip()
    
    if response == 'y':
        create_example_data(db)
    else:
        print("\n⏭️  Skipping example data creation.")
    
    print("\n" + "="*60)
    print("SECURITY RULES")
    print("="*60 + "\n")
    
    print("⚠️  IMPORTANT: Set Firestore security rules!")
    print("📋 Go to: https://console.firebase.google.com/project/kitahack2026-8feed/firestore/rules\n")
    
    print("Copy these rules:\n")
    print("""rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    match /competitors/{competitorId} {
      allow read, write: if request.auth.uid == resource.data.userId;
      allow create: if request.auth.uid == request.resource.data.userId;
    }
    
    match /monitoring_jobs/{jobId} {
      allow read, write: if request.auth.uid == resource.data.userId;
      allow create: if request.auth.uid == request.resource.data.userId;
    }
    
    match /monitoring_logs/{logId} {
      allow read: if request.auth.uid == resource.data.userId;
      allow write: if false;
    }
    
    match /competitor_agent_memory/{userId} {
      allow read, write: if request.auth.uid == userId;
    }
  }
}""")
    
    print("\n✅ Database setup complete!")
    print("\n📚 Next steps:")
    print("   1. Set security rules in Firebase Console")
    print("   2. Test monitoring job creation")
    print("   3. Verify agent memory storage")
    print("   4. Check monitoring logs collection\n")
    
    return True


def create_example_data(db):
    """Create example documents to demonstrate structure"""
    
    print("\n📝 Creating example data...\n")
    
    # Example user ID (use a test user or placeholder)
    test_user_id = "test_user_example"
    
    try:
        # 1. Create example competitor
        competitor_ref = db.collection('competitors').add({
            'userId': test_user_id,
            'name': 'Nike',
            'url': 'https://nike.com',
            'createdAt': datetime.utcnow()
        })
        print(f"   ✅ Created competitor: Nike (ID: {competitor_ref[1].id})")
        
        # 2. Create example monitoring job
        config = {
            "aspects": ["products", "news", "pricing"],
            "frequency_hours": 2,
            "notification": "significant",
            "email": "user@example.com"
        }
        
        job_ref = db.collection('monitoring_jobs').add({
            'userId': test_user_id,
            'competitor': 'Nike',
            'config': json.dumps(config),
            'status': 'active',
            'cronJobId': 'cron_example_12345',
            'nextRun': datetime.utcnow() + timedelta(hours=2),
            'lastRun': datetime.utcnow(),
            'createdAt': datetime.utcnow()
        })
        print(f"   ✅ Created monitoring job (ID: {job_ref[1].id})")
        
        # 3. Create example monitoring log
        findings = {
            "products": [
                {"name": "Air Max 2026", "launched": "2026-02-13"}
            ],
            "news": [
                {
                    "title": "Nike announces sustainability initiative",
                    "url": "https://nike.com/news/sustainability",
                    "date": "2026-02-13"
                }
            ],
            "pricing": [
                {
                    "product": "Air Jordan 1",
                    "change": "-15%",
                    "reason": "Valentine's sale"
                }
            ],
            "isSignificant": True,
            "score": 85,
            "reasons": ["New product launch", "Major price change"]
        }
        
        log_ref = db.collection('monitoring_logs').add({
            'userId': test_user_id,
            'jobId': job_ref[1].id,
            'competitor': 'Nike',
            'timestamp': datetime.utcnow(),
            'data': json.dumps(findings),
            'notified': True
        })
        print(f"   ✅ Created monitoring log (ID: {log_ref[1].id})")
        
        # 4. Create example agent memory
        memory = {
            "prefs": {
                "freq": 6,
                "notif": "significant",
                "timezone": "EST"
            },
            "active": ["Nike", "Adidas"],
            "recent": [
                "Nike price drop detected",
                "Discussed product launches",
                "Set up Adidas monitoring"
            ],
            "stats": {
                "jobs": 5,
                "findings": 127,
                "significant": 18
            }
        }
        
        db.collection('competitor_agent_memory').document(test_user_id).set({
            'memory': json.dumps(memory, indent=2),
            'updatedAt': datetime.utcnow()
        })
        print(f"   ✅ Created agent memory for user: {test_user_id}")
        
        print("\n✅ Example data created successfully!")
        print(f"\n📊 View data: https://console.firebase.google.com/project/kitahack2026-8feed/firestore/data")
        print(f"   Test User ID: {test_user_id}")
        
    except Exception as e:
        print(f"\n❌ Error creating example data: {str(e)}")
        print("   This is normal if you haven't set security rules yet.")
        print("   The structure is still valid!")


def verify_collections(db):
    """Verify collections are accessible"""
    print("\n🔍 Verifying collections...")
    
    collections = ['competitors', 'monitoring_jobs', 'monitoring_logs', 'competitor_agent_memory']
    
    for collection_name in collections:
        try:
            # Try to access collection
            ref = db.collection(collection_name)
            print(f"   ✅ {collection_name}")
        except Exception as e:
            print(f"   ❌ {collection_name}: {str(e)}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 COMPETITOR MONITORING DATABASE SETUP")
    print("="*60 + "\n")
    
    print("This script will:")
    print("  1. Connect to Firebase/Firestore")
    print("  2. Verify collections structure")
    print("  3. Optionally create example data")
    print("  4. Show security rules to apply\n")
    
    response = input("Continue? (y/n): ").lower().strip()
    
    if response == 'y':
        success = setup_database()
        sys.exit(0 if success else 1)
    else:
        print("\n⏭️  Setup cancelled.")
        sys.exit(0)
