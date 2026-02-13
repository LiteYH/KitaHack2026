"""
Script to delete all data from Firestore collections.
Use with caution - this will permanently delete all data!
"""

import firebase_admin
from firebase_admin import credentials, firestore
from app.core.config import settings
import sys


def delete_collection(db, collection_name, batch_size=100):
    """
    Delete all documents in a collection in batches.
    
    Args:
        db: Firestore client
        collection_name: Name of the collection to delete
        batch_size: Number of documents to delete per batch
    """
    collection_ref = db.collection(collection_name)
    deleted_count = 0
    
    while True:
        # Get a batch of documents
        docs = collection_ref.limit(batch_size).stream()
        deleted_in_batch = 0
        
        # Delete documents in batch
        batch = db.batch()
        for doc in docs:
            batch.delete(doc.reference)
            deleted_in_batch += 1
        
        if deleted_in_batch == 0:
            break
        
        batch.commit()
        deleted_count += deleted_in_batch
        print(f"  Deleted {deleted_in_batch} documents from {collection_name} (total: {deleted_count})")
    
    return deleted_count


def main():
    """Main function to delete all Firestore data."""
    
    # Collections to delete
    collections = [
        "competitor_agent_memory",
        "competitors",
        "cron_jobs",
        "monitoring_configs",
        "monitoring_jobs",
        "monitoring_logs",
        "monitoring_results"
    ]
    
    # Confirm deletion
    print("⚠️  WARNING: This will permanently delete ALL data from the following collections:")
    for col in collections:
        print(f"   - {col}")
    print()
    
    response = input("Are you sure you want to proceed? Type 'DELETE ALL' to confirm: ")
    if response != "DELETE ALL":
        print("❌ Deletion cancelled.")
        sys.exit(0)
    
    print("\n🔥 Starting deletion process...")
    
    try:
        # Initialize Firebase
        cred_dict = {
            "type": "service_account",
            "project_id": settings.FIREBASE_PROJECT_ID,
            "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
            "private_key": settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n') if settings.FIREBASE_PRIVATE_KEY else None,
            "client_email": settings.FIREBASE_CLIENT_EMAIL,
            "client_id": settings.FIREBASE_CLIENT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.FIREBASE_CLIENT_EMAIL}"
        }
        
        cred = credentials.Certificate(cred_dict)
        app = firebase_admin.initialize_app(cred)
        db = firestore.client()
        
        print("✅ Connected to Firestore")
        print()
        
        # Delete each collection
        total_deleted = 0
        for collection_name in collections:
            print(f"📂 Deleting collection: {collection_name}")
            count = delete_collection(db, collection_name)
            total_deleted += count
            if count > 0:
                print(f"✅ Deleted {count} documents from {collection_name}")
            else:
                print(f"ℹ️  Collection {collection_name} was already empty")
            print()
        
        print(f"✅ Successfully deleted {total_deleted} total documents")
        print("🎉 All data has been removed from Firestore!")
        
    except Exception as e:
        print(f"❌ Error during deletion: {str(e)}")
        sys.exit(1)
    finally:
        # Cleanup
        if firebase_admin._apps:
            firebase_admin.delete_app(app)


if __name__ == "__main__":
    main()
