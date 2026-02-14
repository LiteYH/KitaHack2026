/**
 * Chat History API Client
 *
 * Handles retrieving and managing chat history from Firestore via backend API.
 */

import { getAuthHeaders } from '../auth-headers';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const API_V1_URL = `${API_BASE_URL}/api/v1`;

// ── Types ────────────────────────────────────────────────────────────

export interface ChatHistoryMessage {
  id: string;
  thread_id: string;
  user_id: string;
  role: 'user' | 'assistant' | 'tool_call' | 'tool_result' | 'agent_status' | 'system';
  content: string;
  timestamp?: string;
  created_at: string;
  agent?: string;
  tool_args?: Record<string, any>;
  tool_call_id?: string;
  node?: string;
  metadata?: Record<string, any>;
}

export interface ClearThreadResponse {
  status: string;
  thread_id: string;
  deleted_count: number;
  message: string;
}

// ── API Functions ────────────────────────────────────────────────────

/**
 * Load chat history for a specific thread.
 * Retrieves all messages from Firestore to restore a conversation.
 */
export async function loadThreadHistory(
  threadId: string,
  limit: number = 100
): Promise<ChatHistoryMessage[]> {
  try {
    const headers = await getAuthHeaders();
    const response = await fetch(
      `${API_V1_URL}/chat/history/${threadId}?limit=${limit}`,
      {
        method: 'GET',
        headers,
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to load history: ${response.statusText}`);
    }

    const messages = await response.json();
    return messages;
  } catch (error) {
    console.error(`[HISTORY] Failed to load thread ${threadId}:`, error);
    throw error;
  }
}

/**
 * Clear all messages in a thread.
 * Deletes chat history from Firestore.
 */
export async function clearThreadHistory(threadId: string): Promise<ClearThreadResponse> {
  try {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_V1_URL}/chat/history/${threadId}`, {
      method: 'DELETE',
      headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to clear history: ${response.statusText}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error(`[HISTORY] Failed to clear thread ${threadId}:`, error);
    throw error;
  }
}

/**
 * Get monitoring update messages (proactive notifications from cron jobs).
 * These are displayed in the chat as system messages.
 */
export async function getMonitoringMessages(
  limit: number = 50
): Promise<ChatHistoryMessage[]> {
  try {
    const headers = await getAuthHeaders();
    const response = await fetch(
      `${API_V1_URL}/chat/messages?message_type=monitoring_update&limit=${limit}`,
      {
        method: 'GET',
        headers,
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to load monitoring messages: ${response.statusText}`);
    }

    const messages = await response.json();
    return messages;
  } catch (error) {
    console.error('[HISTORY] Failed to load monitoring messages:', error);
    throw error;
  }
}
