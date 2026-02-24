"""
Quick test script for image generation tool
Run this to verify Imagen 4.0 integration works
"""

import asyncio
from app.services.agents.content_agent import ContentAgent


async def test_image_generation():
    """Test the complete image generation workflow"""
    
    agent = ContentAgent()
    
    print("=" * 60)
    print("🧪 Testing Image Generation Feature")
    print("=" * 60)
    
    # Test 1: Content generation with image keyword
    print("\n📝 Test 1: Content with image request")
    print("-" * 60)
    response1 = await agent.run("Create an Instagram post about coffee with an image")
    print(response1)
    
    print("\n" + "=" * 60)
    print("\n⏸️  Waiting for user confirmation simulation...")
    print("-" * 60)
    
    # Test 2: Confirm image generation
    print("\n🎨 Test 2: Confirming image generation")
    print("-" * 60)
    response2 = await agent.run("yes, generate for instagram")
    print(response2)
    
    print("\n" + "=" * 60)
    print("✅ Tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_image_generation())
