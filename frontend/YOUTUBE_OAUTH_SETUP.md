# YouTube OAuth Setup Guide

This guide explains how to set up YouTube Data API v3 authentication for the Platform page.

## Prerequisites

1. A Google Cloud Console account
2. Firebase project already configured (already done in this project)

## Setup Steps

### 1. Enable YouTube Data API v3

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your Firebase project (kitahack2026-8feed)
3. Navigate to **APIs & Services** > **Library**
4. Search for "YouTube Data API v3"
5. Click on it and press **Enable**

### 2. Configure OAuth Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen**
2. If not already configured:
   - Choose **External** user type
   - Fill in required fields:
     - App name: "KitaHack2026"
     - User support email: Your email
     - Developer contact email: Your email
3. Add the following scopes:
   - `https://www.googleapis.com/auth/youtube.readonly`
   - `https://www.googleapis.com/auth/youtube.force-ssl`
   - `https://www.googleapis.com/auth/userinfo.profile`
   - `https://www.googleapis.com/auth/userinfo.email`
4. Add test users if your app is in testing mode

### 3. Verify Firebase OAuth Configuration

Your Firebase project should already have OAuth credentials configured. Verify that:

1. Go to **APIs & Services** > **Credentials**
2. Look for an OAuth 2.0 Client ID for Web application
3. Ensure the following are in **Authorized JavaScript origins**:
   - `http://localhost:3000`
   - `http://localhost:5173`
   - Your production domain (if deployed)
4. Ensure the following are in **Authorized redirect URIs**:
   - `http://localhost:3000/__/auth/handler`
   - `http://localhost:5173/__/auth/handler`
   - Your Firebase Auth domain: `https://kitahack2026-8feed.firebaseapp.com/__/auth/handler`

### 4. No Additional Environment Variables Needed

The YouTube authentication uses Firebase's existing OAuth configuration, so you don't need to add any new environment variables. It will use the existing Firebase credentials.

## How It Works

### Authentication Flow

1. User clicks "Connect YouTube" button on the Platform page
2. The app triggers Google OAuth with YouTube scopes
3. User is redirected to Google's consent screen
4. After approval, the app receives an access token
5. The access token is used to fetch YouTube channel information
6. Connection details are saved to Firestore

### Data Stored

When a user connects their YouTube account, the following data is stored in Firestore under `users/{userId}`:

```typescript
{
  youtubeConnection: {
    name: string,          // User's display name
    email: string,         // User's email
    channelId: string,     // YouTube channel ID
    accessToken: string    // OAuth access token
  },
  youtubeConnectedAt: string  // ISO timestamp
}
```

## Using the YouTube API

### In Components

```typescript
import { useYouTubeAuth } from "@/hooks/use-youtube-auth"

function MyComponent() {
  const { isConnected, user, login, logout, isLoading } = useYouTubeAuth()
  
  // user.accessToken can be used to call YouTube API
}
```

### API Utilities

```typescript
import { getYouTubeChannel, getYouTubeVideos } from "@/lib/api/youtube"

// Fetch channel info
const channel = await getYouTubeChannel(accessToken)

// Fetch user's videos
const videos = await getYouTubeVideos(accessToken, maxResults)
```

## Security Notes

1. **Access Token Storage**: Currently stored in Firestore. For production:
   - Consider encrypting tokens
   - Implement token refresh mechanism
   - Add expiration handling

2. **Token Scope**: Tokens have the following scopes:
   - `youtube.readonly`: Read-only access to YouTube data
   - `youtube.force-ssl`: Manage YouTube account (required for some operations)
   - `userinfo.profile` & `userinfo.email`: Basic profile information

3. **Firestore Rules**: Ensure your Firestore security rules protect user data:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

## Testing

1. Navigate to `/platform` page (after authenticating with Firebase)
2. Click "Connect YouTube" button
3. Select your Google account
4. Grant permissions
5. You should see your account details and a "Disconnect" button

## Troubleshooting

### "Access blocked: Authorization Error"
- Ensure YouTube Data API v3 is enabled in Google Cloud Console
- Check that OAuth consent screen is properly configured
- Add your email as a test user if app is in testing mode

### "Failed to get access token"
- Verify Firebase configuration in `lib/firebase.ts`
- Check browser console for detailed error messages
- Ensure redirect URIs are correctly configured

### "No authenticated user found"
- User must be logged in to Firebase before connecting YouTube
- Check Firebase authentication state

## Future Enhancements

- [ ] Implement token refresh mechanism
- [ ] Add YouTube analytics dashboard
- [ ] Implement video upload functionality
- [ ] Add comment management features
- [ ] Implement playlist management
