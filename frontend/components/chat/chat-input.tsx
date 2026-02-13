"use client"

import { useState, type FormEvent } from "react"
import { Paperclip, Mic, Send } from "lucide-react"

interface ChatInputProps {
  onSend: (message: string) => void
  value: string
  onChange: (value: string) => void
  disabled?: boolean
}

export function ChatInput({ onSend, value, onChange, disabled = false }: ChatInputProps) {
  const [isFocused, setIsFocused] = useState(false)

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (!value.trim() || disabled) return
    onSend(value.trim())
    onChange("")
  }

  return (
    <form
      onSubmit={handleSubmit}
      className={`flex items-center gap-2 rounded-xl border bg-card px-4 py-2.5 transition-colors ${
        isFocused ? "border-primary shadow-sm" : "border-border"
      } ${disabled ? "opacity-50" : ""}`}
    >
      <button
        type="button"
        className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:text-foreground disabled:cursor-not-allowed disabled:opacity-50"
        aria-label="Attach file"
        disabled={disabled}
      >
        <Paperclip className="h-4 w-4" />
      </button>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        placeholder="Type your message here"
        className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground focus:outline-none disabled:cursor-not-allowed"
        disabled={disabled}
      />
      <button
        type="button"
        className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:text-foreground disabled:cursor-not-allowed disabled:opacity-50"
        aria-label="Voice input"
        disabled={disabled}
      >
        <Mic className="h-4 w-4" />
      </button>
      <button
        type="submit"
        disabled={!value.trim() || disabled}
        className="flex h-8 shrink-0 items-center gap-1.5 rounded-lg bg-primary px-3 text-xs font-medium text-primary-foreground transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
        aria-label="Send message"
      >
        <Send className="h-3.5 w-3.5" />
        Send
      </button>
    </form>
  )
}
