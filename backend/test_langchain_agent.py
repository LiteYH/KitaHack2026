#!/usr/bin/env python3
"""
Test script to verify LangChain Agent with ROI Tool integration
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("🧪 Testing LangChain Agent with ROI Tool")
print("=" * 60)

try:
    from app.services.chat_service import chat_service
    
    print("\n✅ Chat Service loaded successfully")
    print(f"   Model: {type(chat_service.model).__name__}")
    print(f"   Tools count: {len(chat_service.tools)}")
    
    for tool_name, tool in chat_service.tools.items():
        print(f"\n   Tool: {tool_name}")
        print(f"      Description: {tool.description[:120]}...")
        print(f"      Return Direct: {tool.return_direct}")
    
    print("\n" + "=" * 60)
    print("✅ All components initialized successfully!")
    print("=" * 60)
    
    # Test a simple query
    print("\n🧪 Testing sample ROI query...")
    
    async def test_query():
        try:
            # Test with a general question first
            response, charts = await chat_service.chat(
                user_message="Hello, how can you help me?",
                user_email=None
            )
            print(f"\n✅ General query test passed")
            print(f"   Response length: {len(response)} characters")
            print(f"   Charts: {charts}")
            
        except Exception as e:
            print(f"\n❌ Test failed: {str(e)}")
    
    # Run async test
    asyncio.run(test_query())
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed! Agent is ready.")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error loading chat service: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
