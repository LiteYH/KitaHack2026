"use client"

import { Bot, User } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import type { Components } from "react-markdown"

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
}

interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user"

  const markdownComponents: Components = {
    // Custom styling for markdown elements
    p: ({ children, ...props }) => <p className="mb-2 last:mb-0 leading-relaxed" {...props}>{children}</p>,
    h1: ({ children, ...props }) => <h1 className="text-xl font-bold mb-2 mt-4 first:mt-0" {...props}>{children}</h1>,
    h2: ({ children, ...props }) => <h2 className="text-lg font-bold mb-2 mt-3 first:mt-0" {...props}>{children}</h2>,
    h3: ({ children, ...props }) => <h3 className="text-base font-bold mb-2 mt-2 first:mt-0" {...props}>{children}</h3>,
    ul: ({ children, ...props }) => <ul className="list-disc list-inside mb-2 space-y-1" {...props}>{children}</ul>,
    ol: ({ children, ...props }) => <ol className="list-decimal list-inside mb-2 space-y-1" {...props}>{children}</ol>,
    li: ({ children, node, ...props }) => <li className="leading-relaxed" {...props}>{children}</li>,
    strong: ({ children, ...props }) => <strong className="font-semibold" {...props}>{children}</strong>,
    em: ({ children, ...props }) => <em className="italic" {...props}>{children}</em>,
    code: ({ children, className, ...props }) => {
      const isInline = !className
      return isInline ? (
        <code className="bg-muted px-1.5 py-0.5 rounded text-xs font-mono" {...props}>{children}</code>
      ) : (
        <code className="block bg-muted p-3 rounded-lg text-xs font-mono overflow-x-auto my-2" {...props}>{children}</code>
      )
    },
    blockquote: ({ children, ...props }) => (
      <blockquote className="border-l-4 border-primary pl-4 italic my-2" {...props}>{children}</blockquote>
    ),
    a: ({ children, href, ...props }) => (
      <a href={href} className="text-primary hover:underline" target="_blank" rel="noopener noreferrer" {...props}>
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
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={markdownComponents}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  )
}
