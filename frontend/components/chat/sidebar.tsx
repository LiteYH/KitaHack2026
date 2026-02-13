"use client"

import {
  Home,
  FolderOpen,
  ClipboardList,
  Bot,
  Bell,
  Settings,
  Search,
} from "lucide-react"
import { cn } from "@/lib/utils"

const navItems = [
  { icon: Home, label: "Home" },
  { icon: FolderOpen, label: "Projects" },
  { icon: ClipboardList, label: "Task" },
  { icon: Bot, label: "Ask AI", active: true },
  { icon: Bell, label: "Notification" },
  { icon: Settings, label: "Settings" },
  { icon: Search, label: "Search" },
]

export function Sidebar() {
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
          return (
            <button
              key={item.label}
              className={cn(
                "group flex w-16 flex-col items-center gap-1 rounded-lg px-2 py-2.5 text-[10px] font-medium transition-colors",
                item.active
                  ? "text-primary"
                  : "text-muted-foreground hover:text-foreground"
              )}
              aria-label={item.label}
              aria-current={item.active ? "page" : undefined}
            >
              <Icon
                className={cn(
                  "h-5 w-5",
                  item.active ? "text-primary" : "text-muted-foreground group-hover:text-foreground"
                )}
                strokeWidth={item.active ? 2.5 : 1.75}
              />
              <span>{item.label}</span>
            </button>
          )
        })}
      </nav>
    </aside>
  )
}
