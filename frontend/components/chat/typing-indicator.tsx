"use client"

import { Bot } from "lucide-react"
import { useEffect, useState } from "react"

const typingMessages = [
  "Analyzing your request",
  "Processing data",
  "Generating insights",
  "Thinking",
  "Analyzing campaigns",
]

export function TypingIndicator() {
  const [messageIndex, setMessageIndex] = useState(0)
  const [dots, setDots] = useState("")

  // Rotate through different messages
  useEffect(() => {
    const messageInterval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % typingMessages.length)
    }, 3000) // Change message every 3 seconds

    return () => clearInterval(messageInterval)
  }, [])

  // Animate dots
  useEffect(() => {
    const dotsInterval = setInterval(() => {
      setDots((prev) => {
        if (prev === "...") return ""
        return prev + "."
      })
    }, 500) // Add dot every 500ms

    return () => clearInterval(dotsInterval)
  }, [])

  return (
    <div className="flex items-start gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
        <Bot className="h-4 w-4" />
      </div>
      <div className="max-w-[70%] rounded-2xl border border-border bg-card px-4 py-3 text-sm">
        <div className="flex items-center gap-2">
          <span className="text-foreground">{typingMessages[messageIndex]}</span>
          <span className="inline-block w-6 text-left text-primary">{dots}</span>
        </div>
      </div>
    </div>
  )
}
