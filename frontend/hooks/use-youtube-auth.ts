"use client"

import { useState, useEffect } from "react"
import { GoogleAuthProvider, signInWithPopup, OAuthCredential } from "firebase/auth"
import { auth, db } from "@/lib/firebase"
import { doc, setDoc, getDoc } from "firebase/firestore"

interface YouTubeUser {
  name: string
  email: string
  channelId?: string
  accessToken: string
}

export function useYouTubeAuth() {
  const [isConnected, setIsConnected] = useState(false)
  const [user, setUser] = useState<YouTubeUser | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    checkConnection()
  }, [])

  const checkConnection = async () => {
    try {
      const currentUser = auth.currentUser
      if (!currentUser) return

      const userDoc = await getDoc(doc(db, "users", currentUser.uid))
      const userData = userDoc.data()

      if (userData?.youtubeConnection) {
        setIsConnected(true)
        setUser(userData.youtubeConnection)
      }
    } catch (error) {
      console.error("Error checking YouTube connection:", error)
    }
  }

  const login = async () => {
    try {
      setIsLoading(true)
      const currentUser = auth.currentUser

      if (!currentUser) {
        throw new Error("No authenticated user found")
      }

      const provider = new GoogleAuthProvider()
      
      // Request YouTube Data API v3 scopes
      provider.addScope("https://www.googleapis.com/auth/youtube.readonly")
      provider.addScope("https://www.googleapis.com/auth/youtube.force-ssl")
      provider.addScope("https://www.googleapis.com/auth/userinfo.profile")
      provider.addScope("https://www.googleapis.com/auth/userinfo.email")

      // Force account selection
      provider.setCustomParameters({
        prompt: "select_account"
      })

      const result = await signInWithPopup(auth, provider)
      const credential = GoogleAuthProvider.credentialFromResult(result)
      const accessToken = credential?.accessToken

      if (!accessToken) {
        throw new Error("Failed to get access token")
      }

      // Fetch user's YouTube channel info (optional - may not exist)
      let channelId: string | undefined = undefined
      try {
        const channelResponse = await fetch(
          `https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true`,
          {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          }
        )

        if (channelResponse.ok) {
          const channelData = await channelResponse.json()
          channelId = channelData.items?.[0]?.id
        } else {
          console.warn("Could not fetch YouTube channel info:", channelResponse.status)
        }
      } catch (channelError) {
        console.warn("YouTube channel fetch failed (non-critical):", channelError)
        // Continue anyway - user can still be connected without channel info
      }

      const youtubeUser: YouTubeUser = {
        name: result.user.displayName || "Unknown",
        email: result.user.email || "",
        channelId: channelId || undefined,
        accessToken: accessToken,
      }

      // Save connection to Firestore (only save defined values)
      const connectionData: any = {
        name: youtubeUser.name,
        email: youtubeUser.email,
        accessToken: youtubeUser.accessToken,
      }
      
      // Only add channelId if it exists
      if (channelId) {
        connectionData.channelId = channelId
      }

      await setDoc(
        doc(db, "users", currentUser.uid),
        {
          youtubeConnection: connectionData,
          youtubeConnectedAt: new Date().toISOString(),
        },
        { merge: true }
      )

      setIsConnected(true)
      setUser(youtubeUser)
    } catch (error: any) {
      console.error("YouTube authentication error:", error)
      
      // Provide specific error messages
      let errorMessage = "Failed to connect to YouTube. "
      
      if (error.code === "auth/popup-closed-by-user") {
        errorMessage = "Sign-in cancelled. Please try again."
      } else if (error.code === "auth/popup-blocked") {
        errorMessage = "Pop-up was blocked. Please allow pop-ups and try again."
      } else if (error.message?.includes("access token")) {
        errorMessage = "Failed to get access token. Please ensure you granted all permissions."
      } else if (error.message?.includes("No authenticated user")) {
        errorMessage = "Please sign in to your account first."
      } else {
        errorMessage += "Please ensure:\n1. YouTube Data API v3 is enabled\n2. You granted all permissions\n3. You added yourself as a test user"
      }
      
      alert(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      setIsLoading(true)
      const currentUser = auth.currentUser

      if (!currentUser) return

      // Remove connection from Firestore
      await setDoc(
        doc(db, "users", currentUser.uid),
        {
          youtubeConnection: null,
          youtubeConnectedAt: null,
        },
        { merge: true }
      )

      setIsConnected(false)
      setUser(null)
    } catch (error) {
      console.error("Error disconnecting YouTube:", error)
      alert("Failed to disconnect YouTube. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return {
    isConnected,
    user,
    login,
    logout,
    isLoading,
  }
}
