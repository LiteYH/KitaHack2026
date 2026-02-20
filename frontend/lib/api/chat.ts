/**
 * Chat API Client
 * Handles communication with the backend chat service
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const API_V1_URL = `${API_BASE_URL}/api/v1`;

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatRequest {
  message: string;
  conversation_history?: ChatMessage[];
  user_id?: string;
}

export interface CampaignDataAttachment {
  type: 'analytics' | 'edit_request';
  campaigns: any[];
  metrics: any[];
  summary: any;
  intent: any;
  show_visualization?: boolean;
}

export interface ChatResponse {
  message: string;
  conversation_id?: string | null;
  campaign_data?: CampaignDataAttachment | null;
}

/**
 * Send a message to the chat API and get a response
 */
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_V1_URL}/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
}

/**
 * Stream chat responses from the API
 * @param request Chat request
 * @param onChunk Callback for each chunk received
 * @param onComplete Callback when streaming is complete
 * @param onError Callback for errors
 */
export async function streamChatMessage(
  request: ChatRequest,
  onChunk: (chunk: string) => void,
  onComplete?: () => void,
  onError?: (error: Error) => void
): Promise<void> {
  try {
    const response = await fetch(`${API_V1_URL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('No response body');
    }

    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        onComplete?.();
        break;
      }

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            if (data.done) {
              onComplete?.();
              return;
            }
            if (data.content) {
              onChunk(data.content);
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e);
          }
        }
      }
    }
  } catch (error) {
    console.error('Error streaming chat message:', error);
    onError?.(error instanceof Error ? error : new Error('Unknown error'));
  }
}

/**
 * Check chat service health
 */
export async function checkChatHealth(): Promise<{ status: string; service: string; model: string }> {
  try {
    const response = await fetch(`${API_V1_URL}/chat/health`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error checking chat health:', error);
    throw error;
  }
}
