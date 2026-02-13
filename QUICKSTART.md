# 🚀 Quick Start Guide - BossolutionAI

## ⚡ Get Started in 5 Minutes

### Prerequisites
- Node.js 18+ and npm
- Python 3.10+
- Firebase account (free tier is fine)

---

## 📦 Step 1: Install Dependencies

### Frontend
```powershell
cd frontend
npm install
```

### Backend
```powershell
cd backend
pip install -r requirements.txt
```

---

## 🔥 Step 2: Configure Firebase (IMPORTANT!)

### A. Enable Authentication
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select project: **kitahack2026-8feed**
3. Navigate: **Build** → **Authentication** → **Get Started**
4. Enable these sign-in methods:
   - ✅ **Email/Password**
   - ✅ **Google**

### B. Create Firestore Database
1. Navigate: **Build** → **Firestore Database**
2. Click **Create database**
3. Choose **Production mode** (or Test mode for development)
4. Select closest region (e.g., `asia-southeast1`)
5. Click **Enable**

### C. Get Service Account for Backend
1. Navigate: **Project Settings** (⚙️) → **Service accounts**
2. Click **Generate new private key**
3. Download JSON file (keep it secure! 🔒)
4. Open the JSON and copy values to `backend/.env`:

```env
FIREBASE_PROJECT_ID=kitahack2026-8feed
FIREBASE_PRIVATE_KEY_ID="paste_from_json"
FIREBASE_PRIVATE_KEY="paste_from_json_with_quotes"
FIREBASE_CLIENT_EMAIL="firebase-adminsdk-xxxxx@kitahack2026-8feed.iam.gserviceaccount.com"
FIREBASE_CLIENT_ID="paste_from_json"
```

**✅ Frontend `.env.local` is already configured!**

---

## 🏃 Step 3: Run the Application

### Terminal 1: Start Backend
```powershell
cd backend
uvicorn main:app --reload
```

Expected output:
```
✅ Firebase Admin SDK initialized successfully
🚀 BossolutionAI API is ready!
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Terminal 2: Start Frontend
```powershell
cd frontend
npm run dev
```

Expected output:
```
  ▲ Next.js 16.1.6
  - Local:        http://localhost:3001
  - Network:      http://192.168.x.x:3001

 ✓ Ready in 2.5s
```

---

## 🎯 Step 4: Test the Application

### Open in Browser
Navigate to: **http://localhost:3001**

### Test User Flow
1. ✅ Welcome page loads with Aurora background
2. ✅ Click **"Get Started"** → Redirects to Sign In
3. ✅ Click **"Sign up"** → Create test account
4. ✅ Enter email (e.g., `test@example.com`) and password
5. ✅ Click **"Create Account"** → Should redirect to Chat page
6. ✅ See 6 BossolutionAI feature cards:
   - Content Planning
   - Competitor Intelligence
   - Publishing
   - Campaign & Optimization
   - ROI Dashboard
   - Continuous Monitoring

### Test Google Sign In
1. ✅ Go back to Sign In page
2. ✅ Click **"Google"** button
3. ✅ Select Google account
4. ✅ Should redirect to Chat page

### Test Protected Routes
1. ✅ Log out (if you add logout button)
2. ✅ Try accessing `/chat` directly
3. ✅ Should redirect to `/auth/signin`

---

## 🔍 Verify Everything Works

### Check Backend API
Visit: **http://localhost:8000/docs**
- ✅ Swagger UI should load
- ✅ See available endpoints
- ✅ Test `/health` endpoint

### Check Firebase Connection
In backend terminal, you should see:
```
✅ Firebase Admin SDK initialized successfully
```

If you see warnings about Firebase not configured, check your `.env` file.

---

## 🐛 Troubleshooting

### Frontend: "Cannot find module 'firebase/app'"
```powershell
cd frontend
npm install
```

### Backend: "No module named 'firebase_admin'"
```powershell
cd backend
pip install firebase-admin
```

### "Firebase Admin SDK not initialized"
- Check `backend/.env` has all Firebase variables
- Make sure you downloaded the service account JSON
- Verify the private key includes `\n` for newlines

### "Authentication failed" when signing in
- Check Email/Password is enabled in Firebase Console
- Try creating account first before signing in
- Check browser console for detailed error

### Can't access `/chat` page
- Make sure you're signed in
- Check AuthContext is working (should show loading spinner)
- Clear browser cache and try again

---

## 📚 Next Steps

After everything is working:

1. **Add User Profile**
   - Display user info in header
   - Add logout button
   - Profile settings page

2. **Implement Features**
   - Start with Content Planning (simplest)
   - Add Gemini AI integration
   - Create feature-specific pages

3. **Connect to Social Media**
   - Get Facebook/Instagram API tokens
   - Get LinkedIn API token
   - Get Twitter/X API key

4. **Add Firestore Security Rules**
   - See `FIREBASE_SETUP.md` for recommended rules
   - Test with Firebase Emulator first

---

## 📖 Documentation

- 🏗️ **ARCHITECTURE.md** - Visual system architecture
- 🔥 **FIREBASE_SETUP.md** - Detailed Firebase setup
- 📋 **FIREBASE_INTEGRATION_SUMMARY.md** - Complete integration details
- 🔧 **backend/README.md** - Backend API documentation
- 📁 **backend/STRUCTURE.md** - Folder structure explanation

---

## ✨ Features Currently Working

### Authentication ✅
- [x] Email/Password Sign Up
- [x] Email/Password Sign In
- [x] Google Sign In
- [x] Password Reset
- [x] Protected Routes
- [x] Session Persistence

### Pages ✅
- [x] Welcome Page with Aurora background
- [x] Sign In Page
- [x] Sign Up Page
- [x] Forgot Password Page
- [x] Chat Dashboard (protected)

### Backend ✅
- [x] FastAPI server running
- [x] CORS configured
- [x] Firebase Admin SDK initialized
- [x] Authentication middleware
- [x] Health check endpoint
- [x] Items CRUD API (example)

### To Be Implemented 🚧
- [ ] Content Planning API
- [ ] Competitor Intelligence API
- [ ] Publishing API
- [ ] Campaign Management API
- [ ] Analytics/ROI Dashboard API
- [ ] Monitoring API
- [ ] Social Media Integration
- [ ] Gemini AI Integration
- [ ] User Profile Page
- [ ] Subscription Management

---

## 🎉 Success!

If you've completed all steps and can:
- ✅ Sign up/sign in
- ✅ Access protected chat page
- ✅ See 6 feature cards
- ✅ Backend API is running

**Congratulations! Your BossolutionAI setup is complete!** 🎊

Now you can start building the 6 marketing features! 🚀

---

## 💡 Tips

1. **Use API Docs**: Visit `http://localhost:8000/docs` for interactive API testing
2. **Check Logs**: Backend terminal shows all requests and errors
3. **Browser DevTools**: Use Network tab to debug API calls
4. **Firebase Console**: Monitor authentication and database activity
5. **Git Commits**: Commit after each feature works

---

## 🆘 Need Help?

1. Check `FIREBASE_SETUP.md` for detailed Firebase instructions
2. Check `ARCHITECTURE.md` to understand system design
3. Check browser console for frontend errors
4. Check backend terminal for API errors
5. Verify all environment variables are set

---

## 🔗 Useful Links

- Frontend: http://localhost:3001
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Firebase Console: https://console.firebase.google.com/project/kitahack2026-8feed
- Google Gemini API: https://makersuite.google.com/app/apikey

---

**Happy coding! 🚀**
