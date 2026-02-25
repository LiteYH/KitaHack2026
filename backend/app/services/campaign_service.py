"""
Campaign Service - Handles fetching and analyzing campaign data from Firestore
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.firebase import get_db
from app.schemas.campaign import Campaign, CampaignMetrics, CampaignFilter


class CampaignService:
    """Service for managing campaign data and metrics"""
    
    def __init__(self):
        """Initialize the campaign service"""
        self.collection_name = "campaign_details"
    
    async def get_campaigns(
        self,
        user_id: str,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Campaign]:
        """
        Fetch campaigns from Firestore based on filters
        
        Args:
            user_id: User ID to filter campaigns
            status: Optional status filter ("ongoing" or "paused")
            platform: Optional platform filter
            limit: Optional limit on number of results
            
        Returns:
            List of Campaign objects
        """
        try:
            db = get_db()
            if db is None:
                return []
            
            # Start with base query filtering by userID
            query = db.collection(self.collection_name).where("userID", "==", user_id)
            
            # Add status filter if provided
            if status:
                query = query.where("status", "==", status)
            
            # Add platform filter if provided
            if platform:
                query = query.where("platform", "==", platform)
            
            # Add limit if provided
            if limit:
                query = query.limit(limit)
            
            # Execute query
            docs = query.stream()
            
            campaigns = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id  # Add document ID
                
                # Convert Firestore timestamps to datetime
                if 'startDate' in data and hasattr(data['startDate'], 'timestamp'):
                    data['startDate'] = datetime.fromtimestamp(data['startDate'].timestamp())
                if 'endDate' in data and hasattr(data['endDate'], 'timestamp'):
                    data['endDate'] = datetime.fromtimestamp(data['endDate'].timestamp())
                if 'createdAt' in data and hasattr(data['createdAt'], 'timestamp'):
                    data['createdAt'] = datetime.fromtimestamp(data['createdAt'].timestamp())
                
                campaigns.append(Campaign(**data))
            
            return campaigns
            
        except Exception as e:
            print(f"Error fetching campaigns: {str(e)}")
            raise Exception(f"Failed to fetch campaigns: {str(e)}")
    
    async def create_campaign(
        self,
        campaign_data: Dict[str, Any]
    ) -> Campaign:
        """
        Create a new campaign in Firestore
        
        Args:
            campaign_data: Dictionary containing campaign fields
            
        Returns:
            Created Campaign object with auto-generated ID
        """
        try:
            db = get_db()
            if db is None:
                raise Exception("Database connection not available")
            
            # Add createdAt timestamp
            campaign_data['createdAt'] = datetime.now()
            
            # Create the document with auto-generated ID
            doc_ref = db.collection(self.collection_name).document()
            doc_ref.set(campaign_data)
            
            # Retrieve the created document
            doc = doc_ref.get()
            data = doc.to_dict()
            data['id'] = doc.id
            
            # Convert timestamps
            if 'startDate' in data and hasattr(data['startDate'], 'timestamp'):
                data['startDate'] = datetime.fromtimestamp(data['startDate'].timestamp())
            if 'endDate' in data and hasattr(data['endDate'], 'timestamp'):
                data['endDate'] = datetime.fromtimestamp(data['endDate'].timestamp())
            if 'createdAt' in data and hasattr(data['createdAt'], 'timestamp'):
                data['createdAt'] = datetime.fromtimestamp(data['createdAt'].timestamp())
            
            return Campaign(**data)
            
        except Exception as e:
            print(f"Error creating campaign: {str(e)}")
            raise Exception(f"Failed to create campaign: {str(e)}")
    
    async def get_campaign_by_id(self, campaign_id: str, user_id: str) -> Optional[Campaign]:
        """
        Fetch a specific campaign by ID
        
        Args:
            campaign_id: Campaign document ID
            user_id: User ID for authorization
            
        Returns:
            Campaign object or None if not found
        """
        try:
            db = get_db()
            if db is None:
                return None
            
            doc_ref = db.collection(self.collection_name).document(campaign_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
            
            data = doc.to_dict()
            
            # Verify ownership
            if data.get('userID') != user_id:
                return None
            
            data['id'] = doc.id
            
            # Convert timestamps
            if 'startDate' in data and hasattr(data['startDate'], 'timestamp'):
                data['startDate'] = datetime.fromtimestamp(data['startDate'].timestamp())
            if 'endDate' in data and hasattr(data['endDate'], 'timestamp'):
                data['endDate'] = datetime.fromtimestamp(data['endDate'].timestamp())
            if 'createdAt' in data and hasattr(data['createdAt'], 'timestamp'):
                data['createdAt'] = datetime.fromtimestamp(data['createdAt'].timestamp())
            
            return Campaign(**data)
            
        except Exception as e:
            print(f"Error fetching campaign by ID: {str(e)}")
            return None
    
    async def update_campaign(
        self,
        campaign_id: str,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Campaign]:
        """
        Update a campaign's fields in Firestore
        
        Args:
            campaign_id: Campaign document ID
            user_id: User ID for authorization
            updates: Dictionary of fields to update
            
        Returns:
            Updated Campaign object or None if failed
        """
        try:
            db = get_db()
            if db is None:
                return None
            
            # First verify the campaign exists and belongs to the user
            doc_ref = db.collection(self.collection_name).document(campaign_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
            
            data = doc.to_dict()
            if data.get('userID') != user_id:
                return None
            
            # Update only allowed fields
            allowed_fields = ['totalBudget', 'status', 'amountSpent', 'impressions', 
                            'clicks', 'purchases', 'conversionValue', 'endDate']
            
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
            
            if not filtered_updates:
                return await self.get_campaign_by_id(campaign_id, user_id)
            
            # Perform the update
            doc_ref.update(filtered_updates)
            
            # Return the updated campaign
            return await self.get_campaign_by_id(campaign_id, user_id)
            
        except Exception as e:
            print(f"Error updating campaign: {str(e)}")
            return None
    
    def calculate_metrics(self, campaign: Campaign) -> CampaignMetrics:
        """
        Calculate performance metrics for a campaign
        
        Args:
            campaign: Campaign object
            
        Returns:
            CampaignMetrics object with calculated metrics
        """
        # Calculate CTR (Click-Through Rate)
        ctr = (campaign.clicks / campaign.impressions * 100) if campaign.impressions > 0 else 0
        
        # Calculate CVR (Conversion Rate)
        cvr = (campaign.purchases / campaign.clicks * 100) if campaign.clicks > 0 else 0
        
        # Calculate ROAS (Return on Ad Spend)
        roas = (campaign.conversionValue / campaign.amountSpent) if campaign.amountSpent > 0 else 0
        
        # Calculate Budget Utilization
        budget_utilization = (campaign.amountSpent / campaign.totalBudget * 100) if campaign.totalBudget > 0 else 0
        
        # Calculate Cost Per Click
        cost_per_click = (campaign.amountSpent / campaign.clicks) if campaign.clicks > 0 else 0
        
        # Calculate Cost Per Conversion
        cost_per_conversion = (campaign.amountSpent / campaign.purchases) if campaign.purchases > 0 else 0
        
        return CampaignMetrics(
            campaign_id=campaign.id or "",
            campaign_name=campaign.campaignName,
            ctr=round(ctr, 2),
            cvr=round(cvr, 2),
            roas=round(roas, 2),
            budget_utilization=round(budget_utilization, 2),
            cost_per_click=round(cost_per_click, 2),
            cost_per_conversion=round(cost_per_conversion, 2)
        )
    
    async def get_campaigns_with_metrics(
        self,
        user_id: str,
        status: Optional[str] = None,
        platform: Optional[str] = None
    ) -> tuple[List[Campaign], List[CampaignMetrics]]:
        """
        Fetch campaigns and calculate their metrics
        
        Args:
            user_id: User ID to filter campaigns
            status: Optional status filter
            platform: Optional platform filter
            
        Returns:
            Tuple of (campaigns list, metrics list)
        """
        campaigns = await self.get_campaigns(user_id, status, platform)
        metrics = [self.calculate_metrics(campaign) for campaign in campaigns]
        return campaigns, metrics
    
    def generate_metrics_summary(self, campaigns: List[Campaign], metrics: List[CampaignMetrics]) -> Dict[str, Any]:
        """
        Generate aggregated metrics summary across multiple campaigns
        
        Args:
            campaigns: List of Campaign objects
            metrics: List of CampaignMetrics objects
            
        Returns:
            Dictionary with summary statistics
        """
        if not campaigns:
            return {}
        
        total_budget = sum(c.totalBudget for c in campaigns)
        total_spent = sum(c.amountSpent for c in campaigns)
        total_impressions = sum(c.impressions for c in campaigns)
        total_clicks = sum(c.clicks for c in campaigns)
        total_purchases = sum(c.purchases for c in campaigns)
        total_conversion_value = sum(c.conversionValue for c in campaigns)
        
        avg_ctr = sum(m.ctr for m in metrics) / len(metrics) if metrics else 0
        avg_cvr = sum(m.cvr for m in metrics) / len(metrics) if metrics else 0
        avg_roas = sum(m.roas for m in metrics) / len(metrics) if metrics else 0
        
        return {
            "total_campaigns": len(campaigns),
            "total_budget": total_budget,
            "total_spent": total_spent,
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_purchases": total_purchases,
            "total_conversion_value": total_conversion_value,
            "overall_ctr": round((total_clicks / total_impressions * 100) if total_impressions > 0 else 0, 2),
            "overall_cvr": round((total_purchases / total_clicks * 100) if total_clicks > 0 else 0, 2),
            "overall_roas": round((total_conversion_value / total_spent) if total_spent > 0 else 0, 2),
            "overall_budget_utilization": round((total_spent / total_budget * 100) if total_budget > 0 else 0, 2),
            "average_ctr": round(avg_ctr, 2),
            "average_cvr": round(avg_cvr, 2),
            "average_roas": round(avg_roas, 2)
        }


# Singleton instance
campaign_service = CampaignService()
