/**
 * Agent Chat Area Component
 * 
 * Enhanced chat interface with multi-agent support and HITL
 */

"use client"

import { useState, useRef, useEffect } from "react"
import { UiGraphLogo } from "./uigraph-logo"
import { SuggestionCards } from "./suggestion-cards"
import { ChatInput } from "./chat-input"
import { MessageBubble } from "./message-bubble"
import { HITLApprovalCard } from "./hitl-approval-card"
import { ResolvedHITLCard } from "./resolved-hitl-card"
import { useAgentChat, type ChatMessage } from "@/hooks/use-agent-chat"
import { useAuth } from "@/contexts/AuthContext"
import { Badge } from "@/components/ui/badge"

export function AgentChatArea() {
  const [inputValue, setInputValue] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { user } = useAuth()

  const {
    messages,
    isLoading,
    interrupt,
    currentAgent,
    collapsedMessages,
    sendMessage,
    resumeWithDecision,
    clearMessages,
    toggleMessageCollapse,
  } = useAgentChat(user?.uid)

  const showWelcome = messages.length === 0

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, interrupt])

  const handleSend = (text: string) => {
    sendMessage(text)
  }

  const handleSuggestionSelect = (text: string) => {
    handleSend(text)
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      {/* Agent indicator */}
      {currentAgent && !showWelcome && (
        <div className="shrink-0 border-b border-border bg-muted/50 px-6 py-2">
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">Current Agent:</span>
            <Badge variant="secondary" className="text-xs">
              {currentAgent.replace('_', ' ')}
            </Badge>
          </div>
        </div>
      )}

      {/* Scrollable content area */}
      <div className="flex flex-1 flex-col overflow-y-auto">
        {showWelcome ? (
          <div className="flex flex-1 flex-col items-center justify-center px-6 pb-4">
            <div className="mb-4">
              <UiGraphLogo className="h-24 w-24" />
            </div>
            <h2 className="text-xl font-bold text-foreground">BossolutionAI</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Your AI Marketing Assistant with Multi-Agent Intelligence
            </p>
          </div>
        ) : (
          <div className="flex flex-1 flex-col gap-4 px-6 py-6">
            {messages
              .filter((msg) => msg.role !== 'system')
              .map((msg) => {
                // Handle HITL messages
                if (msg.role === 'hitl') {
                  const isActiveInterrupt = interrupt?.messageId === msg.id;
                  const isResolved = !!msg.resolution;

                  return (
                    <div key={msg.id} className="flex items-start gap-3">
                      <div key={`${msg.id}-avatar`} className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
                        <span className="text-xs font-semibold text-primary">AI</span>
                      </div>
                      <div key={`${msg.id}-content`} className="flex-1">
                        {isActiveInterrupt && msg.interruptData ? (
                          <HITLApprovalCard
                            key={`${msg.id}-approval`}
                            interruptData={msg.interruptData}
                            onDecision={resumeWithDecision}
                          />
                        ) : isResolved && msg.interruptData && msg.resolution ? (
                          <ResolvedHITLCard
                            key={`${msg.id}-resolved`}
                            interruptData={msg.interruptData}
                            resolution={msg.resolution}
                            isCollapsed={collapsedMessages.has(msg.id)}
                            onToggleCollapse={() => toggleMessageCollapse(msg.id)}
                          />
                        ) : null}
                      </div>
                    </div>
                  );
                }

                // Handle regular messages
                return (
                  <MessageBubble 
                    key={msg.id} 
                    message={{
                      id: msg.id,
                      role: msg.role as 'user' | 'assistant',
                      content: msg.content,
                    }}
                  />
                );
              })}

            {/* Loading indicator */}
            {isLoading && (
              <div key="loading-indicator" className="flex items-start gap-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
                  <div className="h-4 w-4 animate-pulse rounded-full bg-primary" />
                </div>
                <div className="flex flex-col gap-2">
                  <div className="h-4 w-32 animate-pulse rounded bg-muted" />
                  <div className="h-4 w-24 animate-pulse rounded bg-muted" />
                </div>
              </div>
            )}
            <div key="messages-end" ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Bottom section: suggestions + input */}
      <div className="shrink-0 border-t border-border bg-card/50 px-6 pb-5 pt-4">
        {showWelcome && (
          <div className="mb-4">
            <SuggestionCards onSelect={handleSuggestionSelect} />
          </div>
        )}
        <ChatInput
          value={inputValue}
          onChange={setInputValue}
          onSend={handleSend}
          disabled={isLoading || !!interrupt}
        />
      </div>
    </div>
  )
}
