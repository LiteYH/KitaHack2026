import { auth, db } from "@/lib/firebase";
import { doc, getDoc, setDoc, updateDoc, serverTimestamp } from "firebase/firestore";

/**
 * Ensures user document exists in Firestore.
 * Creates new document on first login, updates lastLoginAt on subsequent logins.
 * 
 * Document structure:
 * /users/{uid}
 *   - email: string
 *   - createdAt: timestamp
 *   - lastLoginAt: timestamp
 */
export async function ensureUserDoc() {
  const user = auth.currentUser;
  if (!user) return;

  const userRef = doc(db, "users", user.uid);
  const userSnap = await getDoc(userRef);

  if (!userSnap.exists()) {
    // First time login - create new user document
    await setDoc(userRef, {
      email: user.email ?? "",
      createdAt: serverTimestamp(),
      lastLoginAt: serverTimestamp(),
    });
    console.log("✅ Created new user document for:", user.email);
  } else {
    // Returning user - update last login time
    await updateDoc(userRef, {
      lastLoginAt: serverTimestamp(),
    });
    console.log("✅ Updated lastLoginAt for:", user.email);
  }
}

/**
 * Get user document from Firestore
 */
export async function getUserDoc(uid: string) {
  const userRef = doc(db, "users", uid);
  const userSnap = await getDoc(userRef);
  
  if (userSnap.exists()) {
    return { id: userSnap.id, ...userSnap.data() };
  }
  
  return null;
}
