"""
Clear Firestore Collections

Deletes all documents from chat-related collections for testing.
"""
import asyncio
from app.core.firebase import get_db

def clear_collection(collection_name: str):
    """Delete all documents in a collection."""
    db = get_db()
    collection_ref = db.collection(collection_name)
    
    deleted_count = 0
    batch = db.batch()
    batch_count = 0
    
    # Get all documents
    docs = collection_ref.stream()
    
    for doc in docs:
        batch.delete(doc.reference)
        batch_count += 1
        deleted_count += 1
        
        # Commit in batches of 500 (Firestore limit)
        if batch_count >= 500:
            batch.commit()
            print(f"  Deleted {deleted_count} documents so far...")
            batch = db.batch()
            batch_count = 0
    
    # Commit remaining
    if batch_count > 0:
        batch.commit()
    
    print(f"✅ Cleared {deleted_count} documents from '{collection_name}'")
    return deleted_count

def main():
    """Clear all chat and monitoring related collections."""
    print("🧹 Clearing Firestore collections...\n")
    
    collections_to_clear = [
        'chat_messages',
        'chat_threads',
        'user_profiles',  # Contains active_thread_id
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
    
    print(f"\n🎉 Total: Deleted {total_deleted} documents across all collections")
    print("You can now test from scratch!")

if __name__ == '__main__':
    main()
