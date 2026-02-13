"use client"

import { useState, useRef, useEffect } from "react"
import { UiGraphLogo } from "./uigraph-logo"
import { SuggestionCards } from "./suggestion-cards"
import { ChatInput } from "./chat-input"
import { MessageBubble, type Message } from "./message-bubble"

const ASSISTANT_RESPONSES: Record<string, string> = {
  "Show me the backend flow for user authentication":
    "The user authentication flow starts with the client sending credentials to the /api/auth/login endpoint. The server validates the credentials against the database, generates a JWT token pair (access + refresh), and returns them in an HTTP-only cookie. Middleware checks the token on each protected route request.",
  "What business rules apply to payment processing?":
    "Payment processing follows these business rules: 1) All transactions over $10,000 require additional verification. 2) Refunds must be processed within 30 days. 3) Currency conversion uses real-time exchange rates. 4) Failed payments trigger an automatic retry after 24 hours.",
  "Are there any open bugs on the dashboard project?":
    "There are currently 3 open bugs on the dashboard project: 1) Chart rendering lag on mobile devices (P2). 2) Date filter not resetting properly (P1). 3) Export CSV missing header row (P3). The P1 bug is assigned to the frontend team for this sprint.",
  "Explain the API endpoints for the trading platform":
    "The Trading API has the following key endpoints: GET /api/trades - list all trades, POST /api/trades - create a new trade, GET /api/portfolio - get portfolio summary, WebSocket /ws/prices - real-time price streaming. All endpoints require Bearer token authentication.",
  "Who is responsible for the crypto dashboard?":
    "The crypto dashboard is owned by Sarah Chen (Engineering Lead). The frontend is maintained by the UI team (3 engineers), and the data pipeline is managed by the Data Engineering team. For urgent issues, contact #crypto-dashboard on Slack.",
  "Show me recent deployments and their status":
    "Here are the recent deployments: 1) v2.4.1 - Production - Deployed 2h ago (Success). 2) v2.4.0 - Staging - Deployed yesterday (Success). 3) v2.3.9 - Production - Rolled back due to memory leak (Failed). All deployments are tracked in the CI/CD pipeline.",
}

export function ChatArea() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const showWelcome = messages.length === 0

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSend = (text: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
    }
    setMessages((prev) => [...prev, userMessage])

    setTimeout(() => {
      const response =
        ASSISTANT_RESPONSES[text] ||
        `Thanks for asking about "${text}". I'm looking into that for you. In the meantime, feel free to explore the suggestion cards or ask another question!`
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response,
      }
      setMessages((prev) => [...prev, assistantMessage])
    }, 800)
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
            <h2 className="text-xl font-bold text-foreground">UiGraph Chat</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Ask me about your project!
            </p>
          </div>
        ) : (
          <div className="flex flex-1 flex-col gap-4 px-6 py-6">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
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
        />
      </div>
    </div>
  )
}
