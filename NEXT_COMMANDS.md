# 🎯 Next Commands to Run

## Step 1: Complete Firebase Console Setup (5 minutes)

### A. Enable Authentication Providers
1. Open: https://console.firebase.google.com/project/kitahack2026-8feed/authentication
2. Click: **Get Started** (if first time)
3. Click: **Sign-in method** tab
4. Click: **Email/Password** row
   - Toggle **Enable**
   - Click **Save**
5. Click: **Google** row
   - Toggle **Enable**
   - Select your email as support email
   - Click **Save**

### B. Create Firestore Database
1. Open: https://console.firebase.google.com/project/kitahack2026-8feed/firestore
2. Click: **Create database**
3. Select: **Production mode** (recommended) or **Test mode** (development)
4. Choose location: **asia-southeast1** (or closest to you)
5. Click: **Enable**
6. Wait 1-2 minutes for creation

### C. Generate Service Account Key
1. Open: https://console.firebase.google.com/project/kitahack2026-8feed/settings/serviceaccounts/adminsdk
2. Click: **Generate new private key**
3. Click: **Generate key** in popup
4. Save the downloaded JSON file (keep it secure!)
5. Open the JSON file and copy these values to `backend/.env`:
   - `project_id` → `FIREBASE_PROJECT_ID`
   - `private_key_id` → `FIREBASE_PRIVATE_KEY_ID`
   - `private_key` → `FIREBASE_PRIVATE_KEY` (keep quotes!)
   - `client_email` → `FIREBASE_CLIENT_EMAIL`
   - `client_id` → `FIREBASE_CLIENT_ID`

---

## Step 2: Update Backend Environment File

Open `backend/.env` and replace the placeholders:

```env
# Keep existing settings
DEBUG=true
HOST=0.0.0.0
PORT=8000
GOOGLE_API_KEY=AIzaSyBDM6cNkW5n6bc3eMIO2dlq5va3q64nKeo
UPLOAD_DIR=temp_uploads
PROJECT_NAME=BossolutionAI Backend
ENVIRONMENT=development

# Replace these with values from downloaded JSON
FIREBASE_PROJECT_ID=kitahack2026-8feed
FIREBASE_PRIVATE_KEY_ID="your_private_key_id_from_json"
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour key here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL="firebase-adminsdk-xxxxx@kitahack2026-8feed.iam.gserviceaccount.com"
FIREBASE_CLIENT_ID="your_client_id_from_json"
```

**Important:** 
- Keep the quotes around `FIREBASE_PRIVATE_KEY`
- Don't remove the `\n` characters
- Don't commit this file to git!

---

## Step 3: Install Backend Dependency (Optional)

If you skipped it earlier:

```powershell
cd "c:\Yi Hao\UM\Competitions\Kitahack\backend"
pip install firebase-admin
```

---

## Step 4: Start Backend Server

```powershell
cd "c:\Yi Hao\UM\Competitions\Kitahack\backend"
uvicorn main:app --reload
```

**Expected output:**
```
✅ Firebase Admin SDK initialized successfully
🚀 BossolutionAI API is ready!
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**If you see this instead:**
```
Warning: Firebase credentials not configured. Skipping Firebase initialization.
```
→ Go back to Step 2 and check your `.env` file.

Keep this terminal open!

---

## Step 5: Start Frontend Server

Open a **NEW terminal** (don't close backend terminal):

```powershell
cd "c:\Yi Hao\UM\Competitions\Kitahack\frontend"
npm run dev
```

**Expected output:**
```
  ▲ Next.js 16.1.6
  - Local:        http://localhost:3001
  - Network:      http://192.168.x.x:3001

 ✓ Ready in 2-3s
```

Keep this terminal open!

---

## Step 6: Test the Application

### Open Browser
Navigate to: **http://localhost:3001**

### Test Sign Up
1. Click **"Get Started"** button
2. Should redirect to `/auth/signin`
3. Click **"Sign up"** link at bottom
4. Should redirect to `/auth/signup`
5. Enter:
   - Email: `test@example.com`
   - Password: `test123` (min 6 characters)
   - Confirm Password: `test123`
6. Click **"Create Account"**
7. Should redirect to `/chat` page ✅
8. Should see 6 feature cards:
   - Content Planning
   - Competitor Intelligence
   - Publishing
   - Campaign & Optimization
   - ROI Dashboard
   - Continuous Monitoring

### Verify in Firebase Console
1. Open: https://console.firebase.google.com/project/kitahack2026-8feed/authentication/users
2. Should see your test user: `test@example.com` ✅

### Test Sign In
1. Clear browser cookies or use Incognito mode
2. Go to: http://localhost:3001/auth/signin
3. Enter:
   - Email: `test@example.com`
   - Password: `test123`
4. Click **"Sign In"**
5. Should redirect to `/chat` ✅

### Test Google Sign In
1. Go to: http://localhost:3001/auth/signin
2. Click **"Google"** button
3. Select your Google account
4. Should redirect to `/chat` ✅
5. Check Firebase Console → Users
6. Should see new Google user ✅

### Test Protected Routes
1. Sign out (clear cookies or close browser)
2. Try to access: http://localhost:3001/chat
3. Should automatically redirect to `/auth/signin` ✅
4. Sign in
5. Should access `/chat` successfully ✅

---

## Step 7: Test Backend API (Optional)

### Open API Documentation
Navigate to: **http://localhost:8000/docs**

### Test Health Endpoint
1. Click on **GET /health**
2. Click **"Try it out"**
3. Click **"Execute"**
4. Should see:
```json
{
  "status": "ok",
  "environment": "development"
}
```

### Test Protected Endpoint (After you create one)
1. Sign in to frontend: http://localhost:3001/auth/signin
2. Open browser DevTools (F12)
3. Go to Application tab → Local Storage
4. Find Firebase auth token
5. Copy the token value
6. Go to: http://localhost:8000/docs
7. Click **"Authorize"** button (🔒)
8. Enter: `Bearer your_token_here`
9. Click **"Authorize"**
10. Now you can test protected endpoints ✅

---

## ✅ Verification Checklist

After completing all steps:

- [ ] Backend runs without errors
- [ ] Frontend runs without errors
- [ ] Firebase Authentication enabled (Email + Google)
- [ ] Firestore Database created
- [ ] Service account credentials in `backend/.env`
- [ ] Can sign up with email/password
- [ ] Can sign in with email/password
- [ ] Can sign in with Google
- [ ] User appears in Firebase Console
- [ ] Protected `/chat` page works
- [ ] Unauthenticated users redirected to signin
- [ ] Backend API docs accessible
- [ ] Health endpoint works

---

## 🐛 Troubleshooting

### Backend won't start
```
Error: No module named 'firebase_admin'
```
**Fix:** Run `pip install firebase-admin`

---

### Backend shows Firebase warning
```
Warning: Firebase credentials not configured.
```
**Fix:** Check `backend/.env` has all Firebase variables from service account JSON

---

### Frontend shows Firebase errors
```
Cannot find module 'firebase/app'
```
**Fix:** Run `npm install` in frontend folder

---

### Authentication fails
```
Error: auth/invalid-email or auth/wrong-password
```
**Fix:** 
- Verify Email/Password is enabled in Firebase Console
- Check email format is correct
- Try creating account first before signing in

---

### Google Sign In doesn't work
```
Error: popup_closed_by_user or auth/unauthorized-domain
```
**Fix:**
- Verify Google provider is enabled in Firebase Console
- Check project support email is set
- For production, add your domain to authorized domains

---

### "Permission denied" in Firestore
```
Error: Missing or insufficient permissions
```
**Fix:**
- Update Firestore Security Rules in Firebase Console
- For development, you can temporarily use Test mode
- See `FIREBASE_SETUP.md` for recommended security rules

---

## 🎉 Success!

If all checklist items are completed, you're ready to build features! 🚀

### Next Steps:
1. Read `ARCHITECTURE.md` to understand the system
2. Check `backend/README.md` for API development guide
3. Start implementing the 6 BossolutionAI features:
   - Content Planning (start here - simplest)
   - Competitor Intelligence
   - Publishing
   - Campaign & Optimization
   - ROI Dashboard
   - Continuous Monitoring

---

## 📚 Documentation

Quick reference:
- `QUICKSTART.md` - Get started in 5 minutes
- `FIREBASE_SETUP.md` - Detailed Firebase guide
- `FIREBASE_CHECKLIST.md` - Verification checklist
- `WHAT_WAS_DONE.md` - Summary of changes
- `ARCHITECTURE.md` - System architecture

---

## 🆘 Still Having Issues?

1. Check all environment variables are set
2. Restart both servers after changing `.env` files
3. Clear browser cache/cookies
4. Try Incognito mode
5. Check Firebase Console for user creation
6. Check backend terminal for error messages
7. Check browser DevTools console for errors

---

**Good luck building BossolutionAI! 🚀**
