#!/usr/bin/env python3
"""
Test script to verify ROI Tool with AI Analysis Flow:
1. User asks ROI question
2. Orchestrator calls ROI tool
3. Tool fetches data from Firebase
4. Data passed to AI for analysis
5. AI generates insights
6. Returns analysis + charts
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("🧪 Testing ROI Tool with AI Analysis Flow")
print("=" * 70)

try:
    from app.services.chat_service import chat_service
    
    print("\n✅ Chat Service loaded")
    print(f"   Model: {type(chat_service.model).__name__}")
    print(f"   Tools: {list(chat_service.tools.keys())}")
    
    # Check if ROI tool has model set
    roi_tool = chat_service.tools.get("roi_analysis")
    if roi_tool and roi_tool.model:
        print(f"   ROI Tool has AI model: ✅")
    else:
        print(f"   ROI Tool has AI model: ❌")
    
    print("\n" + "=" * 70)
    print("🧪 Test 1: ROI Query with Mock Email")
    print("=" * 70)
    
    async def test_roi_query():
        """Test ROI query flow"""
        
        # Test with a realistic ROI question using real user email
        test_email = "limjl0130@gmail.com"
        test_query = "What is my ROI for the last 7 days?"
        
        print(f"\n📝 Query: '{test_query}'")
        print(f"👤 User: {test_email}")
        print(f"\n{'─' * 70}")
        print("Processing...")
        print(f"{'─' * 70}\n")
        
        try:
            response, charts = await chat_service.chat(
                user_message=test_query,
                user_email=test_email
            )
            
            print(f"\n{'═' * 70}")
            print("📊 RESPONSE:")
            print(f"{'═' * 70}")
            print(response)
            
            print(f"\n{'═' * 70}")
            print(f"📈 CHARTS: {len(charts) if charts else 0} generated")
            print(f"{'═' * 70}")
            
            if charts:
                for i, chart in enumerate(charts, 1):
                    print(f"\n   Chart {i}: {chart.get('type', 'unknown')} - {chart.get('title', 'Untitled')}")
            
            print(f"\n{'═' * 70}")
            print("✅ Test 1 PASSED: ROI query processed successfully")
            print(f"{'═' * 70}")
            
        except Exception as e:
            print(f"\n❌ Test 1 FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🧪 Test 2: General Query (non-ROI)")
    print("=" * 70)
    
    async def test_general_query():
        """Test general query that should NOT use ROI tool"""
        
        test_query = "What features do you offer?"
        
        print(f"\n📝 Query: '{test_query}'")
        print(f"\n{'─' * 70}")
        print("Processing...")
        print(f"{'─' * 70}\n")
        
        try:
            response, charts = await chat_service.chat(
                user_message=test_query,
                user_email=None
            )
            
            print(f"\n{'═' * 70}")
            print("💬 RESPONSE:")
            print(f"{'═' * 70}")
            print(response[:500] + "..." if len(response) > 500 else response)
            
            print(f"\n{'═' * 70}")
            if charts:
                print(f"⚠️  Test 2 PARTIAL: General query returned charts (unexpected)")
            else:
                print(f"✅ Test 2 PASSED: General query processed without charts")
            print(f"{'═' * 70}")
            
        except Exception as e:
            print(f"\n❌ Test 2 FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Run tests
    print("\nStarting tests...\n")
    asyncio.run(test_roi_query())
    print("\n")
    asyncio.run(test_general_query())
    
    print("\n" + "=" * 70)
    print("🎉 All tests completed!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
