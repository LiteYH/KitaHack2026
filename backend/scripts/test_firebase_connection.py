"""
Test script to verify Firebase connection and ROI data access
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.firebase import initialize_firebase

def test_firebase_connection():
    print("=" * 60)
    print("🔍 FIREBASE CONNECTION TEST")
    print("=" * 60)
    
    # Initialize Firebase
    print("\n1️⃣  Testing Firebase initialization...")
    app, db = initialize_firebase()
    
    if db is None:
        print("❌ FAILED: Firebase not initialized")
        return False
    
    print("✅ SUCCESS: Firebase initialized")
    
    # Test ROI collection access
    print("\n2️⃣  Testing ROI collection access...")
    try:
        roi_collection = db.collection('ROI')
        print(f"✅ SUCCESS: ROI collection reference created: {roi_collection}")
    except Exception as e:
        print(f"❌ FAILED: Cannot access ROI collection: {e}")
        return False
    
    # Get all documents (limit 5 for testing)
    print("\n3️⃣  Testing document retrieval (first 5 documents)...")
    try:
        docs = roi_collection.limit(5).stream()
        doc_count = 0
        for doc in docs:
            doc_count += 1
            doc_data = doc.to_dict()
            print(f"\n   📄 Document {doc_count}:")
            print(f"      ID: {doc.id}")
            print(f"      User Email: {doc_data.get('user_email', 'NOT FOUND')}")
            print(f"      Title: {doc_data.get('title', 'NOT FOUND')}")
            print(f"      Top-level keys: {list(doc_data.keys())}")
            
            # Check structure
            has_metrics = 'metrics' in doc_data
            has_costs = 'costs' in doc_data
            has_revenue = 'revenue' in doc_data
            has_roi_analysis = 'roi_analysis' in doc_data
            
            print(f"      Structure check:")
            print(f"         - Has 'metrics': {has_metrics}")
            print(f"         - Has 'costs': {has_costs}")
            print(f"         - Has 'revenue': {has_revenue}")
            print(f"         - Has 'roi_analysis': {has_roi_analysis}")
            
            if has_metrics:
                print(f"         - 'metrics' contains: {list(doc_data['metrics'].keys())}")
            if has_revenue:
                print(f"         - 'revenue' contains: {list(doc_data['revenue'].keys())}")
            if has_costs:
                print(f"         - 'costs' contains: {list(doc_data['costs'].keys())}")
            if has_roi_analysis:
                print(f"         - 'roi_analysis' contains: {list(doc_data['roi_analysis'].keys())}")
        
        if doc_count == 0:
            print("   ⚠️  WARNING: No documents found in ROI collection")
        else:
            print(f"\n   ✅ SUCCESS: Found {doc_count} document(s)")
            
    except Exception as e:
        print(f"❌ FAILED: Error retrieving documents: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test specific user query
    print("\n4️⃣  Testing user-specific query...")
    test_email = "limjl0130@gmail.com"
    print(f"   Filtering by user_email: {test_email}")
    
    try:
        query = roi_collection.where('user_email', '==', test_email)
        docs = query.stream()
        
        user_doc_count = 0
        for doc in docs:
            user_doc_count += 1
            doc_data = doc.to_dict()
            if user_doc_count == 1:
                print(f"\n   📄 Sample document for {test_email}:")
                print(f"      ID: {doc.id}")
                print(f"      Title: {doc_data.get('title', 'NOT FOUND')}")
                print(f"      Views: {doc_data.get('metrics', {}).get('views', 'NOT FOUND')}")
                print(f"      ROI: {doc_data.get('roi_analysis', {}).get('roi_percent', 'NOT FOUND')}%")
        
        print(f"\n   Found {user_doc_count} document(s) for {test_email}")
        
        if user_doc_count == 0:
            print(f"   ⚠️  WARNING: No documents found for {test_email}")
            print(f"   This is why the chatbot says 'couldn't find any ROI data'")
            print(f"\n   💡 SOLUTION: Run the populate_mock_roi_data.py script to add data")
        else:
            print(f"   ✅ SUCCESS: User data exists!")
            
    except Exception as e:
        print(f"❌ FAILED: Error querying user data: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✅ FIREBASE CONNECTION TEST COMPLETE")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_firebase_connection()
    
    if not success:
        print("\n❌ Some tests failed. Check the errors above.")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)
