"""
Quick test script for the chat API endpoints
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.chat_service import chat_service
from app.schemas.chat import ChatMessage


async def test_chat_service():
    """Test the chat service directly"""
    print("=" * 50)
    print("Testing Chat Service")
    print("=" * 50)
    
    try:
        # Test simple message
        print("\n1. Testing simple message...")
        response = await chat_service.chat(
            user_message="Hello! What can you help me with?"
        )
        print(f"✓ Response received: {response[:100]}...")
        
        # Test with conversation history
        print("\n2. Testing with conversation history...")
        history = [
            ChatMessage(role="user", content="I run a small coffee shop"),
            ChatMessage(role="assistant", content="Great! I can help you with marketing strategies for your coffee shop.")
        ]
        response = await chat_service.chat(
            user_message="How can I increase my social media engagement?",
            conversation_history=history
        )
        print(f"✓ Response received: {response[:100]}...")
        
        print("\n" + "=" * 50)
        print("✓ All tests passed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_streaming():
    """Test streaming responses"""
    print("\n" + "=" * 50)
    print("Testing Streaming")
    print("=" * 50)
    
    try:
        print("\nStreaming response for: 'Give me 3 marketing tips'")
        print("-" * 50)
        
        async for chunk in chat_service.chat_stream(
            user_message="Give me 3 quick marketing tips for a small business"
        ):
            print(chunk, end="", flush=True)
        
        print("\n" + "-" * 50)
        print("✓ Streaming test passed!")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests"""
    print("\n🚀 Starting Chat Service Tests\n")
    
    # Test basic chat
    await test_chat_service()
    
    # Test streaming
    await test_streaming()
    
    print("\n✅ All tests completed!\n")


if __name__ == "__main__":
    asyncio.run(main())
