"""
Check what messages are in Firestore
"""
from app.core.firebase import get_db

def check_messages():
    db = get_db()
    
    print("🔍 Checking chat_messages collection...")
    messages = db.collection('chat_messages').stream()
    
    count = 0
    for msg in messages:
        count += 1
        data = msg.to_dict()
        print(f"\n📝 Message {count}:")
        print(f"  ID: {msg.id}")
        print(f"  Thread: {data.get('thread_id', 'N/A')}")
        print(f"  User: {data.get('user_id', 'N/A')}")
        print(f"  Role: {data.get('role', 'N/A')}")
        print(f"  Content: {data.get('content', 'N/A')[:100]}")
        print(f"  Created: {data.get('created_at', 'N/A')}")
    
    if count == 0:
        print("\n❌ No messages found in Firestore!")
    else:
        print(f"\n✅ Total messages: {count}")
    
    print("\n🔍 Checking user_profiles collection...")
    profiles = db.collection('user_profiles').stream()
    for profile in profiles:
        data = profile.to_dict()
        print(f"\n👤 User Profile:")
        print(f"  ID: {profile.id}")
        print(f"  Active Thread: {data.get('active_thread_id', 'N/A')}")

if __name__ == '__main__':
    check_messages()
