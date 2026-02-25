"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  Home,
  FolderOpen,
  ClipboardList,
  Bot,
  Bell,
  Settings,
  Clock,
  Search,
  TrendingUp,
  Cable,
  BarChart2,
} from "lucide-react"
import { cn } from "@/lib/utils"

const navItems = [
  { icon: Home, label: "Home", href: "/" },
  { icon: FolderOpen, label: "Projects", href: "/projects" },
  { icon: ClipboardList, label: "Task", href: "/tasks" },
  { icon: Bot, label: "Ask AI", href: "/chat" },
  { icon: TrendingUp, label: "ROI", href: "/roi" },
  { icon: BarChart2, label: "Campaigns", href: "/campaigns" },
  { icon: Cable, label: "Platform", href: "/platform" },
  { icon: Clock, label: "Cron Jobs", href: "/cron-jobs" },
  { icon: Bell, label: "Notification", href: "/notifications" },
  { icon: Settings, label: "Settings", href: "/settings" },
  { icon: Search, label: "Search", href: "/search" },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="flex h-screen w-20 flex-col items-center border-r border-border bg-card py-5">
      {/* Logo */}
      <div className="mb-6 flex h-10 w-10 items-center justify-center">
        <svg viewBox="0 0 40 40" fill="none" className="h-9 w-9">
          <rect width="40" height="40" rx="8" fill="hsl(217 91% 55%)" />
          <path
            d="M12 14C12 12.8954 12.8954 12 14 12H20C23.3137 12 26 14.6863 26 18C26 21.3137 23.3137 24 20 24H18V28H14V16H12V14ZM18 20H20C21.1046 20 22 19.1046 22 18C22 16.8954 21.1046 16 20 16H18V20Z"
            fill="white"
          />
        </svg>
      </div>

      {/* Nav items */}
      <nav className="flex flex-1 flex-col items-center gap-1">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = item.href !== "/" ? pathname.startsWith(item.href) : pathname === "/"
          return (
            <Link
              key={item.label}
              href={item.href}
              className={cn(
                "group flex w-16 flex-col items-center gap-1 rounded-lg px-2 py-2.5 text-[10px] font-medium transition-colors",
                isActive
                  ? "text-primary"
                  : "text-muted-foreground hover:text-foreground"
              )}
              aria-label={item.label}
              aria-current={isActive ? "page" : undefined}
            >
              <Icon
                className={cn(
                  "h-5 w-5",
                  isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground"
                )}
                strokeWidth={isActive ? 2.5 : 1.75}
              />
              <span className="text-center leading-tight">{item.label}</span>
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
