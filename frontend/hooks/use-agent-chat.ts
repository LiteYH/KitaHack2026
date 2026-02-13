/**
 * useAgentChat Hook
 * 
 * Custom hook for multi-agent chat with streaming and HITL support
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { 
  streamAgentMessage, 
  streamResumeAgent,
  getChatMessages,
  type StreamEvent, 
  type AgentChatRequest,
  type HITLDecision,
  type InterruptData,
  type ChatMessage as APIChatMessage,
} from '@/lib/api/agent';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system' | 'hitl';
  content: string;
  agent?: string;
  interruptData?: InterruptData[];
  resolution?: {
    type: 'approve' | 'edit' | 'reject';
    decisions: HITLDecision[];
    timestamp: number;
  };
}

export interface InterruptState {
  messageId: string; // Link to the message in chat history
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
  // Initialize thread_id immediately - persists across all messages until clearMessages
  const [threadId, setThreadId] = useState<string>(() => crypto.randomUUID());
  
  const cleanupRef = useRef<(() => void) | null>(null);
  const currentMessageRef = useRef<ChatMessage | null>(null);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      cleanupRef.current?.();
    };
  }, []);

  const sendMessage = useCallback((text: string) => {
    // Add user message
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: text,
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setInterrupt(null);

    // Prepare assistant message
    currentMessageRef.current = {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: '',
    };

    const request: AgentChatRequest = {
      message: text,
      thread_id: threadId, // Always use the persistent thread_id
      user_id: userId,
    };

    cleanupRef.current = streamAgentMessage(
      request,
      (event: StreamEvent) => {
        console.log('[STREAM EVENT]', event.type, event);
        switch (event.type) {
          case 'routing':
            console.log('[ROUTING] Agent:', event.agent, 'Task:', event.task);
            setCurrentAgent(event.agent);
            if (currentMessageRef.current) {
              currentMessageRef.current.agent = event.agent;
            }
            break;

          case 'token':
            console.log('[TOKEN] Raw content type:', typeof event.content, 'Value:', event.content);
            if (currentMessageRef.current) {
              // Normalize content: AIMessage.content can be a list of blocks
              const tokenContent = typeof event.content === 'string'
                ? event.content
                : Array.isArray(event.content)
                  ? (event.content as Array<{text?: string}>).map((b) => b.text ?? '').join('')
                  : String(event.content ?? '');
              console.log('[TOKEN] Normalized content:', tokenContent);
              currentMessageRef.current.content += tokenContent;
              setMessages((prev) => {
                const lastMsg = prev[prev.length - 1];
                if (lastMsg?.id === currentMessageRef.current?.id) {
                  // Update existing message
                  return [
                    ...prev.slice(0, -1),
                    { ...currentMessageRef.current! },
                  ];
                } else {
                  // Add new message
                  return [...prev, { ...currentMessageRef.current! }];
                }
              });
            }
            break;

          case 'interrupt':
            // Save interrupt state with agent name AND add to message history
            console.log('[INTERRUPT] Data:', event.data);
            const interruptMessageId = crypto.randomUUID();
            const interruptMessage: ChatMessage = {
              id: interruptMessageId,
              role: 'hitl',
              content: 'Approval required for monitoring configuration',
              agent: currentAgent || 'competitor_monitoring',
              interruptData: event.data,
            };
            setMessages((prev) => [...prev, interruptMessage]);
            // Use the existing thread ID
            setInterrupt({
              messageId: interruptMessageId,
              threadId: threadId,
              agentName: currentAgent || 'competitor_monitoring',
              data: event.data,
            });
            setIsLoading(false);
            break;

          case 'done':
            console.log('[DONE] Stream completed');
            setIsLoading(false);
            currentMessageRef.current = null;
            break;

          case 'error':
            console.error('[ERROR] Stream error:', event.message);
            setIsLoading(false);
            if (currentMessageRef.current) {
              currentMessageRef.current.content = 
                `Error: ${event.message}. Please try again.`;
              setMessages((prev) => [...prev, { ...currentMessageRef.current! }]);
            }
            currentMessageRef.current = null;
            break;
        }
      },
      (error) => {
        console.error('[STREAM] Connection error:', error);
        setIsLoading(false);
        const errorMessage: ChatMessage = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
        };
        setMessages((prev) => [...prev, errorMessage]);
        currentMessageRef.current = null;
      }
    );
  }, [userId, threadId]);

  const resumeWithDecision = useCallback((decisions: HITLDecision[]) => {
    if (!interrupt) return;

    console.log('[RESUME] Starting with decisions:', decisions);
    
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

    // Prepare assistant message for resume
    currentMessageRef.current = {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: '',
    };

    cleanupRef.current = streamResumeAgent(
      {
        agent_name: interrupt.agentName,
        thread_id: interrupt.threadId,
        decisions,
        user_id: userId,
      },
      (event: StreamEvent) => {
        console.log('[RESUME EVENT]', event.type, event);
        switch (event.type) {
          case 'token':
            console.log('[RESUME TOKEN] Raw content type:', typeof event.content, 'Value:', event.content);
            if (currentMessageRef.current) {
              // Normalize content: AIMessage.content can be a list of blocks
              const resumeTokenContent = typeof event.content === 'string'
                ? event.content
                : Array.isArray(event.content)
                  ? (event.content as Array<{text?: string}>).map((b) => b.text ?? '').join('')
                  : String(event.content ?? '');
              console.log('[RESUME TOKEN] Normalized content:', resumeTokenContent);
              currentMessageRef.current.content += resumeTokenContent;
              setMessages((prev) => {
                const lastMsg = prev[prev.length - 1];
                if (lastMsg?.id === currentMessageRef.current?.id) {
                  return [
                    ...prev.slice(0, -1),
                    { ...currentMessageRef.current! },
                  ];
                } else {
                  return [...prev, { ...currentMessageRef.current! }];
                }
              });
            }
            break;

          case 'interrupt':
            // Another interrupt occurred
            console.log('[RESUME INTERRUPT] Another interrupt:', event.data);
            const newInterruptMessageId = crypto.randomUUID();
            const newInterruptMessage: ChatMessage = {
              id: newInterruptMessageId,
              role: 'hitl',
              content: 'Additional approval required',
              agent: interrupt.agentName,
              interruptData: event.data,
            };
            setMessages((prev) => [...prev, newInterruptMessage]);
            setInterrupt({
              messageId: newInterruptMessageId,
              threadId: interrupt.threadId,
              agentName: interrupt.agentName,
              data: event.data,
            });
            setIsLoading(false);
            break;

          case 'done':
            console.log('[RESUME DONE] Resume completed');
            setIsLoading(false);
            currentMessageRef.current = null;
            break;

          case 'error':
            console.error('[RESUME ERROR]:', event.message);
            setIsLoading(false);
            const errorMessage: ChatMessage = {
              id: crypto.randomUUID(),
              role: 'assistant',
              content: `Error: ${event.message}`,
            };
            setMessages((prev) => [...prev, errorMessage]);
            currentMessageRef.current = null;
            break;
        }
      },
      (error) => {
        console.error('[RESUME] Stream error:', error);
        setIsLoading(false);
        const errorMessage: ChatMessage = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: 'Sorry, I encountered an error resuming. Please try again.',
        };
        setMessages((prev) => [...prev, errorMessage]);
        currentMessageRef.current = null;
      }
    );
  }, [interrupt, userId]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setThreadId(crypto.randomUUID()); // Generate new thread for new conversation
    setCurrentAgent(null);
    setInterrupt(null);
    setCollapsedMessages(new Set());
    console.log('[CLEAR] Starting new conversation with new thread ID');
  }, []);

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
