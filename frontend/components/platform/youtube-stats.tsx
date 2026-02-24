"use client"

import { useState, useEffect } from "react"
import { useYouTubeAuth } from "@/hooks/use-youtube-auth"
import { getYouTubeChannel, getYouTubeVideos, YouTubeChannel, YouTubeVideo } from "@/lib/api/youtube"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Play, Eye, ThumbsUp, MessageSquare } from "lucide-react"

/**
 * Example component showing how to use YouTube API utilities
 * This can be used as a reference for building YouTube features
 */
export function YouTubeChannelStats() {
  const { isConnected, user } = useYouTubeAuth()
  const [channel, setChannel] = useState<YouTubeChannel | null>(null)
  const [videos, setVideos] = useState<YouTubeVideo[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isConnected && user?.accessToken) {
      loadChannelData()
    }
  }, [isConnected, user])

  const loadChannelData = async () => {
    if (!user?.accessToken) return

    setLoading(true)
    try {
      const [channelData, videosData] = await Promise.all([
        getYouTubeChannel(user.accessToken),
        getYouTubeVideos(user.accessToken, 5)
      ])

      setChannel(channelData)
      setVideos(videosData)
    } catch (error) {
      console.error("Error loading YouTube data:", error)
    } finally {
      setLoading(false)
    }
  }

  if (!isConnected) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>YouTube Analytics</CardTitle>
          <CardDescription>Connect your YouTube account to see analytics</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-64 mt-2" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-24 w-full" />
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Channel Stats */}
      {channel && (
        <Card>
          <CardHeader>
            <CardTitle>Channel Statistics</CardTitle>
            <CardDescription>{channel.title}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">Subscribers</p>
                <p className="text-2xl font-bold">
                  {parseInt(channel.statistics?.subscriberCount || "0").toLocaleString()}
                </p>
              </div>
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">Total Views</p>
                <p className="text-2xl font-bold">
                  {parseInt(channel.statistics?.viewCount || "0").toLocaleString()}
                </p>
              </div>
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">Videos</p>
                <p className="text-2xl font-bold">
                  {parseInt(channel.statistics?.videoCount || "0").toLocaleString()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Videos */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Videos</CardTitle>
          <CardDescription>Your latest uploads</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {videos.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-8">
                No videos found
              </p>
            ) : (
              videos.map((video) => (
                <div
                  key={video.id}
                  className="flex gap-4 p-3 rounded-lg border hover:bg-muted/50 transition-colors"
                >
                  <img
                    src={video.thumbnails.medium.url}
                    alt={video.title}
                    className="w-40 h-24 object-cover rounded"
                  />
                  <div className="flex-1 space-y-2">
                    <h4 className="font-semibold line-clamp-2">{video.title}</h4>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Eye className="h-4 w-4" />
                        <span>{parseInt(video.statistics?.viewCount || "0").toLocaleString()}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <ThumbsUp className="h-4 w-4" />
                        <span>{parseInt(video.statistics?.likeCount || "0").toLocaleString()}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <MessageSquare className="h-4 w-4" />
                        <span>{parseInt(video.statistics?.commentCount || "0").toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
          {videos.length > 0 && (
            <Button variant="outline" className="w-full mt-4" onClick={loadChannelData}>
              Refresh Data
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
