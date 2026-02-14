/**
 * useAgentChat Hook
 *
 * Custom hook for multi-agent chat with full streaming support.
 * Captures ALL intermediate events: tool calls, tool results, agent status, tokens, HITL.
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import {
  streamAgentMessage,
  streamResumeAgent,
  type StreamEvent,
  type AgentChatRequest,
  type HITLDecision,
  type InterruptData,
} from '@/lib/api/agent';
import {
  loadThreadHistory,
  clearThreadHistory,
  type ChatHistoryMessage,
} from '@/lib/api/chat-history';

// ── Message types ────────────────────────────────────────────────────

export type MessageRole =
  | 'user'
  | 'assistant'
  | 'tool_call'
  | 'tool_result'
  | 'agent_status'
  | 'hitl'
  | 'system';

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  /** Tool or agent name */
  agent?: string;
  /** Tool call arguments (for tool_call messages) */
  toolArgs?: Record<string, any>;
  /** Tool call ID linking call → result */
  toolCallId?: string;
  /** Graph node that produced the message */
  node?: string;
  /** HITL interrupt data */
  interruptData?: InterruptData[];
  /** HITL resolution data */
  resolution?: {
    type: 'approve' | 'edit' | 'reject';
    decisions: HITLDecision[];
    timestamp: number;
  };
  /** Timestamp */
  timestamp: number;
}

export interface InterruptState {
  messageId: string;
  threadId: string;
  agentName: string;
  data: InterruptData[];
}

export interface UseAgentChatReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  interrupt: InterruptState | null;
  currentAgent: string | null;
  collapsedMessages: Set<string>;
  sendMessage: (text: string) => void;
  resumeWithDecision: (decisions: HITLDecision[]) => void;
  clearMessages: () => void;
  toggleMessageCollapse: (messageId: string) => void;
}

export function useAgentChat(userId?: string): UseAgentChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [interrupt, setInterrupt] = useState<InterruptState | null>(null);
  const [currentAgent, setCurrentAgent] = useState<string | null>(null);
  const [collapsedMessages, setCollapsedMessages] = useState<Set<string>>(new Set());
  
  // Load thread ID from localStorage or generate new one
  const [threadId, setThreadId] = useState<string>(() => {
    if (typeof window !== 'undefined') {
      const savedThreadId = localStorage.getItem('chat_thread_id');
      if (savedThreadId) {
        console.log('[THREAD] Loaded thread from localStorage:', savedThreadId);
        return savedThreadId;
      }
    }
    const newThreadId = crypto.randomUUID();
    console.log('[THREAD] Created new thread:', newThreadId);
    return newThreadId;
  });

  const cleanupRef = useRef<(() => void) | null>(null);
  const currentMessageRef = useRef<ChatMessage | null>(null);
  const currentAgentRef = useRef<string | null>(null);
  const threadIdRef = useRef<string>(threadId);

  // Keep refs synced
  useEffect(() => { currentAgentRef.current = currentAgent; }, [currentAgent]);
  useEffect(() => { 
    threadIdRef.current = threadId;
    // Persist thread ID to localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('chat_thread_id', threadId);
    }
  }, [threadId]);

  useEffect(() => {
    return () => {
      cleanupRef.current?.();
    };
  }, []);

  // Auto-collapse intermediate messages when streaming completes
  const prevLoadingRef = useRef(isLoading);
  useEffect(() => {
    // Detect when streaming transitions from true to false
    if (prevLoadingRef.current && !isLoading) {
      // Find all collapsible intermediate messages that should be auto-collapsed
      const messagesToCollapse = messages
        .filter((msg) => {
          // Collapse tool calls and tool results
          if (msg.role === 'tool_call' || msg.role === 'tool_result') {
            return true;
          }
          // Collapse resolved HITL cards
          if (msg.role === 'hitl' && msg.resolution) {
            return true;
          }
          return false;
        })
        .map((msg) => msg.id);

      if (messagesToCollapse.length > 0) {
        setCollapsedMessages((prev) => {
          const next = new Set(prev);
          messagesToCollapse.forEach((id) => next.add(id));
          return next;
        });
      }
    }
    prevLoadingRef.current = isLoading;
  }, [isLoading, messages]);

  // Load chat history from Firestore on mount (only if userId is available)
  useEffect(() => {
    if (!userId || !threadId) return;

    let mounted = true;

    const loadHistory = async () => {
      try {
        setIsLoading(true);
        
        // Load thread history (includes both chat and monitoring messages)
        const historyMessages = await loadThreadHistory(threadId);

        if (!mounted) return;

        // Convert history messages to ChatMessage format
        const chatMessages: ChatMessage[] = historyMessages.map((msg) => {
          // Parse timestamp
          let timestamp = Date.now();
          if (msg.created_at) {
            const parsed = Date.parse(msg.created_at);
            if (!isNaN(parsed)) timestamp = parsed;
          }

          return {
            id: msg.id,
            role: msg.role as MessageRole,
            content: msg.content,
            agent: msg.agent,
            toolArgs: msg.tool_args,
            toolCallId: msg.tool_call_id,
            node: msg.node,
            timestamp,
          };
        });

        // Sort by timestamp
        chatMessages.sort((a, b) => a.timestamp - b.timestamp);

        if (chatMessages.length > 0) {
          setMessages(chatMessages);
          console.log(`[HISTORY] Loaded ${historyMessages.length} messages from thread ${threadId}`);
        }
      } catch (error) {
        console.error('[HISTORY] Failed to load chat history:', error);
        // Don't block the UI if history fails to load
      } finally {
        if (mounted) {
          setIsLoading(false);
        }
      }
    };

    loadHistory();

    return () => {
      mounted = false;
    };
  }, [userId, threadId]);

  /**
   * Process a stream event and update messages accordingly.
   * Handles ALL event types from the backend.
   */
  const processEvent = useCallback(
    (event: StreamEvent) => {
      switch (event.type) {
        case 'metadata':
          // Thread info — nothing to show in UI
          break;

        case 'agent_status': {
          // Which graph node is running
          const agentName = event.node || 'unknown';
          setCurrentAgent(agentName);
          currentAgentRef.current = agentName;

          const statusMsg: ChatMessage = {
            id: crypto.randomUUID(),
            role: 'agent_status',
            content: `Agent node: **${agentName}**`,
            agent: agentName,
            node: event.node,
            timestamp: Date.now(),
          };
          setMessages((prev) => [...prev, statusMsg]);
          break;
        }

        case 'tool_call': {
          // Agent decided to call a tool
          const toolCallMsg: ChatMessage = {
            id: crypto.randomUUID(),
            role: 'tool_call',
            content: `Calling **${event.name}**`,
            agent: event.name,
            toolArgs: event.args,
            toolCallId: event.tool_call_id,
            node: event.node,
            timestamp: Date.now(),
          };
          setMessages((prev) => [...prev, toolCallMsg]);
          setCurrentAgent(event.name);
          currentAgentRef.current = event.name;
          break;
        }

        case 'tool_result': {
          // Result from tool execution
          const toolResultMsg: ChatMessage = {
            id: crypto.randomUUID(),
            role: 'tool_result',
            content: event.content || '(empty result)',
            agent: event.name,
            toolCallId: event.tool_call_id,
            node: event.node,
            timestamp: Date.now(),
          };
          setMessages((prev) => [...prev, toolResultMsg]);
          break;
        }

        case 'token': {
          // LLM streaming token
          if (currentMessageRef.current) {
            const tokenContent =
              typeof event.content === 'string'
                ? event.content
                : Array.isArray(event.content)
                  ? (event.content as Array<{ text?: string }>)
                      .map((b) => b.text ?? '')
                      .join('')
                  : String(event.content ?? '');

            currentMessageRef.current.content += tokenContent;
            if (event.node) {
              currentMessageRef.current.node = event.node;
            }

            setMessages((prev) => {
              const idx = prev.findIndex(
                (m) => m.id === currentMessageRef.current?.id
              );
              if (idx !== -1) {
                // Assistant message exists — remove it and re-append at the end
                // This ensures it always appears AFTER all intermediate messages
                const filtered = prev.filter((m) => m.id !== currentMessageRef.current?.id);
                return [...filtered, { ...currentMessageRef.current! }];
              } else {
                // First token — append new assistant message
                return [...prev, { ...currentMessageRef.current! }];
              }
            });
          }
          break;
        }

        case 'interrupt': {
          // HITL approval request
          const interruptMessageId = crypto.randomUUID();
          const interruptMessage: ChatMessage = {
            id: interruptMessageId,
            role: 'hitl',
            content: 'Approval required for monitoring configuration',
            agent: currentAgentRef.current || 'competitor_monitoring',
            interruptData: event.data,
            timestamp: Date.now(),
          };
          setMessages((prev) => [...prev, interruptMessage]);
          setInterrupt({
            messageId: interruptMessageId,
            threadId: threadIdRef.current,
            agentName: currentAgentRef.current || 'competitor_monitoring',
            data: event.data,
          });
          setIsLoading(false);
          break;
        }

        case 'done':
          setIsLoading(false);
          currentMessageRef.current = null;
          break;

        case 'error':
          setIsLoading(false);
          if (currentMessageRef.current) {
            currentMessageRef.current.content = `Error: ${event.message}. Please try again.`;
            setMessages((prev) => [...prev, { ...currentMessageRef.current! }]);
          } else {
            setMessages((prev) => [
              ...prev,
              {
                id: crypto.randomUUID(),
                role: 'assistant',
                content: `Error: ${event.message}. Please try again.`,
                timestamp: Date.now(),
              },
            ]);
          }
          currentMessageRef.current = null;
          break;
      }
    },
    []
  );

  const sendMessage = useCallback(
    (text: string) => {
      // Add user message
      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'user',
        content: text,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setInterrupt(null);

      // Prepare assistant message ref for streaming tokens
      currentMessageRef.current = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: '',
        timestamp: Date.now(),
      };

      const request: AgentChatRequest = {
        message: text,
        thread_id: threadIdRef.current,
        user_id: userId,
      };

      cleanupRef.current = streamAgentMessage(
        request,
        processEvent,
        (error) => {
          console.error('[STREAM] Connection error:', error);
          setIsLoading(false);
          setMessages((prev) => [
            ...prev,
            {
              id: crypto.randomUUID(),
              role: 'assistant',
              content: 'Sorry, I encountered a connection error. Please try again.',
              timestamp: Date.now(),
            },
          ]);
          currentMessageRef.current = null;
        }
      );
    },
    [userId, processEvent]
  );

  const resumeWithDecision = useCallback(
    (decisions: HITLDecision[]) => {
      if (!interrupt) return;

      // Update the interrupt message with resolution
      const decisionType = decisions[0]?.type || 'approve';
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === interrupt.messageId
            ? {
                ...msg,
                resolution: {
                  type: decisionType,
                  decisions,
                  timestamp: Date.now(),
                },
              }
            : msg
        )
      );

      setIsLoading(true);
      setInterrupt(null);

      // Prepare assistant message ref for resume tokens
      currentMessageRef.current = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: '',
        timestamp: Date.now(),
      };

      cleanupRef.current = streamResumeAgent(
        {
          agent_name: interrupt.agentName,
          thread_id: interrupt.threadId,
          decisions,
          user_id: userId,
        },
        processEvent,
        (error) => {
          console.error('[RESUME] Stream error:', error);
          setIsLoading(false);
          setMessages((prev) => [
            ...prev,
            {
              id: crypto.randomUUID(),
              role: 'assistant',
              content: 'Sorry, I encountered an error resuming. Please try again.',
              timestamp: Date.now(),
            },
          ]);
          currentMessageRef.current = null;
        }
      );
    },
    [interrupt, userId, processEvent]
  );

  const clearMessages = useCallback(async () => {
    // Clear from Firestore if user is authenticated
    if (userId && threadIdRef.current) {
      try {
        await clearThreadHistory(threadIdRef.current);
        console.log(`[HISTORY] Cleared thread ${threadIdRef.current} from Firestore`);
      } catch (error) {
        console.error('[HISTORY] Failed to clear thread history:', error);
        // Continue with local clear even if Firestore clear fails
      }
    }

    // Clear local state
    setMessages([]);
    const newThreadId = crypto.randomUUID();
    setThreadId(newThreadId);
    threadIdRef.current = newThreadId;
    setCurrentAgent(null);
    currentAgentRef.current = null;
    setInterrupt(null);
    setCollapsedMessages(new Set());
  }, [userId]);

  const toggleMessageCollapse = useCallback((messageId: string) => {
    setCollapsedMessages((prev) => {
      const next = new Set(prev);
      if (next.has(messageId)) {
        next.delete(messageId);
      } else {
        next.add(messageId);
      }
      return next;
    });
  }, []);

  return {
    messages,
    isLoading,
    interrupt,
    currentAgent,
    collapsedMessages,
    sendMessage,
    resumeWithDecision,
    clearMessages,
    toggleMessageCollapse,
  };
}
