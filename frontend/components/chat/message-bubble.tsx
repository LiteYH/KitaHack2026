"use client"

import { useMemo, memo, useState } from "react"
import { Bot, User, FileText, Download } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import type { Components } from "react-markdown"
import { parseGenUI, renderGenUIComponent } from "@/components/genui/GenUIRenderer"
import { ROIChart, type ChartConfig } from "./roi-chart"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/contexts/AuthContext"
import { downloadPDFReport } from "@/lib/api/report"
import { useToast } from "@/hooks/use-toast"
import { CampaignAnalyticsCard } from "./campaign-analytics-card"
import { CampaignVisualization } from "./campaign-visualization"
import type { CampaignDataAttachment } from "@/lib/api/chat"

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  charts?: ChartConfig[]
  filterContext?: {
    days?: number
    userEmail?: string
  }
  campaignData?: CampaignDataAttachment
}

interface MessageBubbleProps {
  message: Message
}

// Move markdown components outside component to prevent recreation on every render
// This is a CRITICAL performance optimization
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

// Wrap component in React.memo to prevent re-renders when props don't change
// This prevents ALL messages from re-rendering on every keystroke
const MessageBubbleComponent = ({ message }: MessageBubbleProps) => {
  const isUser = message.role === "user"
  const { user } = useAuth()
  const { toast } = useToast()
  const [isDownloading, setIsDownloading] = useState(false)

  // Extract embedded ROI charts block from content, if present
  const { displayContent, roiCharts, roiFilterContext } = useMemo(() => {
    if (isUser) return { displayContent: message.content, roiCharts: undefined, roiFilterContext: undefined }
    const raw = message.content || ''
    const start = raw.indexOf('<roi-charts>')
    const end = raw.indexOf('</roi-charts>')
    if (start !== -1 && end !== -1) {
      try {
        const payload = JSON.parse(raw.slice(start + 12, end))
        const cleaned = raw.slice(0, start).trimEnd()
        return {
          displayContent: cleaned,
          roiCharts: payload.charts as ChartConfig[],
          roiFilterContext: payload.filter_context as { days?: number; userEmail?: string },
        }
      } catch {
        return { displayContent: raw, roiCharts: undefined, roiFilterContext: undefined }
      }
    }
    return { displayContent: raw, roiCharts: undefined, roiFilterContext: undefined }
  }, [isUser, message.content])

  // Merge with any charts already set on the message prop
  const activeCharts = roiCharts ?? message.charts
  const activeFilterContext = roiFilterContext ?? message.filterContext

  // Check if this message contains ROI analysis (has charts)
  const hasROIAnalysis = !isUser && !!activeCharts && activeCharts.length > 0

  // Parse GenUI for assistant messages - handle undefined/null content gracefully
  // Memoize to prevent re-parsing on every render (performance optimization)
  const segments = useMemo(
    () => !isUser ? parseGenUI(displayContent) : null,
    [isUser, displayContent]
  )

  const handleDownloadReport = async () => {
    try {
      setIsDownloading(true)
      
      // Get user email for filtering ROI data
      const userEmail = user?.email
      
      if (!userEmail) {
        toast({
          title: "Authentication Required",
          description: "Please sign in to download your ROI report.",
          variant: "destructive",
        })
        return
      }

      // Get filter context from message (days filter from chat query)
      const days = activeFilterContext?.days

      // Download the PDF report with the same filters used in the chat
      await downloadPDFReport(userEmail, days)
      
      toast({
        title: "Report Downloaded",
        description: days 
          ? `Your ROI report for the last ${days} days has been downloaded.`
          : "Your ROI report has been downloaded successfully.",
      })
    } catch (error) {
      console.error("Error downloading report:", error)
      toast({
        title: "Download Failed",
        description: error instanceof Error ? error.message : "Failed to download report. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsDownloading(false)
    }
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
          <div className="space-y-4">
            {segments?.map((segment, index) => {
              const uniqueKey = `${message.id}-${segment.type}-${index}-${segment.content?.slice(0, 10) || segment.data?.type || ''}`;
              
              if (segment.type === 'text') {
                return (
                  <div key={uniqueKey} className="prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={markdownComponents}
                    >
                      {segment.content}
                    </ReactMarkdown>
                  </div>
                )
              } else if (segment.type === 'genui' && segment.data) {
                return (
                  <div key={uniqueKey} className="my-4">
                    {renderGenUIComponent(segment.data)}
                  </div>
                )
              }
              return null
            })}

            {/* Render ROI charts if present */}
            {activeCharts && activeCharts.length > 0 && (
              <div className="mt-4 space-y-4">
                {activeCharts.map((chart, index) => (
                  <ROIChart key={index} config={chart} />
                ))}
              </div>
            )}

            {/* Render campaign analytics card if present */}
            {message.campaignData && (
              <>
                <CampaignAnalyticsCard
                  campaigns={message.campaignData.campaigns}
                  metrics={message.campaignData.metrics}
                  summary={message.campaignData.summary}
                  type={message.campaignData.type}
                />
                {message.campaignData.show_visualization && (
                  <div className="mt-3">
                    <CampaignVisualization
                      campaigns={message.campaignData.campaigns}
                    />
                  </div>
                )}
              </>
            )}

            {/* Create Report button for ROI analysis messages */}
            {hasROIAnalysis && (
              <div className="mt-4 pt-4 border-t border-border">
                <Button
                  onClick={handleDownloadReport}
                  disabled={isDownloading}
                  className="w-full sm:w-auto"
                  variant="default"
                >
                  {isDownloading ? (
                    <>
                      <Download className="mr-2 h-4 w-4 animate-pulse" />
                      Generating Report...
                    </>
                  ) : (
                    <>
                      <FileText className="mr-2 h-4 w-4" />
                      Create Report
                    </>
                  )}
                </Button>
                <p className="text-xs text-muted-foreground mt-2">
                  Generate a comprehensive PDF report with AI-powered insights
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// Custom comparison function - only re-render if message content actually changed
const arePropsEqual = (prevProps: MessageBubbleProps, nextProps: MessageBubbleProps) => {
  return (
    prevProps.message.id === nextProps.message.id &&
    prevProps.message.content === nextProps.message.content &&
    prevProps.message.role === nextProps.message.role &&
    prevProps.message.charts === nextProps.message.charts
  )
}

// Export memoized component
export const MessageBubble = memo(MessageBubbleComponent, arePropsEqual)
MessageBubble.displayName = 'MessageBubble'
