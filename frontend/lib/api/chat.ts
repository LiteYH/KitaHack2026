/**
 * Chat API Client - Multi-Agent System
 * Handles communication with the unified multi-agent backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const API_V1_URL = `${API_BASE_URL}/api/v1`;

// ── Types ────────────────────────────────────────────────────────────

export interface ChartConfig {
  type: 'bar' | 'line' | 'pie' | 'area';
  title: string;
  data: any[];
  xKey?: string;
  yKey?: string;
  yLabel?: string;
  lines?: Array<{
    key: string;
    color: string;
    label: string;
  }>;
}

export interface ApprovalDecision {
  thread_id: string;
  approved: boolean;
  tool_name?: string;
}

export interface ApprovalRequest {
  tool_name: string;
  tool_args: any;
  message: string;
  thread_id: string;
  requires_approval: boolean;
}

export interface AgentChatRequest {
  message: string;
  thread_id?: string;
  user_id?: string;
  user_email?: string;
  approval_decision?: ApprovalDecision;
}

export interface AgentChatResponse {
  message: string;
  thread_id: string;
  agent?: string;
  charts?: ChartConfig[];
  requires_approval?: boolean;
  approval_request?: ApprovalRequest;
  filter_context?: {
    days?: number;
    user_email?: string;
  };
}

export type StreamEventType = 'routing' | 'metadata' | 'token' | 'interrupt' | 'done' | 'error';

export interface MetadataEvent {
  type: 'metadata';
  thread_id: string;
}

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

export type StreamEvent = RoutingEvent | MetadataEvent | TokenEvent | InterruptEvent | ErrorEvent | DoneEvent;

export interface HITLDecision {
  type: 'approve' | 'edit' | 'reject';
  interrupt_id?: string;
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
      console.log('[API] Starting stream request:', request);
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
        console.log('[API/STREAM] Received chunk:', chunk.substring(0, 200));
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const rawData = line.slice(6);
            console.log('[API/STREAM] Parsing SSE line:', rawData.substring(0, 200));
            try {
              const data = JSON.parse(rawData) as StreamEvent;
              console.log('[API/STREAM] Parsed event:', data.type, data);
              onEvent(data);

              if (data.type === 'done') {
                console.log('[API/STREAM] Stream done signal received');
                onComplete?.();
                return;
              }
            } catch (e) {
              console.error('[API/STREAM] Error parsing SSE data:', e, 'Raw:', rawData);
            }
          }
        }
      }
    } catch (error) {
      if (!aborted) {
        console.error('[API/STREAM] Stream error:', error);
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
      console.log('[API/RESUME] Starting resume stream request:', request);
      const response = await fetch(`${API_V1_URL}/chat/resume/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: abortController.signal,
      });

      if (!response.ok) {
        console.error('[API/RESUME] HTTP error:', response.status, response.statusText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      console.log('[API/RESUME] Stream connected successfully');
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
        console.log('[API/RESUME] Received chunk:', chunk.substring(0, 200));
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const rawData = line.slice(6);
            console.log('[API/RESUME] Parsing SSE line:', rawData.substring(0, 200));
            try {
              const data = JSON.parse(rawData) as StreamEvent;
              console.log('[API/RESUME] Parsed event:', data.type, data);
              onEvent(data);

              if (data.type === 'done') {
                console.log('[API/RESUME] Stream done signal received');
                onComplete?.();
                return;
              }
            } catch (e) {
              console.error('[API/RESUME] Error parsing SSE data:', e, 'Raw:', rawData);
            }
          }
        }
      }
    } catch (error) {
      if (!aborted) {
        console.error('[API/RESUME] Stream error:', error);
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
