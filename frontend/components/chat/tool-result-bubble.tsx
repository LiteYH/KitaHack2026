/**
 * Tool Result Bubble
 *
 * Displays the result returned from a tool execution.
 * Content is collapsible since tool results can be large.
 */

"use client"

import { memo, useMemo } from "react"
import { CheckCircle2, ChevronDown, ChevronRight } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { parseGenUI, renderGenUIComponent } from "@/components/genui/GenUIRenderer"

interface ToolResultBubbleProps {
  name: string
  content: string
  isCollapsed?: boolean
  onToggle?: () => void
}

const ToolResultBubbleComponent = ({
  name,
  content,
  isCollapsed = true,
  onToggle,
}: ToolResultBubbleProps) => {
  const displayName = name.replace(/_/g, " ")
  const truncated = content.length > 200
  const preview = truncated ? content.slice(0, 200) + "…" : content

  // Parse for GenUI components in the result
  const segments = useMemo(() => parseGenUI(content), [content])
  const hasGenUI = segments.some((s) => s.type === "genui")

  return (
    <div className="flex items-start gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
        <CheckCircle2 className="h-4 w-4" />
      </div>
      <div className="max-w-[80%]">
        <button
          onClick={onToggle}
          className="flex items-center gap-1.5 text-xs font-medium text-emerald-700 dark:text-emerald-400 hover:underline"
        >
          {isCollapsed ? (
            <ChevronRight className="h-3 w-3" />
          ) : (
            <ChevronDown className="h-3 w-3" />
          )}
          <span>✅ Result from: {displayName}</span>
        </button>
        {!isCollapsed && (
          <div className="mt-1 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-xs dark:border-emerald-800 dark:bg-emerald-950/50 overflow-x-auto max-h-72 overflow-y-auto">
            {hasGenUI ? (
              <div className="space-y-3">
                {segments.map((segment, i) => {
                  if (segment.type === "text" && segment.content) {
                    return (
                      <div
                        key={`${i}-text`}
                        className="prose prose-xs dark:prose-invert max-w-none text-emerald-900 dark:text-emerald-200"
                      >
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {segment.content}
                        </ReactMarkdown>
                      </div>
                    )
                  } else if (segment.type === "genui" && segment.data) {
                    return (
                      <div key={`${i}-genui`} className="my-2">
                        {renderGenUIComponent(segment.data)}
                      </div>
                    )
                  }
                  return null
                })}
              </div>
            ) : (
              <div className="prose prose-xs dark:prose-invert max-w-none text-emerald-900 dark:text-emerald-200 whitespace-pre-wrap">
                {content}
              </div>
            )}
          </div>
        )}
        {isCollapsed && truncated && (
          <p className="mt-1 text-[10px] text-muted-foreground italic">
            {preview}
          </p>
        )}
      </div>
    </div>
  )
}

export const ToolResultBubble = memo(ToolResultBubbleComponent)
ToolResultBubble.displayName = "ToolResultBubble"
