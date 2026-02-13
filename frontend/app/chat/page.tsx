import { Sidebar } from "@/components/chat/sidebar"
import { ChatHeader, GreetingBanner } from "@/components/chat/chat-header"
import { ChatArea } from "@/components/chat/chat-area"

export default function ChatPage() {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <main className="flex flex-1 flex-col overflow-hidden">
        <ChatHeader />
        <GreetingBanner />
        <ChatArea />
      </main>
    </div>
  )
}
