# 🧪 Quick Test Commands

## Test the Firestore User Implementation

### Step 1: Set Firestore Rules (REQUIRED!)

Open: https://console.firebase.google.com/project/kitahack2026-8feed/firestore/rules

Paste this and click **Publish**:

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

---

### Step 2: Start Frontend (if not running)

```powershell
cd "c:\Yi Hao\UM\Competitions\Kitahack\frontend"
npm run dev
```

---

### Step 3: Test Sign Up (First Time User)

1. Open: http://localhost:3001
2. Click **"Get Started"**
3. Click **"Sign up"**
4. Enter:
   - Email: `testuser@example.com`
   - Password: `test1234`
   - Confirm: `test1234`
5. Click **"Create Account"**
6. Should redirect to `/chat` ✅

**Open Browser DevTools (F12) → Console tab**

You should see:
```
✅ Created new user document for: testuser@example.com
```

---

### Step 4: Verify in Firestore Console

Open: https://console.firebase.google.com/project/kitahack2026-8feed/firestore/data

You should see:

```
📁 users (collection)
   └── 📄 Zf3xyKT8... (your UID)
        ├── email: "testuser@example.com"
        ├── createdAt: Feb 13, 2026 at 10:30 AM
        └── lastLoginAt: Feb 13, 2026 at 10:30 AM
```

✅ **Document ID should match your Firebase Auth UID!**

---

### Step 5: Test Returning User (Update lastLoginAt)

1. **Sign out** (or use Incognito mode)
2. Go to: http://localhost:3001/auth/signin
3. Sign in with: `testuser@example.com` / `test1234`
4. Should redirect to `/chat` ✅

**Check Console (F12)**:
```
✅ Updated lastLoginAt for: testuser@example.com
```

**Check Firestore Console**:
- `lastLoginAt` should have a **newer timestamp** ✅
- `createdAt` should **stay the same** ✅

---

### Step 6: Test Google Sign In

1. Go to: http://localhost:3001/auth/signin
2. Click **"Google"** button
3. Select Google account
4. Should redirect to `/chat` ✅

**Check Console**:
```
✅ Created new user document for: yourgoogle@gmail.com
```
(or "Updated lastLoginAt" if you used this Google account before)

**Check Firestore Console**:
- New user document with Google email ✅

---

## 🐛 Troubleshooting

### "Missing or insufficient permissions"

**Problem**: Firestore rules not set or incorrect

**Fix**:
1. Go to Firestore → Rules tab
2. Make sure rules are published
3. Check `match /users/{userId}` exists
4. Click **Publish** again

---

### "Document not created"

**Problem**: Rules blocking or auth not working

**Fix**:
1. Check browser console for errors
2. Make sure you're signed in (check `auth.currentUser`)
3. Try signing out and in again
4. Check backend terminal for errors

---

### "Cannot read properties of null"

**Problem**: `auth.currentUser` is null

**Fix**:
1. Make sure you completed sign in
2. Check AuthContext is wrapped around app
3. Wait for auth state to load (check `loading` state)

---

### Console shows nothing

**Problem**: Browser console might be filtered

**Fix**:
1. Press F12 → Console tab
2. Check filter dropdown (should be "All levels")
3. Look for 🔵 info messages
4. Look for ✅ emoji in messages

---

## ✅ Success Criteria

After all tests, you should have:

- [x] User document created on first sign up
- [x] `lastLoginAt` updated on subsequent logins
- [x] Console logs show success messages
- [x] Firestore Console shows documents
- [x] Document ID = Firebase Auth UID
- [x] Google Sign In creates document too
- [x] No permission errors

---

## 🎉 If Everything Works

You now have:
- ✅ Automatic user tracking
- ✅ Login activity monitoring
- ✅ User-linked data structure ready
- ✅ Secure Firestore rules

**You're ready to implement the 6 BossolutionAI features!** 🚀

---

## 📝 Quick Reference

### Get Current User UID
```typescript
import { auth } from "@/lib/firebase";
const uid = auth.currentUser?.uid;
```

### Get User Document
```typescript
import { getUserDoc } from "@/lib/firestore/users";
const userData = await getUserDoc(uid);
console.log(userData);
```

### Link Data to User
```typescript
// When creating campaigns, content, etc.
const campaign = {
  userId: auth.currentUser?.uid,  // 🔥 Always include this
  name: "Spring Sale",
  // ... other fields
};
```

---

**Happy testing! 🎊**
