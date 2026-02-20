from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class Campaign(BaseModel):
    """Campaign data model matching Firestore structure"""
    id: Optional[str] = Field(default=None, description="Document ID from Firestore")
    userID: str = Field(..., description="User ID who owns the campaign")
    campaignName: str = Field(..., description="Name of the campaign")
    totalBudget: int = Field(..., description="Total budget allocated")
    amountSpent: int = Field(..., description="Amount spent so far")
    impressions: int = Field(..., description="Number of impressions")
    clicks: int = Field(..., description="Number of clicks")
    purchases: int = Field(..., description="Number of purchases/conversions")
    conversionValue: int = Field(..., description="Total conversion value in currency")
    platform: str = Field(..., description="Platform (Instagram, Facebook, KOL, E-commerce, etc.)")
    status: Literal["ongoing", "paused"] = Field(..., description="Campaign status")
    startDate: datetime = Field(..., description="Campaign start date")
    endDate: datetime = Field(..., description="Campaign end date")
    createdAt: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "abc123",
                "userID": "DT4DNex2L1N2rZ9kPddEzqougK22",
                "campaignName": "Summer Sale 2026",
                "totalBudget": 5000,
                "amountSpent": 3200,
                "impressions": 150000,
                "clicks": 7500,
                "purchases": 180,
                "conversionValue": 27000,
                "platform": "Instagram",
                "status": "ongoing",
                "startDate": "2026-02-01T00:00:00",
                "endDate": "2026-02-28T00:00:00",
                "createdAt": "2026-02-01T00:00:00"
            }
        }


class CampaignMetrics(BaseModel):
    """Calculated metrics for a campaign"""
    campaign_id: str
    campaign_name: str
    ctr: float = Field(..., description="Click-Through Rate (clicks/impressions)")
    cvr: float = Field(..., description="Conversion Rate (purchases/clicks)")
    roas: float = Field(..., description="Return on Ad Spend (conversionValue/amountSpent)")
    budget_utilization: float = Field(..., description="Budget utilization percentage (amountSpent/totalBudget)")
    cost_per_click: float = Field(..., description="Cost per click (amountSpent/clicks)")
    cost_per_conversion: float = Field(..., description="Cost per conversion (amountSpent/purchases)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "campaign_id": "abc123",
                "campaign_name": "Summer Sale 2026",
                "ctr": 0.05,
                "cvr": 0.024,
                "roas": 8.44,
                "budget_utilization": 0.64,
                "cost_per_click": 0.43,
                "cost_per_conversion": 17.78
            }
        }


class CampaignFilter(BaseModel):
    """Filter parameters for fetching campaigns"""
    userID: str = Field(..., description="User ID to filter campaigns")
    status: Optional[Literal["ongoing", "paused"]] = Field(default=None, description="Filter by status")
    platform: Optional[str] = Field(default=None, description="Filter by platform")
    limit: Optional[int] = Field(default=None, description="Limit number of results")


class CampaignListResponse(BaseModel):
    """Response model for campaign list"""
    campaigns: List[Campaign]
    total_count: int
    metrics_summary: Optional[dict] = Field(default=None, description="Aggregated metrics across campaigns")


class CampaignAnalysisRequest(BaseModel):
    """Request for campaign analysis"""
    userID: str = Field(..., description="User ID")
    campaign_ids: Optional[List[str]] = Field(default=None, description="Specific campaign IDs to analyze")
    status: Optional[Literal["ongoing", "paused"]] = Field(default=None, description="Filter by status")
    analysis_type: Optional[str] = Field(default="optimization", description="Type of analysis (optimization, comparison, etc.)")


class CampaignAnalysisResponse(BaseModel):
    """Response for campaign analysis"""
    campaigns: List[Campaign]
    metrics: List[CampaignMetrics]
    insights: str = Field(..., description="AI-generated insights and recommendations")
    total_campaigns: int


class CampaignUpdateRequest(BaseModel):
    """Request model for updating campaign fields"""
    totalBudget: Optional[int] = Field(default=None, description="Updated total budget")
    status: Optional[Literal["ongoing", "paused"]] = Field(default=None, description="Updated campaign status")
    amountSpent: Optional[int] = Field(default=None, description="Updated amount spent")
    impressions: Optional[int] = Field(default=None, description="Updated impressions")
    clicks: Optional[int] = Field(default=None, description="Updated clicks")
    purchases: Optional[int] = Field(default=None, description="Updated purchases")
    conversionValue: Optional[int] = Field(default=None, description="Updated conversion value")
    
    class Config:
        json_schema_extra = {
            "example": {
                "totalBudget": 6000,
                "status": "paused"
            }
        }
