# Firebase Setup Guide for BossolutionAI

This guide will help you complete the Firebase Authentication and Firestore Database setup.

## ✅ What's Already Done

1. ✅ Firebase dependencies installed (frontend & backend)
2. ✅ Firebase configuration files created
3. ✅ Authentication pages (Sign In / Sign Up) created
4. ✅ Protected routes implemented
5. ✅ "Get Started" button redirects to `/auth/signin`
6. ✅ Backend Firebase Admin SDK configured

## 🔧 What You Need to Do

### 1. Enable Firebase Authentication

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **kitahack2026-8feed**
3. In the left sidebar, click **Build** → **Authentication**
4. Click **Get Started** (if first time)
5. Go to **Sign-in method** tab
6. Enable these providers:
   - **Email/Password** ✅
   - **Google** ✅

### 2. Create Firestore Database

1. In Firebase Console, click **Build** → **Firestore Database**
2. Click **Create database**
3. Choose **Production mode** (recommended) or **Test mode** (for development)
4. Select a location closest to your users (e.g., `asia-southeast1`)
5. Click **Enable**

### 3. Generate Firebase Admin Service Account (for Backend)

1. In Firebase Console, go to **Project Settings** (⚙️ gear icon)
2. Click on **Service accounts** tab
3. Click **Generate new private key**
4. A JSON file will be downloaded (keep it secure! ⚠️)
5. Open the downloaded JSON file and copy these values to `backend/.env`:

```env
FIREBASE_PROJECT_ID=kitahack2026-8feed
FIREBASE_PRIVATE_KEY_ID="copy_from_json"
FIREBASE_PRIVATE_KEY="copy_from_json_including_quotes"
FIREBASE_CLIENT_EMAIL="firebase-adminsdk-xxxxx@kitahack2026-8feed.iam.gserviceaccount.com"
FIREBASE_CLIENT_ID="copy_from_json"
```

**Important:** The `FIREBASE_PRIVATE_KEY` should be wrapped in quotes and contain `\n` for line breaks.

## 🚀 Test the Setup

### Frontend Test:

```powershell
cd frontend
npm run dev
```

1. Open http://localhost:3001
2. Click **"Get Started"** → Should redirect to Sign In page
3. Click **"Sign up"** → Create a test account
4. Try signing in with Email/Password
5. Try signing in with Google
6. After successful login → Should redirect to Chat page

### Backend Test:

```powershell
cd backend
uvicorn main:app --reload
```

Expected output:
```
✅ Firebase Admin SDK initialized successfully
🚀 BossolutionAI API is ready!
```

## 📁 Firestore Collections Structure

The following collections will be created when you start using the features:

### Users Collection: `users/{userId}`
```json
{
  "email": "user@example.com",
  "displayName": "John Doe",
  "createdAt": "2024-01-15T10:30:00Z",
  "subscription": "free",
  "credits": 100
}
```

### Campaigns Collection: `campaigns/{campaignId}`
```json
{
  "userId": "user123",
  "name": "Spring Sale Campaign",
  "status": "active",
  "platforms": ["facebook", "instagram"],
  "budget": 5000,
  "startDate": "2024-02-01",
  "endDate": "2024-02-28",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

### Content Collection: `content/{contentId}`
```json
{
  "userId": "user123",
  "campaignId": "campaign123",
  "type": "post",
  "platform": "facebook",
  "content": "Check out our amazing spring sale!",
  "status": "draft",
  "scheduledDate": "2024-02-05T14:00:00Z",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

### Competitors Collection: `competitors/{competitorId}`
```json
{
  "userId": "user123",
  "name": "Competitor ABC",
  "website": "https://competitor.com",
  "platforms": ["facebook", "instagram"],
  "lastScanned": "2024-01-15T10:30:00Z"
}
```

### Analytics Collection: `analytics/{analyticsId}`
```json
{
  "userId": "user123",
  "campaignId": "campaign123",
  "date": "2024-02-05",
  "impressions": 15000,
  "clicks": 450,
  "conversions": 25,
  "revenue": 1250.50,
  "roi": 125.5
}
```

### Monitoring Collection: `monitoring/{monitoringId}`
```json
{
  "userId": "user123",
  "type": "keyword",
  "keywords": ["spring sale", "discount"],
  "platforms": ["twitter", "facebook"],
  "alerts": true,
  "createdAt": "2024-01-15T10:30:00Z"
}
```

## 🔐 Security Rules (Recommended)

After testing, update your Firestore Security Rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    match /campaigns/{campaignId} {
      allow read, write: if request.auth != null && 
        resource.data.userId == request.auth.uid;
    }
    
    match /content/{contentId} {
      allow read, write: if request.auth != null && 
        resource.data.userId == request.auth.uid;
    }
    
    match /competitors/{competitorId} {
      allow read, write: if request.auth != null && 
        resource.data.userId == request.auth.uid;
    }
    
    match /analytics/{analyticsId} {
      allow read: if request.auth != null && 
        resource.data.userId == request.auth.uid;
      allow write: if false; // Only backend can write
    }
    
    match /monitoring/{monitoringId} {
      allow read, write: if request.auth != null && 
        resource.data.userId == request.auth.uid;
    }
  }
}
```

## 🛠️ Next Steps

After Firebase is fully configured:

1. **Create Feature Services** - Implement backend services for each of the 6 BossolutionAI features
2. **Create API Routers** - Add routers for campaigns, content, competitors, etc.
3. **Connect Frontend to Backend** - Add API calls from React components to backend
4. **Implement AI Features** - Integrate Google Gemini API for content generation
5. **Add Publishing Integration** - Connect social media APIs (Facebook, Instagram, LinkedIn, Twitter)

## 📝 Environment Files Summary

### Frontend (`.env.local`)
```env
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Backend (`.env`)
```env
# Google Gemini
GOOGLE_API_KEY=your_gemini_api_key

# Tavily (competitor web search)
TAVILY_API_KEY=your_tavily_api_key

# Firebase Admin SDK
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY_ID=your_private_key_id
FIREBASE_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n..."
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxx@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your_client_id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token

# Email notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
NOTIFICATION_FROM_EMAIL=noreply@bossolutionai.com
```

## 🐛 Troubleshooting

### "Cannot find module 'firebase/app'" error
- Run: `npm install` in frontend folder

### "Firebase not initialized" in backend
- Make sure you completed Step 3 (Generate Service Account)
- Check that all Firebase environment variables are set in `backend/.env`

### "Invalid authentication credentials"
- Double-check that Email/Password and Google auth are enabled in Firebase Console
- Clear browser cache and try again

### "Permission denied" when accessing Firestore
- Update Security Rules in Firebase Console
- Make sure user is authenticated before accessing data

## 📚 Resources

- [Firebase Authentication Docs](https://firebase.google.com/docs/auth)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
