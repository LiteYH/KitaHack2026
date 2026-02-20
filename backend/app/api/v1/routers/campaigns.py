from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List
from app.schemas.campaign import (
    Campaign,
    CampaignMetrics,
    CampaignListResponse,
    CampaignAnalysisRequest,
    CampaignAnalysisResponse,
    CampaignUpdateRequest,
    CampaignCreateRequest
)
from app.services.campaign_service import campaign_service

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=CampaignListResponse, summary="Get user's campaigns")
async def get_campaigns(
    user_id: str = Query(..., description="User ID to fetch campaigns for"),
    status: Optional[str] = Query(None, description="Filter by status (ongoing/paused)"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    limit: Optional[int] = Query(None, description="Limit number of results")
):
    """
    Fetch campaigns for a specific user with optional filters
    
    Args:
        user_id: User ID to fetch campaigns for
        status: Optional status filter
        platform: Optional platform filter
        limit: Optional limit on results
        
    Returns:
        CampaignListResponse with campaigns and metrics
    """
    try:
        campaigns, metrics = await campaign_service.get_campaigns_with_metrics(
            user_id=user_id,
            status=status,
            platform=platform
        )
        
        # Apply limit if specified
        if limit and limit > 0:
            campaigns = campaigns[:limit]
            metrics = metrics[:limit]
        
        # Generate summary
        summary = campaign_service.generate_metrics_summary(campaigns, metrics)
        
        return CampaignListResponse(
            campaigns=campaigns,
            total_count=len(campaigns),
            metrics_summary=summary
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch campaigns: {str(e)}"
        )


@router.post("", response_model=Campaign, summary="Create a new campaign", status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign: CampaignCreateRequest
):
    """
    Create a new campaign
    
    Args:
        campaign: Campaign data to create
        
    Returns:
        Created Campaign object with auto-generated ID
    """
    try:
        # Convert Pydantic model to dict
        campaign_dict = campaign.model_dump()
        
        # Create the campaign
        created_campaign = await campaign_service.create_campaign(campaign_dict)
        
        return created_campaign
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )


@router.get("/{campaign_id}", response_model=Campaign, summary="Get a specific campaign")
async def get_campaign(
    campaign_id: str,
    user_id: str = Query(..., description="User ID for authorization")
):
    """
    Fetch a specific campaign by ID
    
    Args:
        campaign_id: Campaign document ID
        user_id: User ID for authorization
        
    Returns:
        Campaign object
    """
    try:
        campaign = await campaign_service.get_campaign_by_id(campaign_id, user_id)
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found or access denied"
            )
        
        return campaign
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch campaign: {str(e)}"
        )


@router.get("/{campaign_id}/metrics", response_model=CampaignMetrics, summary="Get campaign metrics")
async def get_campaign_metrics(
    campaign_id: str,
    user_id: str = Query(..., description="User ID for authorization")
):
    """
    Get calculated metrics for a specific campaign
    
    Args:
        campaign_id: Campaign document ID
        user_id: User ID for authorization
        
    Returns:
        CampaignMetrics object
    """
    try:
        campaign = await campaign_service.get_campaign_by_id(campaign_id, user_id)
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found or access denied"
            )
        
        metrics = campaign_service.calculate_metrics(campaign)
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate metrics: {str(e)}"
        )


@router.get("/health", summary="Check campaign service health")
async def health_check():
    """Check if the campaign service is operational"""
    try:
        return {
            "status": "healthy",
            "service": "campaigns"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Campaign service unavailable: {str(e)}"
        )


@router.put("/{campaign_id}", response_model=Campaign, summary="Update a campaign")
async def update_campaign(
    campaign_id: str,
    updates: CampaignUpdateRequest,
    user_id: str = Query(..., description="User ID for authorization")
):
    """
    Update a campaign's fields (budget, status, etc.)
    
    Args:
        campaign_id: Campaign document ID
        updates: Fields to update
        user_id: User ID for authorization
        
    Returns:
        Updated Campaign object
    """
    try:
        # Convert Pydantic model to dict, excluding None values
        update_dict = updates.model_dump(exclude_none=True)
        
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        updated_campaign = await campaign_service.update_campaign(
            campaign_id=campaign_id,
            user_id=user_id,
            updates=update_dict
        )
        
        if not updated_campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found or access denied"
            )
        
        return updated_campaign
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign: {str(e)}"
        )
