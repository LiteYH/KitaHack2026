"use client"

import { useState, useRef, useEffect } from "react"
import { UiGraphLogo } from "./uigraph-logo"
import { SuggestionCards } from "./suggestion-cards"
import { ChatInput } from "./chat-input"
import { MessageBubble, type Message } from "./message-bubble"
import { sendChatMessage, type ChatMessage as APIChatMessage, type ChartConfig, type ApprovalRequest } from "@/lib/api/chat"
import { useAuth } from "@/contexts/AuthContext"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

export function ChatArea() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [pendingApproval, setPendingApproval] = useState<ApprovalRequest | null>(null)
  const [threadId, setThreadId] = useState<string | undefined>(undefined)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { user } = useAuth()

  const showWelcome = messages.length === 0

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, pendingApproval])

  const handleSend = async (text: string, approvalDecision?: { approved: boolean; thread_id: string }) => {
    // Don't add user message if this is an approval decision
    if (!approvalDecision) {
      const userMessage: Message = {
        id: crypto.randomUUID(),
        role: "user",
        content: text,
      }
      setMessages((prev) => [...prev, userMessage])
    }
    
    setIsLoading(true)

    try {
      // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      // AUTHENTICATED USER EMAIL RETRIEVAL FOR ROI DATA ACCESS
      // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      // 
      // When users ask ROI-related questions, the backend needs their Gmail to:
      // 1. Query Firebase ROI collection (filtered by user_email field)
      // 2. Ensure data privacy (user only sees their own data)
      // 3. Provide personalized analytics and insights
      //
      // Flow:
      // 1. User is authenticated via Firebase Auth (AuthContext)
      // 2. Get user's email from auth context (user?.email)
      // 3. Pass email to backend in chat request
      // 4. Backend triggers LangGraph agent with user email in context
      // 5. If AI detects ROI query → LangGraph HITL requests approval
      // 6. User approves → Backend queries Firebase with user_email filter
      // 7. ROI data is analyzed and returned with charts
      //
      // Security:
      // - User must be authenticated to have email
      // - Firebase rules enforce user_email filtering
      // - No cross-user data access possible
      // - Approval dialog explains data access before execution
      // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      
      const userEmail = user?.email
      const userId = user?.uid

      // Log for debugging (remove in production for privacy)
      if (userEmail) {
        console.log("📧 [AUTH] User Gmail retrieved for ROI queries:", userEmail)
      } else {
        console.warn("⚠️ [AUTH] No user email found - ROI queries will require login")
      }

      // Convert messages to API format for conversation history
      const conversationHistory: APIChatMessage[] = messages.map(msg => ({
        role: msg.role as "user" | "assistant",
        content: msg.content,
      }))

      // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      // SEND REQUEST TO BACKEND WITH USER EMAIL
      // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      // The backend will:
      // - Include user_email in LangGraph agent context
      // - AI automatically detects ROI queries
      // - LangGraph HITL pauses and requests approval for ROI data access
      // - If approved: Queries Firebase: WHERE user_email == userEmail
      // - Returns analysis with charts
      // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      
      const response = await sendChatMessage({
        message: approvalDecision ? "" : text,
        conversation_history: conversationHistory,
        user_id: userId,
        user_email: userEmail, // 🔑 Key: Pass Gmail to backend for Firebase ROI query
        thread_id: threadId,
        approval_decision: approvalDecision ? {
          thread_id: approvalDecision.thread_id,
          approved: approvalDecision.approved,
          tool_name: pendingApproval?.tool_name
        } : undefined
      })

      // Store thread_id for subsequent requests
      if (response.thread_id) {
        setThreadId(response.thread_id)
      }

      // Check if approval is required
      if (response.requires_approval && response.approval_request) {
        // Show approval request UI
        setPendingApproval(response.approval_request)
        
        // Add the approval request message to the chat
        const approvalMessage: Message = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.message,
        }
        setMessages((prev) => [...prev, approvalMessage])
      } else {
        // Clear any pending approval
        setPendingApproval(null)
        
        // Add assistant response with charts and filter context if present
        const assistantMessage: Message = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.message,
          charts: response.charts,
          filterContext: response.filter_context,
        }
        setMessages((prev) => [...prev, assistantMessage])
      }
    } catch (error) {
      console.error("Error sending message:", error)
      
      // Clear pending approval on error
      setPendingApproval(null)
      
      // Show error message to user
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "Sorry, I encountered an error processing your message. Please try again.",
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleApprovalDecision = async (approved: boolean) => {
    if (!pendingApproval) return

    // Add a visual confirmation of the user's choice
    const decisionMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: approved ? "Yes" : "No",
    }
    setMessages((prev) => [...prev, decisionMessage])

    // Send the approval decision
    await handleSend("", {
      approved,
      thread_id: pendingApproval.thread_id
    })

    // Clear pending approval
    setPendingApproval(null)
  }

  const handleSuggestionSelect = (text: string) => {
    handleSend(text)
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      {/* Scrollable content area */}
      <div className="flex flex-1 flex-col overflow-y-auto">
        {showWelcome ? (
          <div className="flex flex-1 flex-col items-center justify-center px-6 pb-4">
            <div className="mb-4">
              <UiGraphLogo className="h-24 w-24" />
            </div>
            <h2 className="text-xl font-bold text-foreground">BossolutionAI</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Your AI Marketing Assistant
            </p>
          </div>
        ) : (
          <div className="flex flex-1 flex-col gap-4 px-6 py-6">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {isLoading && !pendingApproval && (
              <div className="flex items-start gap-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
                  <div className="h-4 w-4 animate-pulse rounded-full bg-primary" />
                </div>
                <div className="flex flex-col gap-2">
                  <div className="h-4 w-32 animate-pulse rounded bg-muted" />
                  <div className="h-4 w-24 animate-pulse rounded bg-muted" />
                </div>
              </div>
            )}
            
            {/* Approval Request UI */}
            {pendingApproval && (
              <Card className="p-4 border-2 border-primary/20 bg-primary/5">
                <div className="flex flex-col gap-3">
                  <p className="text-sm font-medium">Do you approve this data access?</p>
                  <div className="flex gap-3">
                    <Button
                      onClick={() => handleApprovalDecision(true)}
                      disabled={isLoading}
                      className="flex-1"
                    >
                      Yes
                    </Button>
                    <Button
                      onClick={() => handleApprovalDecision(false)}
                      disabled={isLoading}
                      variant="outline"
                      className="flex-1"
                    >
                      No
                    </Button>
                  </div>
                </div>
              </Card>
            )}
            
            <div ref={messagesEndRef} />
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
          disabled={isLoading || !!pendingApproval}
        />
      </div>
    </div>
  )
}
