#!/usr/bin/env python3
"""
Firebase/Firestore Client for Backend
Handles Firestore operations using the existing Firebase setup
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import the existing Firebase setup
from app.core.firebase import get_db, initialize_firebase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FirestoreClient:
    """
    Firestore client that uses the existing Firebase Admin SDK setup
    """
    
    def __init__(self):
        self.db = None
        self.firebase_available = False
        
        try:
            # Use existing Firebase initialization
            logger.info("🔧 Getting Firestore client from existing Firebase setup...")
            self.db = get_db()
            
            if self.db is not None:
                self.firebase_available = True
                logger.info("✅ Firestore client ready")
            else:
                logger.warning("⚠️ Firestore client not available - Firebase may not be configured")
                
        except Exception as e:
            logger.error(f"❌ Failed to get Firestore client: {e}")
            self.firebase_available = False
    
    async def get_youtube_roi_data(self, user_id: Optional[str] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Fetch YouTube ROI data from Firestore 'roi_metrics' collection
        """
        try:
            if not self.firebase_available or not self.db:
                logger.error("❌ Firestore client not available")
                return []
            
            logger.info(f"🔍 Fetching YouTube ROI data from Firestore (limit: {limit})...")
            
            # Query the roi_metrics collection
            collection_ref = self.db.collection('roi_metrics')
            query = collection_ref
            
            # Filter by user_id if provided
            if user_id:
                query = query.where('user_id', '==', user_id)
            
            # Order by created_at and limit results
            query = query.order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)
            
            # Execute query
            docs = query.stream()
            
            # Convert documents to list of dictionaries
            data = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data['id'] = doc.id  # Add document ID
                data.append(doc_data)
            
            logger.info(f"✅ Retrieved {len(data)} YouTube ROI records from Firestore")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error fetching YouTube ROI data: {str(e)}")
            return []
    
    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get statistics about a Firestore collection
        """
        try:
            if not self.firebase_available or not self.db:
                return {"error": "Firestore not available"}
            
            collection_ref = self.db.collection(collection_name)
            docs = collection_ref.stream()
            
            count = sum(1 for _ in docs)
            
            return {
                "collection": collection_name,
                "document_count": count,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting collection stats: {str(e)}")
            return {"error": str(e)}


# Create a singleton instance
firestore_client = FirestoreClient()


if __name__ == "__main__":
    # Test the Firestore client
    import asyncio
    
    async def test():
        client = FirestoreClient()
        
        # Test getting YouTube ROI data
        data = await client.get_youtube_roi_data(limit=10)
        print(f"Retrieved {len(data)} records")
        
        # Test collection stats
        stats = await client.get_collection_stats('roi_metrics')
        print(f"Collection stats: {stats}")
    
    asyncio.run(test())
