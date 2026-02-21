# How to Delete Old ROI Data

## Option 1: Firebase Console (Recommended)

1. Go to Firebase Console: https://console.firebase.google.com
2. Select your project: `kitahack2026`
3. Go to Firestore Database
4. Navigate to the `ROI` collection
5. Delete the old documents that have flat structure:
   - Click on each document (like `2ifXAckhxLNDmlvt3oEC`)
   - Click the trash icon at the top
   - Confirm deletion

## Option 2: Delete by User Email (Python Script)

If you want to delete all ROI data for a specific user before regenerating:

```python
# In your backend directory, create: scripts/delete_roi_data.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.firebase import initialize_firebase

def delete_user_roi_data(user_email: str):
    app, db = initialize_firebase()
    
    if db is None:
        print("❌ Firebase not initialized")
        return
    
    roi_collection = db.collection('ROI')
    docs = roi_collection.where('user_email', '==', user_email).stream()
    
    count = 0
    for doc in docs:
        doc.reference.delete()
        count += 1
        print(f"🗑️  Deleted: {doc.id}")
    
    print(f"\n✅ Deleted {count} documents for {user_email}")

if __name__ == "__main__":
    USER_EMAIL = "limjl0130@gmail.com"
    delete_user_roi_data(USER_EMAIL)
```

## Option 3: Delete All ROI Data (Use with Caution!)

Only use this if you want to completely clear the ROI collection:

```python
def delete_all_roi_data():
    app, db = initialize_firebase()
    
    if db is None:
        print("❌ Firebase not initialized")
        return
    
    roi_collection = db.collection('ROI')
    docs = roi_collection.stream()
    
    count = 0
    for doc in docs:
        doc.reference.delete()
        count += 1
        print(f"🗑️  Deleted: {doc.id}")
    
    print(f"\n✅ Deleted {count} total documents")
```

## Recommendation

**Best approach:**
1. Use Firebase Console to manually delete the old flat-structure documents
2. Or just leave them - the new script will add properly structured data
3. Run the populate script to add new data with correct structure
4. The code will work with the new data (nested structure)
