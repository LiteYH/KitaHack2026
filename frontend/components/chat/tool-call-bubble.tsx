/**
 * Tool Call Bubble
 *
 * Displays when the agent invokes a tool (e.g., competitor_monitoring).
 * Shows tool name and collapsible args.
 */

"use client"

import { memo } from "react"
import { Wrench, ChevronDown, ChevronRight } from "lucide-react"

interface ToolCallBubbleProps {
  name: string
  args?: Record<string, any>
  isCollapsed?: boolean
  onToggle?: () => void
}

const ToolCallBubbleComponent = ({
  name,
  args,
  isCollapsed = true,
  onToggle,
}: ToolCallBubbleProps) => {
  const displayName = name.replace(/_/g, " ")

  return (
    <div className="flex items-start gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400">
        <Wrench className="h-4 w-4" />
      </div>
      <div className="max-w-[80%]">
        <button
          onClick={onToggle}
          className="flex items-center gap-1.5 text-xs font-medium text-amber-700 dark:text-amber-400 hover:underline"
        >
          {isCollapsed ? (
            <ChevronRight className="h-3 w-3" />
          ) : (
            <ChevronDown className="h-3 w-3" />
          )}
          <span>🔧 Calling tool: {displayName}</span>
        </button>
        {!isCollapsed && args && Object.keys(args).length > 0 && (
          <pre className="mt-1 rounded-lg border border-amber-200 bg-amber-50 p-2 text-xs text-amber-900 dark:border-amber-800 dark:bg-amber-950/50 dark:text-amber-200 overflow-x-auto max-h-48 overflow-y-auto">
            {JSON.stringify(args, null, 2)}
          </pre>
        )}
      </div>
    </div>
  )
}

export const ToolCallBubble = memo(ToolCallBubbleComponent)
ToolCallBubble.displayName = "ToolCallBubble"
