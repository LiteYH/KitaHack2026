"""
Reset to Fresh State

Keeps only the users collection, clears everything else.
"""
from app.core.firebase import get_db

def clear_collection(collection_name: str):
    """Delete all documents in a collection."""
    db = get_db()
    collection_ref = db.collection(collection_name)
    
    deleted_count = 0
    batch = db.batch()
    batch_count = 0
    
    docs = collection_ref.stream()
    
    for doc in docs:
        batch.delete(doc.reference)
        batch_count += 1
        deleted_count += 1
        
        if batch_count >= 500:
            batch.commit()
            batch = db.batch()
            batch_count = 0
    
    if batch_count > 0:
        batch.commit()
    
    if deleted_count > 0:
        print(f"✅ Cleared {deleted_count} documents from '{collection_name}'")
    return deleted_count

def main():
    """Clear all collections except users."""
    print("🧹 Resetting to fresh state...\n")
    print("Keeping: users collection")
    print("Clearing: everything else\n")
    
    collections_to_clear = [
        'user_profiles',  # Will be recreated on next chat
        'chat_messages',
        'chat_threads',
        'monitoring_configs',
        'monitoring_results',
        'cron_jobs',
        'thread_states',
    ]
    
    total_deleted = 0
    
    for collection in collections_to_clear:
        try:
            count = clear_collection(collection)
            total_deleted += count
        except Exception as e:
            print(f"❌ Error clearing '{collection}': {e}")
    
    print(f"\n🎉 Deleted {total_deleted} documents")
    print("✅ Ready for fresh start - users collection intact")

if __name__ == '__main__':
    main()
