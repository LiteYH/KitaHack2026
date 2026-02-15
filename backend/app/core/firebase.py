import firebase_admin
from firebase_admin import credentials, auth, firestore
from app.core.config import settings
import json
from typing import Optional

_app: Optional[firebase_admin.App] = None
_db: Optional[firestore.Client] = None


def initialize_firebase():
    """
    Initialize Firebase Admin SDK with service account credentials.
    This should be called once during application startup.
    """
    global _app, _db
    
    if _app is None:
        try:
            # Check if Firebase credentials are configured
            if not settings.FIREBASE_PROJECT_ID:
                print("Warning: Firebase credentials not configured. Skipping Firebase initialization.")
                return None, None
            
            # Check if Firebase is already initialized
            try:
                _app = firebase_admin.get_app()
                _db = firestore.client()
                print("✅ Using existing Firebase Admin SDK instance")
                return _app, _db
            except ValueError:
                # App doesn't exist, initialize it
                pass
            
            # Initialize with service account credentials
            cred_dict = {
                "type": "service_account",
                "project_id": settings.FIREBASE_PROJECT_ID,
                "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
                "private_key": settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n') if settings.FIREBASE_PRIVATE_KEY else None,
                "client_email": settings.FIREBASE_CLIENT_EMAIL,
                "client_id": settings.FIREBASE_CLIENT_ID,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.FIREBASE_CLIENT_EMAIL}"
            }
            
            cred = credentials.Certificate(cred_dict)
            _app = firebase_admin.initialize_app(cred)
            _db = firestore.client()
            
            print("✅ Firebase Admin SDK initialized successfully")
            return _app, _db
            
        except Exception as e:
            print(f"❌ Failed to initialize Firebase: {str(e)}")
            print("The app will continue running without Firebase functionality.")
            return None, None
    
    return _app, _db


def get_db() -> firestore.Client:
    """
    Get Firestore database client.
    Returns the initialized Firestore client or None if not initialized.
    """
    if _db is None:
        _, db = initialize_firebase()
        return db
    return _db


def verify_token(id_token: str) -> dict:
    """
    Verify a Firebase ID token.
    
    Args:
        id_token: The Firebase ID token to verify
        
    Returns:
        Decoded token containing user information
        
    Raises:
        Exception: If token is invalid or verification fails
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise Exception(f"Token verification failed: {str(e)}")


def get_user(uid: str) -> dict:
    """
    Get user information by UID.
    
    Args:
        uid: The user's Firebase UID
        
    Returns:
        User record dictionary
        
    Raises:
        Exception: If user not found or retrieval fails
    """
    try:
        user = auth.get_user(uid)
        return {
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name,
            "photo_url": user.photo_url,
            "email_verified": user.email_verified,
            "disabled": user.disabled,
            "created_at": user.user_metadata.creation_timestamp,
            "last_sign_in": user.user_metadata.last_sign_in_timestamp,
        }
    except Exception as e:
        raise Exception(f"Failed to get user: {str(e)}")
