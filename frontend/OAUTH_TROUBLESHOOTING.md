# OAuth Consent Screen & YouTube API Troubleshooting Guide

## Issue: "Invalid URL: cannot contain a local host domain"

Google OAuth **does not allow localhost URLs** in the OAuth consent screen for External user type apps. This is a Google security policy.

## ✅ Solution for Testing (Recommended)

Since you're in **Testing mode** with test users, you have these options:

### Option 1: Leave Fields Empty (Simplest)
1. In the OAuth consent screen, **leave these fields EMPTY**:
   - Application home page
   - Application privacy policy link
   - Application terms of service link
2. Only fill **Authorised domains** - leave it EMPTY too for now
3. Make sure your email `limjl0130@gmail.com` is added as a test user
4. Click **Save and Continue**

**Why this works**: For apps in Testing mode, these URLs are optional and only shown to test users during OAuth consent.

---

### Option 2: Use Temporary Production URLs
If you must fill these fields, use temporary placeholder URLs:

```
Application home page: https://example.com
Privacy policy: https://example.com/privacy  
Terms of service: https://example.com/terms
Authorised domains: example.com
```

Replace with real URLs when you deploy to production.

---

## 🔧 Complete Setup Checklist

### Step 1: Enable YouTube Data API v3
- [x] Go to [APIs Library](https://console.cloud.google.com/apis/library/youtube.googleapis.com)
- [x] Select project: `kitahack2026-8feed`
- [x] Click **Enable**
- [x] Wait 1-2 minutes for propagation

### Step 2: Configure OAuth Consent Screen
- [ ] Go to [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)
- [ ] User Type: **External** (or Internal if available)
- [ ] Add these scopes:
  - `https://www.googleapis.com/auth/youtube.readonly`
  - `https://www.googleapis.com/auth/youtube.force-ssl`
  - `https://www.googleapis.com/auth/userinfo.profile`
  - `https://www.googleapis.com/auth/userinfo.email`
- [ ] **App domain section**: Leave empty OR use example.com placeholders
- [ ] Add test user: `limjl0130@gmail.com`
- [ ] Save

### Step 3: Verify OAuth Credentials
- [ ] Go to [Credentials](https://console.cloud.google.com/apis/credentials)
- [ ] Find your OAuth 2.0 Client ID
- [ ] Ensure **Authorized JavaScript origins** includes:
  - `http://localhost:3000`
  - `http://localhost:5173` (if using Vite)
- [ ] Ensure **Authorized redirect URIs** includes:
  - `http://localhost:3000/__/auth/handler`
  - Your Firebase Auth domain

---

## 🐛 Common Errors & Fixes

### Error: 401 Unauthorized
**Cause**: Invalid or expired access token

**Fix**:
1. Click "Disconnect" on the Platform page
2. Go to https://myaccount.google.com/permissions
3. Remove "KitaHack2026" access
4. Clear browser cache (`Ctrl+Shift+Delete`)
5. Reconnect YouTube on Platform page
6. **Grant ALL permissions** when prompted

### Error: 403 Forbidden
**Cause**: YouTube Data API v3 not enabled OR token issued before API was enabled

**Fix**:
1. Verify API is enabled (see Step 1 above)
2. Wait 2 minutes after enabling
3. Get a fresh token (disconnect & reconnect)
4. Check that you're added as a test user

### Error: No videos found
**Possible causes**:
- You don't have a YouTube channel
- Your channel has no uploaded videos
- Channel is too new (needs activation time)

**Fix**:
1. Go to youtube.com and make sure you have a channel
2. Upload at least one video
3. Wait a few minutes for YouTube to process
4. Click "Refresh" on the Platform page

---

## 🚀 Testing Your Setup

1. Open Chrome DevTools (F12) → Console tab
2. Go to http://localhost:3000/platform
3. Click "Connect YouTube"
4. Watch the console for detailed logs:
   - ✅ = Success
   - ⚠️ = Warning (non-critical)
   - ❌ = Error (needs fixing)

The logs will tell you exactly what's wrong.

---

## 📝 Production Deployment

When deploying to production:

1. Create actual Privacy Policy page (`/privacy`)
2. Create actual Terms of Service page (`/terms`)
3. Update OAuth consent screen with:
   - Real production URLs
   - Real authorised domains
4. Submit app for verification (if needed)
5. Update Firebase authorized domains

---

## 🆘 Still Having Issues?

Check the browser console for detailed error messages. The code includes comprehensive logging that will tell you:
- Token status
- API response codes
- Specific error messages
- Step-by-step fixes

Common console commands for debugging:
```javascript
// Check stored data
localStorage.getItem('firebase:authUser')

// Clear all data
localStorage.clear()
sessionStorage.clear()
```

---

## 💡 Key Points

1. **Localhost URLs are NOT allowed** in OAuth consent screen for External apps
2. For testing, **leave the App domain fields empty**
3. Test users can use the app even without these URLs
4. Tokens expire after ~1 hour - reconnect to refresh
5. API changes take 1-2 minutes to propagate
