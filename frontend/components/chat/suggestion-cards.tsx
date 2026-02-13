"use client"

import {
  FileText,
  Search,
  Send,
  Target,
  BarChart3,
  Eye,
} from "lucide-react"
import type { LucideIcon } from "lucide-react"

interface Suggestion {
  icon: LucideIcon
  iconColor: string
  title: string
  description: string
}

const suggestions: Suggestion[] = [
  {
    icon: FileText,
    title: "Content Planning",
    description: "Generate marketing content for my social media campaign",
    iconColor: "text-blue-500",
  },
  {
    icon: Search,
    title: "Competitor Intelligence",
    description: "Analyze my competitors' marketing strategies",
    iconColor: "text-purple-500",
  },
  {
    icon: Send,
    title: "Publishing",
    description: "Schedule and publish my content automatically",
    iconColor: "text-green-500",
  },
  {
    icon: Target,
    title: "Campaign & Optimization",
    description: "How can I optimize my current campaigns?",
    iconColor: "text-orange-500",
  },
  {
    icon: BarChart3,
    title: "ROI Dashboard",
    description: "Show me my ROI dashboard and campaign performance",
    iconColor: "text-indigo-500",
  },
  {
    icon: Eye,
    title: "Continuous Monitoring",
    description: "Monitor competitors and suggest response strategies",
    iconColor: "text-rose-500",
  },
]

interface SuggestionCardsProps {
  onSelect: (text: string) => void
}

export function SuggestionCards({ onSelect }: SuggestionCardsProps) {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {suggestions.map((item) => {
        const Icon = item.icon
        return (
          <button
            key={item.title}
            onClick={() => onSelect(item.description)}
            className="group flex items-start gap-3 rounded-xl border border-border bg-card p-4 text-left transition-all hover:border-primary/30 hover:shadow-sm"
          >
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-secondary">
              <Icon className={`h-4 w-4 ${item.iconColor}`} />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-foreground">{item.title}</p>
              <p className="mt-0.5 text-xs leading-relaxed text-muted-foreground line-clamp-2">
                {item.description}
              </p>
            </div>
          </button>
        )
      })}
    </div>
  )
}
