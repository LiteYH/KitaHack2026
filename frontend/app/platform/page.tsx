"use client"

import { Sidebar } from "@/components/chat/sidebar"
import { ProtectedRoute } from "@/components/auth/ProtectedRoute"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Youtube, Facebook, Instagram, Eye, ThumbsUp, MessageSquare, Clock } from "lucide-react"
import { useYouTubeAuth } from "@/hooks/use-youtube-auth"
import { Badge } from "@/components/ui/badge"
import { useState, useEffect } from "react"
import { getYouTubeVideos, YouTubeVideo } from "@/lib/api/youtube"
import { Skeleton } from "@/components/ui/skeleton"

export default function PlatformPage() {
  const { isConnected, user, login, logout, isLoading } = useYouTubeAuth()
  const [videos, setVideos] = useState<YouTubeVideo[]>([])
  const [loadingVideos, setLoadingVideos] = useState(false)

  useEffect(() => {
    if (isConnected && user?.accessToken) {
      loadVideos()
    } else {
      setVideos([])
    }
  }, [isConnected, user])

  const loadVideos = async () => {
    if (!user?.accessToken) {
      console.error("❌ Cannot load videos: No access token available")
      return
    }

    console.log("🔄 Loading videos...")
    console.log("👤 User email:", user.email)
    console.log("🔑 Has access token:", !!user.accessToken)
    console.log("📺 Channel ID:", user.channelId || "Not set")

    setLoadingVideos(true)
    try {
      const data = await getYouTubeVideos(user.accessToken, 10)
      setVideos(data)
      
      if (data.length === 0) {
        console.warn("⚠️ No videos loaded - Check the troubleshooting guide below")
      } else {
        console.log(`✅ Loaded ${data.length} video(s)`)
      }
    } catch (error) {
      console.error("❌ Error loading videos:", error)
    } finally {
      setLoadingVideos(false)
    }
  }

  const formatNumber = (num: string | undefined) => {
    if (!num) return "0"
    return parseInt(num).toLocaleString()
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now.getTime() - date.getTime())
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) return "Today"
    if (diffDays === 1) return "Yesterday"
    if (diffDays < 7) return `${diffDays} days ago`
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`
    return `${Math.floor(diffDays / 365)} years ago`
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen overflow-hidden bg-background">
        <Sidebar />
        <main className="flex flex-1 flex-col overflow-auto p-8">
          <div className="mx-auto w-full max-w-7xl space-y-8">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Platform Connections</h1>
              <p className="text-muted-foreground mt-2">
                Connect your social media accounts to analyze and manage your content
              </p>
            </div>

            {/* Horizontal Platform Widgets */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* YouTube Widget */}
              <Card className={`relative cursor-pointer transition-all hover:shadow-lg ${isConnected ? 'border-green-500' : ''}`}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10">
                      <Youtube className="h-5 w-5 text-red-500" />
                    </div>
                    {isConnected && (
                      <Badge variant="default" className="bg-green-500 text-xs">
                        Connected
                      </Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <h3 className="font-semibold text-sm">YouTube</h3>
                    {isConnected && user ? (
                      <p className="text-xs text-muted-foreground truncate">{user.name}</p>
                    ) : (
                      <p className="text-xs text-muted-foreground">Not connected</p>
                    )}
                  </div>
                  {isConnected && user ? (
                    <Button 
                      onClick={logout} 
                      variant="outline" 
                      size="sm"
                      className="w-full text-xs"
                      disabled={isLoading}
                    >
                      Disconnect
                    </Button>
                  ) : (
                    <Button 
                      onClick={login} 
                      size="sm"
                      className="w-full bg-red-500 hover:bg-red-600 text-xs"
                      disabled={isLoading}
                    >
                      {isLoading ? "Connecting..." : "Connect"}
                    </Button>
                  )}
                </CardContent>
              </Card>

              {/* Facebook Widget */}
              <Card className="relative opacity-60">
                <CardHeader className="pb-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-500/10">
                    <Facebook className="h-5 w-5 text-blue-500" />
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <h3 className="font-semibold text-sm">Facebook</h3>
                    <p className="text-xs text-muted-foreground">Not connected</p>
                  </div>
                  <Button 
                    size="sm"
                    className="w-full bg-blue-500 hover:bg-blue-600 text-xs"
                    disabled
                  >
                    Coming Soon
                  </Button>
                </CardContent>
              </Card>

              {/* Instagram Widget */}
              <Card className="relative opacity-60">
                <CardHeader className="pb-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-purple-500 to-pink-500/10">
                    <Instagram className="h-5 w-5 text-pink-500" />
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <h3 className="font-semibold text-sm">Instagram</h3>
                    <p className="text-xs text-muted-foreground">Not connected</p>
                  </div>
                  <Button 
                    size="sm"
                    className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-xs"
                    disabled
                  >
                    Coming Soon
                  </Button>
                </CardContent>
              </Card>

              {/* TikTok Widget */}
              <Card className="relative opacity-60">
                <CardHeader className="pb-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-900/10">
                    <svg 
                      className="h-5 w-5" 
                      viewBox="0 0 24 24" 
                      fill="currentColor"
                    >
                      <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z"/>
                    </svg>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <h3 className="font-semibold text-sm">TikTok</h3>
                    <p className="text-xs text-muted-foreground">Not connected</p>
                  </div>
                  <Button 
                    size="sm"
                    className="w-full bg-slate-900 hover:bg-slate-800 text-xs"
                    disabled
                  >
                    Coming Soon
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* YouTube Videos Section */}
            {isConnected && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold">Your YouTube Videos</h2>
                    <p className="text-sm text-muted-foreground mt-1">
                      Latest uploads from your channel
                    </p>
                  </div>
                  <Button 
                    onClick={loadVideos} 
                    variant="outline"
                    disabled={loadingVideos}
                    size="sm"
                  >
                    {loadingVideos ? "Loading..." : "Refresh"}
                  </Button>
                </div>

                {loadingVideos ? (
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {[...Array(6)].map((_, i) => (
                      <Card key={i} className="overflow-hidden">
                        <Skeleton className="h-48 w-full" />
                        <CardContent className="p-4 space-y-2">
                          <Skeleton className="h-4 w-3/4" />
                          <Skeleton className="h-3 w-1/2" />
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : videos.length > 0 ? (
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {videos.map((video) => (
                      <Card key={video.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                        <div className="relative group">
                          <img
                            src={video.thumbnails.high.url}
                            alt={video.title}
                            className="w-full h-48 object-cover"
                          />
                          <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                            <a
                              href={`https://www.youtube.com/watch?v=${video.id}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-white hover:text-red-500 transition-colors"
                            >
                              <Youtube className="h-12 w-12" />
                            </a>
                          </div>
                        </div>
                        <CardContent className="p-4 space-y-3">
                          <div>
                            <h3 className="font-semibold line-clamp-2 text-sm leading-tight">
                              {video.title}
                            </h3>
                            <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
                              <Clock className="h-3 w-3" />
                              <span>{formatDate(video.publishedAt)}</span>
                            </div>
                          </div>
                          
                          {video.statistics && (
                            <div className="flex items-center gap-4 text-xs text-muted-foreground pt-2 border-t">
                              <div className="flex items-center gap-1">
                                <Eye className="h-3 w-3" />
                                <span>{formatNumber(video.statistics.viewCount)}</span>
                              </div>
                              <div className="flex items-center gap-1">
                                <ThumbsUp className="h-3 w-3" />
                                <span>{formatNumber(video.statistics.likeCount)}</span>
                              </div>
                              <div className="flex items-center gap-1">
                                <MessageSquare className="h-3 w-3" />
                                <span>{formatNumber(video.statistics.commentCount)}</span>
                              </div>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <Card className="p-12">
                    <div className="text-center space-y-4">
                      <div className="flex justify-center">
                        <div className="h-16 w-16 rounded-full bg-muted flex items-center justify-center">
                          <Youtube className="h-8 w-8 text-muted-foreground" />
                        </div>
                      </div>
                      <div>
                        <h3 className="font-semibold">No Videos Found</h3>
                        <p className="text-sm text-muted-foreground mt-1">
                          This could mean you haven't uploaded any videos yet,<br />
                          or the YouTube Data API v3 needs to be enabled.
                        </p>
                      </div>
                      <div className="bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 max-w-2xl mx-auto text-left">
                        <p className="text-sm font-semibold mb-3 text-amber-900 dark:text-amber-100">🔧 Troubleshooting</p>
                        <div className="space-y-3 text-xs text-amber-800 dark:text-amber-200">
                          <div className="bg-white dark:bg-amber-900/30 border border-amber-300 dark:border-amber-700 rounded p-2">
                            <p className="font-semibold mb-2 text-amber-900 dark:text-amber-100">⚡ Quick Fix (Token Issue):</p>
                            <ol className="space-y-1 list-decimal list-inside ml-2">
                              <li>Click <strong>"Disconnect"</strong> button above</li>
                              <li>Wait 2 seconds</li>
                              <li>Click <strong>"Connect YouTube"</strong> again</li>
                              <li>Grant all permissions when prompted</li>
                            </ol>
                          </div>
                          
                          <p className="font-semibold pt-1">If still not working:</p>
                          
                          <div>
                            <p className="font-semibold mb-1">Step 1: Enable YouTube Data API v3</p>
                            <ol className="space-y-1 list-decimal list-inside ml-2">
                              <li>Go to <a href="https://console.cloud.google.com/apis/library/youtube.googleapis.com" target="_blank" rel="noopener noreferrer" className="underline hover:text-amber-600">Google Cloud Console</a></li>
                              <li>Select project: <code className="bg-amber-100 dark:bg-amber-900 px-1 rounded">kitahack2026-8feed</code></li>
                              <li>Click <strong>"Enable"</strong> button</li>
                            </ol>
                          </div>
                          <div>
                            <p className="font-semibold mb-1">Step 2: Add Test User</p>
                            <ol className="space-y-1 list-decimal list-inside ml-2">
                              <li>Go to <a href="https://console.cloud.google.com/apis/credentials/consent" target="_blank" rel="noopener noreferrer" className="underline hover:text-amber-600">OAuth Consent Screen</a></li>
                              <li>Under <strong>Test users</strong>, add your email</li>
                              <li>Click <strong>"Save"</strong></li>
                            </ol>
                          </div>
                          <div>
                            <p className="font-semibold mb-1">Step 3: Revoke & Reconnect</p>
                            <ol className="space-y-1 list-decimal list-inside ml-2">
                              <li>Go to <a href="https://myaccount.google.com/permissions" target="_blank" rel="noopener noreferrer" className="underline hover:text-amber-600">Google Account Permissions</a></li>
                              <li>Find "KitaHack2026" and click "Remove access"</li>
                              <li>Come back and reconnect YouTube above</li>
                            </ol>
                          </div>
                        </div>
                      </div>
                    </div>
                  </Card>
                )}
              </div>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
