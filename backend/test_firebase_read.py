"""
Test script to read data from Firebase Firestore.
This script demonstrates how to read data from various collections.
"""

import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.firebase import initialize_firebase, get_db


def test_read_users():
    """Test reading data from the users collection."""
    print("\n" + "="*50)
    print("Testing Users Collection")
    print("="*50)
    
    try:
        db = get_db()
        if db is None:
            print("❌ Firebase not initialized")
            return
        
        # Get all users
        users_ref = db.collection('users')
        users = users_ref.stream()
        
        user_count = 0
        for user in users:
            user_count += 1
            user_data = user.to_dict()
            print(f"\n📄 User ID: {user.id}")
            print(f"   Data: {user_data}")
        
        if user_count == 0:
            print("ℹ️  No users found in the collection")
        else:
            print(f"\n✅ Found {user_count} user(s)")
            
    except Exception as e:
        print(f"❌ Error reading users: {str(e)}")


def test_read_chats():
    """Test reading data from the chats collection."""
    print("\n" + "="*50)
    print("Testing Chats Collection")
    print("="*50)
    
    try:
        db = get_db()
        if db is None:
            print("❌ Firebase not initialized")
            return
        
        # Get all chats
        chats_ref = db.collection('chats')
        chats = chats_ref.stream()
        
        chat_count = 0
        for chat in chats:
            chat_count += 1
            chat_data = chat.to_dict()
            print(f"\n💬 Chat ID: {chat.id}")
            print(f"   Data: {chat_data}")
        
        if chat_count == 0:
            print("ℹ️  No chats found in the collection")
        else:
            print(f"\n✅ Found {chat_count} chat(s)")
            
    except Exception as e:
        print(f"❌ Error reading chats: {str(e)}")


def test_read_messages():
    """Test reading messages from a specific chat."""
    print("\n" + "="*50)
    print("Testing Messages Subcollection")
    print("="*50)
    
    try:
        db = get_db()
        if db is None:
            print("❌ Firebase not initialized")
            return
        
        # First, get a chat to read messages from
        chats_ref = db.collection('chats')
        chats = list(chats_ref.limit(1).stream())
        
        if not chats:
            print("ℹ️  No chats available to read messages from")
            return
        
        chat_id = chats[0].id
        print(f"📝 Reading messages from chat: {chat_id}")
        
        # Get messages from the chat
        messages_ref = db.collection('chats').document(chat_id).collection('messages')
        messages = messages_ref.order_by('timestamp').stream()
        
        message_count = 0
        for message in messages:
            message_count += 1
            message_data = message.to_dict()
            print(f"\n   Message ID: {message.id}")
            print(f"   Data: {message_data}")
        
        if message_count == 0:
            print(f"ℹ️  No messages found in chat {chat_id}")
        else:
            print(f"\n✅ Found {message_count} message(s)")
            
    except Exception as e:
        print(f"❌ Error reading messages: {str(e)}")


def list_all_collections():
    """List all root-level collections in Firestore."""
    print("\n" + "="*50)
    print("Listing All Collections")
    print("="*50)
    
    try:
        db = get_db()
        if db is None:
            print("❌ Firebase not initialized")
            return
        
        collections = db.collections()
        collection_names = [col.id for col in collections]
        
        if not collection_names:
            print("ℹ️  No collections found")
        else:
            print(f"\n📚 Found {len(collection_names)} collection(s):")
            for name in collection_names:
                print(f"   - {name}")
            
    except Exception as e:
        print(f"❌ Error listing collections: {str(e)}")


def main():
    """Main function to run all tests."""
    print("\n" + "🔥"*25)
    print("Firebase Firestore Read Test")
    print("🔥"*25)
    
    # Initialize Firebase
    print("\n🔧 Initializing Firebase...")
    app, db = initialize_firebase()
    
    if app is None or db is None:
        print("\n❌ Failed to initialize Firebase. Please check your .env configuration.")
        return
    
    # Run tests
    list_all_collections()
    test_read_users()
    test_read_chats()
    test_read_messages()
    
    print("\n" + "="*50)
    print("✅ Test completed!")
    print("="*50)


if __name__ == "__main__":
    main()
