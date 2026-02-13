import { Sidebar } from "@/components/chat/sidebar"
import { CronJobsSidebar } from "@/components/chat/cron-jobs-sidebar"
import { ProtectedRoute } from "@/components/auth/ProtectedRoute"

export default function CronJobsPage() {
  return (
    <ProtectedRoute>
      <div className="flex h-screen overflow-hidden bg-background">
        <Sidebar />
        <main className="flex flex-1 flex-col overflow-hidden">
          <div className="border-b border-border px-6 py-4">
            <h1 className="text-xl font-semibold text-foreground">Cron Jobs</h1>
            <p className="text-sm text-muted-foreground">
              View, edit, and manage your monitoring schedules.
            </p>
          </div>
          <div className="flex-1 overflow-hidden p-6">
            <CronJobsSidebar variant="page" className="h-full" />
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}