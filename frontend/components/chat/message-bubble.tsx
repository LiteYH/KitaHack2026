"use client"

import { Bot, User } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import type { Components } from "react-markdown"
import { CampaignAnalyticsCard } from "./campaign-analytics-card"
import { CampaignVisualization } from "./campaign-visualization"
import type { CampaignDataAttachment } from "@/lib/api/chat"

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  campaignData?: CampaignDataAttachment
}

interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user"

  const markdownComponents: Components = {
    // Custom styling for markdown elements
    p: ({ children }) => <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>,
    h1: ({ children }) => <h1 className="text-xl font-bold mb-2 mt-4 first:mt-0">{children}</h1>,
    h2: ({ children }) => <h2 className="text-lg font-bold mb-2 mt-3 first:mt-0">{children}</h2>,
    h3: ({ children }) => <h3 className="text-base font-bold mb-2 mt-2 first:mt-0">{children}</h3>,
    ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
    ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
    li: ({ children }) => <li className="leading-relaxed">{children}</li>,
    strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
    em: ({ children }) => <em className="italic">{children}</em>,
    code: ({ children, className }) => {
      const isInline = !className
      return isInline ? (
        <code className="bg-muted px-1.5 py-0.5 rounded text-xs font-mono">{children}</code>
      ) : (
        <code className="block bg-muted p-3 rounded-lg text-xs font-mono overflow-x-auto my-2">{children}</code>
      )
    },
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-primary pl-4 italic my-2">{children}</blockquote>
    ),
    a: ({ children, href }) => (
      <a href={href} className="text-primary hover:underline" target="_blank" rel="noopener noreferrer">
        {children}
      </a>
    ),
  }

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-primary/10 text-primary"
        }`}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>
      <div
        className={`max-w-[70%] rounded-2xl px-4 py-3 text-sm ${
          isUser
            ? "bg-primary text-primary-foreground"
            : "border border-border bg-card text-foreground"
        }`}
      >
        {isUser ? (
          <div className="leading-relaxed">{message.content}</div>
        ) : (
          <>
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={markdownComponents}
              >
                {message.content}
              </ReactMarkdown>
            </div>
            {/* Render campaign analytics card if present */}
            {message.campaignData && (
              <>
                <CampaignAnalyticsCard
                  campaigns={message.campaignData.campaigns}
                  metrics={message.campaignData.metrics}
                  summary={message.campaignData.summary}
                  type={message.campaignData.type}
                />
                {/* Render visualization prompt if requested */}
                {message.campaignData.show_visualization && (
                  <div className="mt-3">
                    <CampaignVisualization 
                      campaigns={message.campaignData.campaigns}
                    />
                  </div>
                )}
              </>
            )}
          </>
        )}
      </div>
    </div>
  )
}
