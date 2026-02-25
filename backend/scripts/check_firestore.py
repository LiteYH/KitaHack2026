"""
Check Firestore Collections

Shows what data currently exists in Firestore.
"""
from app.core.firebase import get_db

def check_collection(collection_name: str):
    """Check documents in a collection."""
    db = get_db()
    collection_ref = db.collection(collection_name)
    
    docs = list(collection_ref.stream())
    
    if docs:
        print(f"\n📦 {collection_name}: {len(docs)} documents")
        for doc in docs[:5]:  # Show first 5
            data = doc.to_dict()
            print(f"  - {doc.id}: {list(data.keys())}")
        if len(docs) > 5:
            print(f"  ... and {len(docs) - 5} more")
    else:
        print(f"\n📦 {collection_name}: Empty ✓")

def main():
    """Check all collections."""
    print("🔍 Checking Firestore collections...\n")
    
    collections = [
        'users',
        'user_profiles', 
        'chat_messages',
        'chat_threads',
        'monitoring_configs',
        'monitoring_results',
        'cron_jobs',
        'thread_states',
    ]
    
    for collection in collections:
        try:
            check_collection(collection)
        except Exception as e:
            print(f"\n❌ Error checking '{collection}': {e}")

if __name__ == '__main__':
    main()
