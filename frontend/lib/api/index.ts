/**
 * API Client Index
 * Central export for all API services
 */

// Chat API
export {
  sendChatMessage,
  streamChatMessage,
  checkChatServiceHealth,
  type ChatMessage,
  type ChatRequest,
  type ChatResponse,
} from './chat';

// Campaign API
export {
  getCampaigns,
  getCampaignById,
  getCampaignMetrics,
  checkCampaignServiceHealth,
  type Campaign,
  type CampaignMetrics,
  type CampaignListResponse,
  type GetCampaignsParams,
} from './campaigns';
