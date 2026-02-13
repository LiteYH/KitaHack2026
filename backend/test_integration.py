"""
Integration test for chat API endpoints using httpx
Run this with the server running: python main.py
"""
import asyncio
import httpx


BASE_URL = "http://localhost:8000/api/v1"


async def test_health():
    """Test the health endpoint"""
    print("\n1. Testing /chat/health endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/chat/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200
        print("   ✓ Health check passed")


async def test_chat_message():
    """Test sending a chat message"""
    print("\n2. Testing /chat/message endpoint...")
    async with httpx.AsyncClient() as client:
        payload = {
            "message": "Hello! What can you help me with?",
            "conversation_history": None,
            "user_id": "test_user"
        }
        response = await client.post(
            f"{BASE_URL}/chat/message",
            json=payload,
            timeout=30.0
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response preview: {data['message'][:100]}...")
        assert response.status_code == 200
        assert "message" in data
        print("   ✓ Chat message test passed")


async def test_chat_with_history():
    """Test chat with conversation history"""
    print("\n3. Testing chat with conversation history...")
    async with httpx.AsyncClient() as client:
        payload = {
            "message": "Can you give me specific examples?",
            "conversation_history": [
                {"role": "user", "content": "I need marketing help for my bakery"},
                {"role": "assistant", "content": "I can help you with marketing strategies for your bakery!"}
            ],
            "user_id": "test_user"
        }
        response = await client.post(
            f"{BASE_URL}/chat/message",
            json=payload,
            timeout=30.0
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response preview: {data['message'][:100]}...")
        assert response.status_code == 200
        print("   ✓ Conversation history test passed")


async def test_streaming():
    """Test streaming endpoint"""
    print("\n4. Testing /chat/stream endpoint...")
    async with httpx.AsyncClient() as client:
        payload = {
            "message": "Give me 3 quick tips",
            "conversation_history": None,
            "user_id": "test_user"
        }
        
        chunks = 0
        async with client.stream(
            "POST",
            f"{BASE_URL}/chat/stream",
            json=payload,
            timeout=30.0
        ) as response:
            print(f"   Status: {response.status_code}")
            assert response.status_code == 200
            
            print("   Streaming response: ", end="", flush=True)
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    chunks += 1
                    if chunks <= 3:  # Print first few chunks
                        print(".", end="", flush=True)
            
            print(f"\n   Received {chunks} chunks")
            print("   ✓ Streaming test passed")


async def main():
    """Run all integration tests"""
    print("=" * 60)
    print("Chat API Integration Tests")
    print("=" * 60)
    print("\nMake sure the server is running: python main.py")
    print("-" * 60)
    
    try:
        await test_health()
        await test_chat_message()
        await test_chat_with_history()
        await test_streaming()
        
        print("\n" + "=" * 60)
        print("✅ All integration tests passed!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
