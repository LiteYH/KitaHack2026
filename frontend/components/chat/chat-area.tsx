"use client"

import { useState, useRef, useEffect } from "react"
import { UiGraphLogo } from "./uigraph-logo"
import { SuggestionCards } from "./suggestion-cards"
import { ChatInput } from "./chat-input"
import { MessageBubble, type Message } from "./message-bubble"

const ASSISTANT_RESPONSES: Record<string, string> = {
  "Generate marketing content for my social media campaign":
    "I can help you generate engaging content! Let me create compelling text, eye-catching images, and video concepts for your campaign. What's your target audience and key message? I'll generate platform-optimized content for Facebook, Instagram, LinkedIn, and Twitter.",
  "Analyze my competitors' marketing strategies":
    "I'll scrape and analyze your competitors' content across multiple platforms. I've identified their top-performing posts, engagement patterns, and trending content. Their strategy focuses on short-form videos (68% engagement), user-generated content, and weekly contests. Would you like detailed insights?",
  "Schedule and publish my content automatically":
    "Your content is ready to be published! I can automatically post to Facebook, Instagram, LinkedIn, Twitter, and TikTok. Set your preferred posting schedule, and I'll optimize posting times based on your audience's activity patterns. Want to review the queue?",
  "How can I optimize my current campaigns?":
    "Based on your campaign data, I recommend: 1) Shift 30% budget to Instagram Reels (3x higher ROI). 2) A/B test your call-to-action buttons. 3) Reduce ad spend on Facebook by 15% and increase LinkedIn by 20%. 4) Update ad creatives - current ones are showing fatigue. Expected ROI improvement: +42%.",
  "Show me my ROI dashboard and campaign performance":
    "Your ROI Dashboard shows: Campaign A: $12,450 revenue, 340% ROI. Campaign B: $8,200 revenue, 280% ROI. Overall profit: $20,650 with 22% month-over-month growth. Top performing channel: Instagram (45% of conversions). Download detailed reports or view AI insights?",
  "Monitor competitors and suggest response strategies":
    "Continuous monitoring active! Competitor X just launched a flash sale campaign (30% off). Recommendation: Counter with a limited-time bundle offer + free shipping within 4 hours. Competitor Y's viral post gained 10K shares - I've analyzed their content style and prepared a similar template for you.",
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
