"use client"

import { Bot, User, FileText, Download } from "lucide-react"
import { useState } from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import type { Components } from "react-markdown"
import { ROIChart, type ChartConfig } from "./roi-chart"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/contexts/AuthContext"
import { downloadPDFReport } from "@/lib/api/report"
import { useToast } from "@/hooks/use-toast"

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  charts?: ChartConfig[]
}

interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user"
  const { user } = useAuth()
  const { toast } = useToast()
  const [isDownloading, setIsDownloading] = useState(false)

  // Check if this message contains ROI analysis (has charts)
  const hasROIAnalysis = !isUser && message.charts && message.charts.length > 0

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

      // Download the PDF report
      await downloadPDFReport(userEmail)
      
      toast({
        title: "Report Downloaded",
        description: "Your ROI report has been downloaded successfully.",
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
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={markdownComponents}
            >
              {message.content}
            </ReactMarkdown>
            
            {/* Render charts if present */}
            {message.charts && message.charts.length > 0 && (
              <div className="mt-4 space-y-4">
                {message.charts.map((chart, index) => (
                  <ROIChart key={index} config={chart} />
                ))}
              </div>
            )}
            
            {/* Create Report Button for ROI Analysis */}
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
