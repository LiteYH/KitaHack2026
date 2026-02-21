"""
Delete all ROI data for a specific user to regenerate with correct dates
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.firebase import initialize_firebase

def delete_user_roi_data(user_email: str):
    """
    Delete all ROI data for a specific user
    
    Args:
        user_email: Email of the user whose data to delete
    """
    print("=" * 60)
    print("🗑️  DELETE USER ROI DATA")
    print("=" * 60)
    print(f"User: {user_email}")
    print(f"⚠️  WARNING: This will delete ALL ROI documents for this user!")
    print("=" * 60)
    
    # Initialize Firebase
    app, db = initialize_firebase()
    
    if db is None:
        print("❌ Firebase not initialized")
        return
    
    try:
        roi_collection = db.collection('ROI')
        
        # Query documents for this user
        print(f"\n🔍 Querying documents for: {user_email}")
        docs = roi_collection.where('user_email', '==', user_email).stream()
        
        # Delete each document
        count = 0
        doc_ids = []
        for doc in docs:
            doc_ids.append(doc.id)
            count += 1
        
        if count == 0:
            print(f"✅ No documents found for {user_email}")
            return
        
        print(f"📊 Found {count} document(s) to delete")
        print(f"\n⏳ Deleting documents...")
        
        deleted = 0
        for doc_id in doc_ids:
            roi_collection.document(doc_id).delete()
            deleted += 1
            if deleted % 5 == 0:
                print(f"   Deleted {deleted}/{count}...")
        
        print(f"\n✅ Successfully deleted {deleted} document(s) for {user_email}")
        print(f"📁 Collection: ROI")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error deleting data: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    USER_EMAIL = "limjl0130@gmail.com"
    
    delete_user_roi_data(USER_EMAIL)
    
    print(f"\n💡 Next step: Run populate_mock_roi_data.py to generate new data")
