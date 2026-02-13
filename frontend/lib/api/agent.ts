/**
 * Chat API Client - Multi-Agent System
 * Handles communication with the unified multi-agent backend
 */

import { getAuthHeaders } from '../auth-headers';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const API_V1_URL = `${API_BASE_URL}/api/v1`;

// ── Types ────────────────────────────────────────────────────────────

export interface AgentChatRequest {
  message: string;
  thread_id?: string;
  user_id?: string;
}

export interface AgentChatResponse {
  message: string;
  thread_id: string;
  agent?: string;
}

export type StreamEventType = 'routing' | 'token' | 'interrupt' | 'done' | 'error';

export interface RoutingEvent {
  type: 'routing';
  agent: string;
  task: string;
  confidence: number;
}

export interface TokenEvent {
  type: 'token';
  content: string;
}

export interface InterruptEvent {
  type: 'interrupt';
  data: InterruptData[];
}

export interface InterruptData {
  id?: string;
  value: {
    action_requests?: ActionRequest[];
    [key: string]: any;
  };
}

export interface ActionRequest {
  id?: string;
  name?: string;
  action: string;
  args: Record<string, any>;
  description?: string;
}

export interface ErrorEvent {
  type: 'error';
  message: string;
}

export interface DoneEvent {
  type: 'done';
}

export type StreamEvent = RoutingEvent | TokenEvent | InterruptEvent | ErrorEvent | DoneEvent;

export interface HITLDecision {
  type: 'approve' | 'edit' | 'reject';
  interrupt_id?: string;
  action?: string;
  args?: Record<string, any>;
  feedback?: string;
}

export interface AgentResumeRequest {
  agent_name: string;
  thread_id: string;
  decisions: HITLDecision[];
  user_id?: string;
}

export interface AgentResumeResponse {
  message: string;
  thread_id: string;
  completed: boolean;
}

export interface ChatMessage {
  id: string;
  user_id: string;
  message: string;
  type: string;
  sender: string;
  timestamp: string;
  metadata?: {
    competitor?: string;
    aspects?: string[];
    is_significant?: boolean;
    significance_score?: number;
    result_id?: string;
    config_id?: string;
  };
}

// ── API Functions ────────────────────────────────────────────────────

/**
 * Send a message to the chat API (non-streaming)
 */
export async function sendAgentMessage(request: AgentChatRequest): Promise<AgentChatResponse> {
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
    console.error('Error sending agent message:', error);
    throw error;
  }
}

/**
 * Stream a message to the chat API
 */
export function streamAgentMessage(
  request: AgentChatRequest,
  onEvent: (event: StreamEvent) => void,
  onError?: (error: Error) => void,
  onComplete?: () => void
): () => void {
  let aborted = false;
  const abortController = new AbortController();

  (async () => {
    try {
      const response = await fetch(`${API_V1_URL}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: abortController.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      while (!aborted) {
        const { done, value } = await reader.read();

        if (done) {
          onComplete?.();
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6)) as StreamEvent;
              onEvent(data);

              if (data.type === 'done') {
                onComplete?.();
                return;
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (error) {
      if (!aborted) {
        console.error('Stream error:', error);
        onError?.(error instanceof Error ? error : new Error('Unknown error'));
      }
    }
  })();

  // Return cleanup function
  return () => {
    aborted = true;
    abortController.abort();
  };
}

/**
 * Resume an interrupted execution (non-streaming)
 */
export async function resumeAgent(request: AgentResumeRequest): Promise<AgentResumeResponse> {
  try {
    const response = await fetch(`${API_V1_URL}/chat/resume`, {
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
    console.error('Error resuming agent:', error);
    throw error;
  }
}

/**
 * Resume an interrupted agent execution with streaming
 */
export function streamResumeAgent(
  request: AgentResumeRequest,
  onEvent: (event: StreamEvent) => void,
  onError?: (error: Error) => void,
  onComplete?: () => void
): () => void {
  let aborted = false;
  const abortController = new AbortController();

  (async () => {
    try {
      const response = await fetch(`${API_V1_URL}/chat/resume/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: abortController.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      while (!aborted) {
        const { done, value } = await reader.read();

        if (done) {
          onComplete?.();
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6)) as StreamEvent;
              onEvent(data);

              if (data.type === 'done') {
                onComplete?.();
                return;
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (error) {
      if (!aborted) {
        console.error('Resume stream error:', error);
        onError?.(error instanceof Error ? error : new Error('Unknown error'));
      }
    }
  })();

  // Return cleanup function
  return () => {
    aborted = true;
    abortController.abort();
  };
}

/**
 * Get chat messages (monitoring updates, etc.)
 */
export async function getChatMessages(
  limit: number = 50,
  messageType?: string
): Promise<ChatMessage[]> {
  try {
    const headers = await getAuthHeaders();
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    if (messageType) {
      params.append('message_type', messageType);
    }

    const response = await fetch(`${API_V1_URL}/chat/messages?${params}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Failed to get chat messages: ${error}`);
    }

    return response.json();
  } catch (error) {
    console.error('Get chat messages error:', error);
    throw error;
  }
}
