/**
 * Agent Status Bubble
 *
 * Inline indicator showing which graph node is currently executing.
 * Rendered as a compact, non-intrusive status line.
 */

"use client"

import { memo } from "react"
import { Activity } from "lucide-react"

interface AgentStatusBubbleProps {
  node: string
}

const AgentStatusBubbleComponent = ({ node }: AgentStatusBubbleProps) => {
  const displayName = node.replace(/_/g, " ")

  return (
    <div className="flex items-center justify-center gap-2 py-1">
      <div className="h-px flex-1 bg-border" />
      <div className="flex items-center gap-1.5 rounded-full border border-border bg-muted/50 px-3 py-1">
        <Activity className="h-3 w-3 text-blue-500 animate-pulse" />
        <span className="text-[10px] font-medium text-muted-foreground">
          {displayName}
        </span>
      </div>
      <div className="h-px flex-1 bg-border" />
    </div>
  )
}

export const AgentStatusBubble = memo(AgentStatusBubbleComponent)
AgentStatusBubble.displayName = "AgentStatusBubble"
