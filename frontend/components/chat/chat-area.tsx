"use client"

import { useState, useRef, useEffect } from "react"
import { UiGraphLogo } from "./uigraph-logo"
import { SuggestionCards } from "./suggestion-cards"
import { ChatInput } from "./chat-input"
import { MessageBubble, type Message } from "./message-bubble"
import { sendChatMessage, type ChatMessage as APIChatMessage } from "@/lib/api/chat"
import { useAuth } from "@/contexts/AuthContext"

export function ChatArea() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { user } = useAuth()

  const showWelcome = messages.length === 0

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSend = async (text: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
    }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Convert messages to API format for conversation history
      const conversationHistory: APIChatMessage[] = messages.map(msg => ({
        role: msg.role as "user" | "assistant",
        content: msg.content,
      }))

      // Call the API
      const response = await sendChatMessage({
        message: text,
        conversation_history: conversationHistory,
        user_id: user?.uid,
      })

      // Add assistant response
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.message,
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error("Error sending message:", error)
      
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
            {isLoading && (
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
          disabled={isLoading}
        />
      </div>
    </div>
  )
}
