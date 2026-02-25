/**
 * YouTube Data API v3 Utilities
 * 
 * This file contains utility functions for interacting with the YouTube Data API v3
 */

const YOUTUBE_API_BASE_URL = "https://www.googleapis.com/youtube/v3"

export interface YouTubeChannel {
  id: string
  title: string
  description: string
  customUrl?: string
  thumbnails: {
    default: { url: string }
    medium: { url: string }
    high: { url: string }
  }
  statistics?: {
    viewCount: string
    subscriberCount: string
    videoCount: string
  }
}

export interface YouTubeVideo {
  id: string
  title: string
  description: string
  thumbnails: {
    default: { url: string }
    medium: { url: string }
    high: { url: string }
  }
  publishedAt: string
  statistics?: {
    viewCount: string
    likeCount: string
    commentCount: string
  }
}

/**
 * Fetch user's YouTube channel information
 */
export async function getYouTubeChannel(
  accessToken: string
): Promise<YouTubeChannel | null> {
  try {
    const response = await fetch(
      `${YOUTUBE_API_BASE_URL}/channels?part=snippet,statistics&mine=true`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    )

    if (!response.ok) {
      throw new Error("Failed to fetch channel data")
    }

    const data = await response.json()
    const channel = data.items?.[0]

    if (!channel) return null

    return {
      id: channel.id,
      title: channel.snippet.title,
      description: channel.snippet.description,
      customUrl: channel.snippet.customUrl,
      thumbnails: channel.snippet.thumbnails,
      statistics: channel.statistics,
    }
  } catch (error) {
    console.error("Error fetching YouTube channel:", error)
    return null
  }
}

/**
 * Fetch user's uploaded videos
 */
export async function getYouTubeVideos(
  accessToken: string,
  maxResults: number = 10
): Promise<YouTubeVideo[]> {
  try {
    console.log("📹 Fetching YouTube videos...")
    console.log("🔑 Token length:", accessToken?.length || 0)
    
    if (!accessToken) {
      console.error("❌ No access token provided")
      return []
    }
    
    // First, get the uploads playlist ID
    const channelResponse = await fetch(
      `${YOUTUBE_API_BASE_URL}/channels?part=contentDetails&mine=true`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    )

    if (!channelResponse.ok) {
      const errorData = await channelResponse.json().catch(() => ({}))
      
      console.error("❌ YouTube API Error:", channelResponse.status)
      console.error("Error details:", JSON.stringify(errorData, null, 2))
      
      if (channelResponse.status === 403) {
        console.warn("\n⚠️ YouTube API Access Denied (403)")
        console.warn("📋 Setup Required:")
        console.warn("   1. Enable 'YouTube Data API v3' in Google Cloud Console")
        console.warn("   2. Go to: https://console.cloud.google.com/apis/library/youtube.googleapis.com")
        console.warn("   3. Select project: kitahack2026-8feed")
        console.warn("   4. Click 'Enable' button")
        console.warn("   5. Wait 1-2 minutes for propagation")
        console.warn("   6. Reconnect your YouTube account\n")
      } else if (channelResponse.status === 401) {
        console.warn("\n🔑 YouTube Token Invalid or Expired (401)")
        console.warn("📋 Most Common Causes:")
        console.warn("   • Token was issued before API was enabled")
        console.warn("   • Token has expired (usually after 1 hour)")
        console.warn("   • OAuth consent screen not configured correctly")
        console.warn("\n💡 Quick Fix:")
        console.warn("   1. Click 'Disconnect' button")
        console.warn("   2. Wait 2 seconds")
        console.warn("   3. Click 'Connect YouTube' again")
        console.warn("   4. Make sure to GRANT ALL PERMISSIONS")
        console.warn("\n💡 If still failing:")
        console.warn("   1. Go to https://myaccount.google.com/permissions")
        console.warn("   2. Remove 'KitaHack2026' access")
        console.warn("   3. Clear browser cache (Ctrl+Shift+Delete)")
        console.warn("   4. Try connecting again\n")
      } else if (channelResponse.status === 400) {
        console.error("\n❌ Bad Request (400)")
        console.error("The API request was malformed. This is likely a code issue.")
        console.error("Error details:", errorData)
      } else {
        console.error("\n❌ Unexpected Error:", channelResponse.status)
        console.error("Details:", errorData)
      }
      
      return []
    }
    
    console.log("✅ Channel data retrieved successfully")

    const channelData = await channelResponse.json()
    const uploadsPlaylistId =
      channelData.items?.[0]?.contentDetails?.relatedPlaylists?.uploads

    if (!uploadsPlaylistId) {
      console.warn("⚠️ No uploads playlist found")
      console.warn("Possible reasons:")
      console.warn("   • You don't have a YouTube channel yet")
      console.warn("   • Your channel doesn't have any uploaded videos")
      console.warn("   • YouTube account is too new (needs time to activate channel)")
      return []
    }
    
    console.log("📂 Found uploads playlist:", uploadsPlaylistId)

    // Fetch videos from uploads playlist
    const videosResponse = await fetch(
      `${YOUTUBE_API_BASE_URL}/playlistItems?part=snippet&playlistId=${uploadsPlaylistId}&maxResults=${maxResults}`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    )

    if (!videosResponse.ok) {
      const videoError = await videosResponse.json().catch(() => ({}))
      console.error("❌ Failed to fetch videos:", videosResponse.status, videoError)
      return []
    }

    const videosData = await videosResponse.json()
    const videoIds = videosData.items?.map(
      (item: any) => item.snippet.resourceId.videoId
    )

    if (!videoIds || videoIds.length === 0) {
      console.log("ℹ️ No videos found in playlist")
      return []
    }
    
    console.log(`📊 Found ${videoIds.length} video(s)`)

    // Fetch video statistics
    const statsResponse = await fetch(
      `${YOUTUBE_API_BASE_URL}/videos?part=statistics,snippet&id=${videoIds.join(",")}`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    )

    if (!statsResponse.ok) {
      const statsError = await statsResponse.json().catch(() => ({}))
      console.warn("⚠️ Failed to fetch video statistics:", statsResponse.status, statsError)
      console.log("📹 Returning videos without statistics")
      // Return videos without statistics
      return videosData.items?.map((item: any) => ({
        id: item.snippet.resourceId.videoId,
        title: item.snippet.title,
        description: item.snippet.description,
        thumbnails: item.snippet.thumbnails,
        publishedAt: item.snippet.publishedAt,
      })) || []
    }

    const statsData = await statsResponse.json()
    const videos = statsData.items?.map((video: any) => ({
      id: video.id,
      title: video.snippet.title,
      description: video.snippet.description,
      thumbnails: video.snippet.thumbnails,
      publishedAt: video.snippet.publishedAt,
      statistics: video.statistics,
    })) || []
    
    console.log(`✅ Successfully loaded ${videos.length} video(s) with statistics`)
    return videos
  } catch (error) {
    console.error("Error fetching YouTube videos:", error)
    return []
  }
}

/**
 * Search for videos on YouTube
 */
export async function searchYouTubeVideos(
  accessToken: string,
  query: string,
  maxResults: number = 10
): Promise<YouTubeVideo[]> {
  try {
    const response = await fetch(
      `${YOUTUBE_API_BASE_URL}/search?part=snippet&q=${encodeURIComponent(query)}&type=video&maxResults=${maxResults}`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    )

    if (!response.ok) {
      throw new Error("Failed to search videos")
    }

    const data = await response.json()

    return data.items?.map((item: any) => ({
      id: item.id.videoId,
      title: item.snippet.title,
      description: item.snippet.description,
      thumbnails: item.snippet.thumbnails,
      publishedAt: item.snippet.publishedAt,
    })) || []
  } catch (error) {
    console.error("Error searching YouTube videos:", error)
    return []
  }
}
