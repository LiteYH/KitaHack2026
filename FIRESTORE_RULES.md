# 🔒 Firestore Security Rules Setup

## ⚠️ IMPORTANT: You MUST set these rules!

Without proper security rules, your database is either:
- Completely open (anyone can read/write) ❌
- Completely locked (even authenticated users can't access) ❌

---

## 📋 Steps to Update Rules

### 1. Go to Firebase Console
Open: https://console.firebase.google.com/project/kitahack2026-8feed/firestore/rules

### 2. Click "Rules" Tab
You'll see the current rules editor.

### 3. Replace with These Rules
Copy and paste these rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Users collection - users can only read/write their own document
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Campaigns collection - users can only access their own campaigns
    match /campaigns/{campaignId} {
      allow read, write: if request.auth != null && 
                           resource.data.userId == request.auth.uid;
      allow create: if request.auth != null && 
                       request.resource.data.userId == request.auth.uid;
    }
    
    // Content collection - users can only access their own content
    match /content/{contentId} {
      allow read, write: if request.auth != null && 
                           resource.data.userId == request.auth.uid;
      allow create: if request.auth != null && 
                       request.resource.data.userId == request.auth.uid;
    }
    
    // Competitors collection - users can only access their own competitors
    match /competitors/{competitorId} {
      allow read, write: if request.auth != null && 
                           resource.data.userId == request.auth.uid;
      allow create: if request.auth != null && 
                       request.resource.data.userId == request.auth.uid;
    }
    
    // Analytics collection - users can read their own analytics
    // Only backend can write (via Firebase Admin SDK)
    match /analytics/{analyticsId} {
      allow read: if request.auth != null && 
                     resource.data.userId == request.auth.uid;
      allow write: if false; // Only backend can write
    }
    
    // Monitoring collection - users can only access their own monitoring data
    match /monitoring/{monitoringId} {
      allow read, write: if request.auth != null && 
                           resource.data.userId == request.auth.uid;
      allow create: if request.auth != null && 
                       request.resource.data.userId == request.auth.uid;
    }
  }
}
```

### 4. Click "Publish"
Wait for confirmation message.

---

## 🧠 What These Rules Do

### Users Collection
```javascript
match /users/{userId} {
  allow read, write: if request.auth != null && request.auth.uid == userId;
}
```
- ✅ User can read/write **only their own** document (`/users/{their-uid}`)
- ❌ User **cannot** access other users' documents
- ❌ Unauthenticated users **cannot** access anything

### Example:
- User UID: `abc123`
- ✅ Can access: `/users/abc123`
- ❌ Cannot access: `/users/xyz789`

---

### Campaigns/Content/Competitors/Monitoring Collections
```javascript
allow read, write: if request.auth != null && 
                      resource.data.userId == request.auth.uid;
```
- ✅ User can only access documents where `userId` field matches their UID
- ❌ Cannot access other users' campaigns/content/etc.

### Example:
Document in `/campaigns/campaign123`:
```json
{
  "userId": "abc123",
  "name": "Spring Sale"
}
```
- User `abc123`: ✅ Can access
- User `xyz789`: ❌ Cannot access

---

### Analytics Collection (Read-Only for Users)
```javascript
allow read: if request.auth != null && 
               resource.data.userId == request.auth.uid;
allow write: if false; // Only backend can write
```
- ✅ Users can **read** their own analytics
- ❌ Users **cannot write** analytics (only backend via Admin SDK can)
- This prevents users from manipulating their own stats

---

## 🧪 Test Your Rules

### After Publishing Rules:

1. **Sign in to your app**: http://localhost:3001/auth/signin

2. **Open Browser DevTools** (F12)

3. **Go to Console tab**

4. **Test Create User Document** (should see):
```
✅ Created new user document for: your@email.com
```

5. **Sign out and sign in again** (should see):
```
✅ Updated lastLoginAt for: your@email.com
```

6. **Check Firestore in Firebase Console**:
   - Go to Firestore Database → Data tab
   - You should see:
   ```
   users (collection)
     └── {your-uid} (document)
          ├── email: "your@email.com"
          ├── createdAt: Timestamp
          └── lastLoginAt: Timestamp
   ```

---

## ⚠️ Common Issues

### Issue: "Missing or insufficient permissions"
**Cause**: Rules not published or user not authenticated

**Fix**:
1. Make sure you clicked "Publish" in Rules tab
2. Make sure user is signed in
3. Clear browser cache and try again

---

### Issue: "Document not created"
**Cause**: Rules might be blocking writes

**Fix**:
1. Check Firebase Console → Firestore → Rules tab
2. Make sure rules match exactly as shown above
3. Check browser console for error messages

---

### Issue: "Can see other users' data"
**Cause**: Rules not restrictive enough

**Fix**:
1. Double-check the `userId` field is being set correctly
2. Make sure rules check `resource.data.userId == request.auth.uid`
3. Test with 2 different accounts

---

## 🚀 Next Steps

After rules are set:

1. ✅ Users collection will auto-create on login
2. ✅ You can start implementing campaigns/content features
3. ✅ Each feature will automatically be user-scoped

---

## 📝 For Development (Optional)

If you want to test with **wide-open rules** temporarily:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

⚠️ **WARNING**: This allows ANY authenticated user to access ALL data!
Only use for quick testing, then switch back to proper rules.

---

## ✅ Checklist

- [ ] Opened Firebase Console → Firestore → Rules
- [ ] Copied and pasted the security rules
- [ ] Clicked "Publish"
- [ ] Tested sign in/sign up
- [ ] Saw "Created new user document" in console
- [ ] Verified user document in Firestore Database → Data tab
- [ ] Tested sign in again (should update lastLoginAt)

---

**Once these rules are set, your Firestore is secure and ready! 🎉**
