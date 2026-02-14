/**
 * Campaign API Client
 * Handles communication with the backend campaign service
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const API_V1_URL = `${API_BASE_URL}/api/v1`;

export interface Campaign {
  id?: string;
  userID: string;
  campaignName: string;
  totalBudget: number;
  amountSpent: number;
  impressions: number;
  clicks: number;
  purchases: number;
  conversionValue: number;
  platform: string;
  status: 'ongoing' | 'paused';
  startDate: string;
  endDate: string;
  createdAt: string;
}

export interface CampaignMetrics {
  campaign_id: string;
  campaign_name: string;
  ctr: number;
  cvr: number;
  roas: number;
  budget_utilization: number;
  cost_per_click: number;
  cost_per_conversion: number;
}

export interface CampaignListResponse {
  campaigns: Campaign[];
  total_count: number;
  metrics_summary?: {
    total_campaigns: number;
    total_budget: number;
    total_spent: number;
    total_impressions: number;
    total_clicks: number;
    total_purchases: number;
    total_conversion_value: number;
    overall_ctr: number;
    overall_cvr: number;
    overall_roas: number;
    overall_budget_utilization: number;
    average_ctr: number;
    average_cvr: number;
    average_roas: number;
  };
}

export interface GetCampaignsParams {
  user_id: string;
  status?: 'ongoing' | 'paused';
  platform?: string;
  limit?: number;
}

/**
 * Fetch campaigns for a user with optional filters
 */
export async function getCampaigns(params: GetCampaignsParams): Promise<CampaignListResponse> {
  try {
    const queryParams = new URLSearchParams({
      user_id: params.user_id,
    });

    if (params.status) {
      queryParams.append('status', params.status);
    }
    if (params.platform) {
      queryParams.append('platform', params.platform);
    }
    if (params.limit) {
      queryParams.append('limit', params.limit.toString());
    }

    const response = await fetch(`${API_V1_URL}/campaigns?${queryParams.toString()}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching campaigns:', error);
    throw error;
  }
}

/**
 * Fetch a specific campaign by ID
 */
export async function getCampaignById(campaignId: string, userId: string): Promise<Campaign> {
  try {
    const response = await fetch(
      `${API_V1_URL}/campaigns/${campaignId}?user_id=${userId}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching campaign:', error);
    throw error;
  }
}

/**
 * Fetch metrics for a specific campaign
 */
export async function getCampaignMetrics(
  campaignId: string,
  userId: string
): Promise<CampaignMetrics> {
  try {
    const response = await fetch(
      `${API_V1_URL}/campaigns/${campaignId}/metrics?user_id=${userId}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching campaign metrics:', error);
    throw error;
  }
}

/**
 * Check campaign service health
 */
export async function checkCampaignServiceHealth(): Promise<{ status: string; service: string }> {
  try {
    const response = await fetch(`${API_V1_URL}/campaigns/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error checking campaign service health:', error);
    throw error;
  }
}
