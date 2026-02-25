"use client"

import { Bell, LayoutGrid, ChevronDown, Clock, Trash2 } from "lucide-react"
import { UserProfileDropdown } from "./user-profile-dropdown"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"

interface ChatHeaderProps {
  onClearMessages?: () => void;
  messageCount?: number;
}

export function ChatHeader({ onClearMessages, messageCount = 0 }: ChatHeaderProps) {
  return (
    <header className="flex items-center justify-between border-b border-border bg-card px-6 py-3">
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-semibold text-foreground">BossolutionAI</h1>
      </div>
      <div className="flex items-center gap-3">
        {messageCount > 0 && onClearMessages && (
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <button
                className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive"
                aria-label="Clear all messages"
              >
                <Trash2 className="h-5 w-5" />
              </button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Clear all messages?</AlertDialogTitle>
                <AlertDialogDescription>
                  This will delete all messages in the current conversation and start a new session. This action cannot be undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={onClearMessages} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                  Clear Messages
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        )}
        <button
          className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
          aria-label="Apps"
        >
          <LayoutGrid className="h-5 w-5" />
        </button>
        <button
          className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
          aria-label="Notifications"
        >
          <Bell className="h-5 w-5" />
        </button>
        <UserProfileDropdown />
      </div>
    </header>
  )
}

export function GreetingBanner() {
  return (
    <div className="flex items-center justify-between border-b border-border bg-card px-6 py-4">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
          <svg viewBox="0 0 24 24" className="h-5 w-5 text-primary" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
          </svg>
        </div>
        <div>
          <p className="text-sm font-semibold text-foreground">
            {"Hi, I'm BossolutionAI. How can I help you?"}
          </p>
          <p className="text-xs text-muted-foreground">
            Your AI-powered marketing assistant for content creation, competitor analysis, and campaign optimization!
          </p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <button className="flex items-center gap-1.5 rounded-lg border border-border bg-card px-3 py-1.5 text-xs font-medium text-foreground transition-colors hover:bg-secondary">
          Marketing Manager
          <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />
        </button>
        <button className="flex items-center gap-1.5 rounded-lg border border-border bg-card px-3 py-1.5 text-xs font-medium text-foreground transition-colors hover:bg-secondary">
          <Clock className="h-3.5 w-3.5" />
          History
        </button>
      </div>
    </div>
  )
}
