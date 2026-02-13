import { Sidebar } from "@/components/chat/sidebar"
import { ChatHeader, GreetingBanner } from "@/components/chat/chat-header"
import { AgentChatArea } from "@/components/chat/agent-chat-area"
import { ProtectedRoute } from "@/components/auth/ProtectedRoute"

export default function ChatPage() {
  return (
    <ProtectedRoute>
      <div className="flex h-screen overflow-hidden bg-background">
        <Sidebar />
        <main className="flex flex-1 overflow-hidden">
          <section className="flex flex-1 flex-col overflow-hidden">
            <ChatHeader />
            <GreetingBanner />
            <AgentChatArea />
          </section>
        </main>
      </div>
    </ProtectedRoute>
  )
}
