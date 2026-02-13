# ✅ Firebase Setup Checklist

Use this checklist to ensure your Firebase setup is complete.

## 📋 Pre-Setup

- [ ] Have a Google account
- [ ] Opened [Firebase Console](https://console.firebase.google.com/)
- [ ] Selected project **kitahack2026-8feed**

---

## 🔐 Authentication Setup

### Enable Sign-In Methods
- [ ] Opened **Build** → **Authentication** in Firebase Console
- [ ] Clicked **Get Started** (if first time)
- [ ] Went to **Sign-in method** tab
- [ ] Enabled **Email/Password** provider
  - [ ] Clicked on Email/Password row
  - [ ] Toggled **Enable** switch
  - [ ] Clicked **Save**
- [ ] Enabled **Google** provider
  - [ ] Clicked on Google row
  - [ ] Toggled **Enable** switch
  - [ ] Selected project support email
  - [ ] Clicked **Save**

### Test Authentication (Optional)
- [ ] Went to **Users** tab
- [ ] Should see empty list (no users yet)
- [ ] Will populate after first sign-up

---

## 🗄️ Firestore Database Setup

### Create Database
- [ ] Opened **Build** → **Firestore Database**
- [ ] Clicked **Create database**
- [ ] Selected mode:
  - [ ] **Production mode** (recommended) - requires security rules
  - [ ] **Test mode** (development only) - open for 30 days
- [ ] Selected location (e.g., `asia-southeast1` or `us-central1`)
- [ ] Clicked **Enable**
- [ ] Waited for database creation (1-2 minutes)

### Verify Database
- [ ] See **Data** tab with empty collections
- [ ] See **Rules** tab with default rules
- [ ] See **Indexes** tab (empty for now)

---

## 🔑 Service Account Setup (Backend)

### Generate Private Key
- [ ] Clicked ⚙️ **Project Settings** (top left)
- [ ] Went to **Service accounts** tab
- [ ] Clicked **Generate new private key**
- [ ] Confirmed in popup dialog
- [ ] Downloaded JSON file
- [ ] **IMPORTANT**: Saved JSON file in secure location (NOT in git repo!)

### Extract Credentials
- [ ] Opened downloaded JSON file
- [ ] Found `project_id` value
- [ ] Found `private_key_id` value
- [ ] Found `private_key` value (long string with `\n`)
- [ ] Found `client_email` value
- [ ] Found `client_id` value

### Update Backend .env
- [ ] Opened `backend/.env` file
- [ ] Pasted `project_id` → `FIREBASE_PROJECT_ID`
- [ ] Pasted `private_key_id` → `FIREBASE_PRIVATE_KEY_ID`
- [ ] Pasted `private_key` → `FIREBASE_PRIVATE_KEY` (keep the quotes!)
- [ ] Pasted `client_email` → `FIREBASE_CLIENT_EMAIL`
- [ ] Pasted `client_id` → `FIREBASE_CLIENT_ID`
- [ ] Saved file
- [ ] **IMPORTANT**: Verified `.env` is in `.gitignore`

---

## 📦 Dependencies Installation

### Frontend
- [ ] Opened terminal in `frontend` folder
- [ ] Ran `npm install`
- [ ] No errors in installation
- [ ] Verified `firebase` package in `node_modules`

### Backend
- [ ] Opened terminal in `backend` folder
- [ ] Ran `pip install firebase-admin` (or `pip install -r requirements.txt`)
- [ ] No errors in installation
- [ ] Verified installation: `python -c "import firebase_admin; print('OK')"`

---

## 🧪 Testing

### Backend Test
- [ ] Started backend: `uvicorn main:app --reload`
- [ ] Saw in console: `✅ Firebase Admin SDK initialized successfully`
- [ ] Saw in console: `🚀 BossolutionAI API is ready!`
- [ ] Opened http://localhost:8000/docs
- [ ] Swagger UI loaded successfully
- [ ] Tested `/health` endpoint → Status 200

### Frontend Test
- [ ] Started frontend: `npm run dev`
- [ ] No compilation errors
- [ ] Opened http://localhost:3001
- [ ] Welcome page loaded with Aurora background

### Authentication Flow Test

#### Sign Up
- [ ] Clicked **Get Started** button
- [ ] Redirected to `/auth/signin`
- [ ] Clicked **Sign up** link
- [ ] Redirected to `/auth/signup`
- [ ] Entered test email (e.g., `test@example.com`)
- [ ] Entered password (min 6 characters)
- [ ] Confirmed password
- [ ] Clicked **Create Account**
- [ ] Successfully redirected to `/chat` page
- [ ] Saw chat interface with 6 feature cards

#### Verify User in Firebase
- [ ] Opened Firebase Console → Authentication → Users
- [ ] Saw newly created user in list
- [ ] Verified email matches

#### Sign Out & Sign In
- [ ] Signed out (clear browser cookies or use incognito)
- [ ] Went to `/auth/signin`
- [ ] Entered same email and password
- [ ] Clicked **Sign In**
- [ ] Successfully redirected to `/chat`

#### Google Sign In
- [ ] Went to `/auth/signin`
- [ ] Clicked **Google** button
- [ ] Google account picker appeared
- [ ] Selected Google account
- [ ] Successfully redirected to `/chat`
- [ ] Checked Firebase Console → Users for new Google user

#### Password Reset
- [ ] Went to `/auth/forgot-password`
- [ ] Entered email address
- [ ] Clicked **Send Reset Link**
- [ ] Saw success message
- [ ] Checked email inbox
- [ ] Received Firebase password reset email
- [ ] Clicked link in email
- [ ] Reset password successfully

#### Protected Route Test
- [ ] Signed out completely
- [ ] Tried accessing `/chat` directly
- [ ] Automatically redirected to `/auth/signin`
- [ ] Signed in
- [ ] Successfully accessed `/chat`

---

## 🎯 Firestore Database Test

### Create Test Data (Optional)
- [ ] Opened Firebase Console → Firestore Database
- [ ] Clicked **Start collection**
- [ ] Collection ID: `test`
- [ ] Added document with auto ID
- [ ] Added field: `message` (string) = `"Hello Firebase!"`
- [ ] Saved document
- [ ] Verified document appears in database

### Test Backend Connection
- [ ] Created test endpoint in backend (optional):
```python
@app.get("/test-firestore")
async def test_firestore():
    from app.core.firebase import get_db
    db = get_db()
    doc_ref = db.collection('test').document()
    doc_ref.set({'timestamp': firestore.SERVER_TIMESTAMP})
    return {"status": "success", "id": doc_ref.id}
```
- [ ] Called endpoint: http://localhost:8000/test-firestore
- [ ] Checked Firebase Console → Firestore
- [ ] Verified new document was created

---

## 🔒 Security (Important for Production!)

### Update Security Rules
- [ ] Opened Firestore Database → Rules tab
- [ ] Pasted recommended security rules from `FIREBASE_SETUP.md`
- [ ] Clicked **Publish**
- [ ] Verified rules are active

### API Keys
- [ ] Verified Firebase API keys in `.env.local` are public (frontend)
- [ ] Verified service account credentials in `.env` are NOT committed to git
- [ ] Added `.env` and `.env.local` to `.gitignore`

---

## 📊 Final Verification

### All Systems Check
- [ ] ✅ Frontend running on http://localhost:3001
- [ ] ✅ Backend running on http://localhost:8000
- [ ] ✅ Firebase Authentication working
- [ ] ✅ Firestore Database accessible
- [ ] ✅ User can sign up
- [ ] ✅ User can sign in
- [ ] ✅ Google Sign In works
- [ ] ✅ Password reset works
- [ ] ✅ Protected routes work
- [ ] ✅ Backend verifies tokens
- [ ] ✅ Backend connects to Firestore

---

## 🎉 Success!

If all items are checked, your Firebase setup is **COMPLETE**! 🎊

### What You Can Do Now:
1. ✅ Build the 6 BossolutionAI features
2. ✅ Create Firestore collections for your data
3. ✅ Implement backend services
4. ✅ Connect frontend to backend APIs
5. ✅ Deploy to production

---

## 📝 Notes

### Common Issues & Solutions

**Issue**: "Firebase not initialized" in backend
- **Solution**: Check all environment variables in `backend/.env`
- **Solution**: Restart backend server after updating .env

**Issue**: "Authentication failed" when signing in
- **Solution**: Verify Email/Password is enabled in Firebase Console
- **Solution**: Check browser console for detailed error

**Issue**: "Cannot find module 'firebase/app'"
- **Solution**: Run `npm install` in frontend folder

**Issue**: "Permission denied" in Firestore
- **Solution**: Update security rules in Firebase Console
- **Solution**: Make sure user is authenticated

**Issue**: Google Sign In doesn't work
- **Solution**: Verify Google provider is enabled
- **Solution**: Check project support email is set

---

## 🆘 Need Help?

Refer to:
- `FIREBASE_SETUP.md` - Detailed setup guide
- `QUICKSTART.md` - Quick start instructions
- `ARCHITECTURE.md` - System architecture
- Firebase Docs: https://firebase.google.com/docs

---

**Last Updated**: After Firebase integration
**Status**: Ready for feature development 🚀
