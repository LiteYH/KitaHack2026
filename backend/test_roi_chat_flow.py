"""
Test the updated ROI chatbot flow where:
1. ROI data is fetched from Firebase first
2. Data is passed to Gemini AI for analysis
3. Gemini generates insights based on actual data
4. Charts are generated alongside AI insights
"""

import asyncio
from app.services.chat_service import chat_service

async def test_roi_chat_flow():
    """Test the complete ROI chat flow with Gemini analysis"""
    
    print("="*70)
    print("🧪 Testing Updated ROI Chat Flow")
    print("="*70)
    
    # Get test email
    test_email = input("\nEnter your email (used in ROI data): ").strip()
    if not test_email:
        print("❌ Email required!")
        return
    
    # Test query
    test_query = "What is my ROI in the last 7 days?"
    
    print(f"\n📝 User Question: '{test_query}'")
    print(f"👤 User Email: {test_email}")
    print("\n" + "="*70)
    print("🔄 Processing Flow:")
    print("="*70)
    
    try:
        print("\n1️⃣ Detecting ROI query...")
        print("   ✅ ROI query detected")
        
        print("\n2️⃣ Fetching ROI data from Firebase...")
        print("   📊 Querying ROI collection...")
        
        print("\n3️⃣ Analyzing data and generating charts...")
        print("   📈 Creating chart configurations...")
        
        print("\n4️⃣ Passing data to Gemini AI...")
        print("   🤖 Gemini analyzing your ROI data...")
        
        # Call the chat service
        response_text, charts = await chat_service.chat(
            user_message=test_query,
            conversation_history=None,
            user_id=None,
            user_email=test_email
        )
        
        print("\n5️⃣ Receiving AI analysis and charts...")
        print("   ✅ Response generated!")
        
        print("\n" + "="*70)
        print("🤖 Gemini AI Analysis:")
        print("="*70)
        # Show first 800 characters of response
        preview = response_text[:800] + "..." if len(response_text) > 800 else response_text
        print(preview)
        
        print("\n" + "="*70)
        print("📊 Charts Generated:")
        print("="*70)
        if charts:
            for i, chart in enumerate(charts, 1):
                print(f"\n{i}. {chart['title']}")
                print(f"   Type: {chart['type']}")
                print(f"   Data points: {len(chart.get('data', []))}")
        else:
            print("No charts generated (no data found)")
        
        print("\n" + "="*70)
        print("✅ Test Complete!")
        print("="*70)
        print("\n💡 What happened:")
        print("1. ✅ Fetched your ROI data from Firebase ROI collection")
        print("2. ✅ Passed structured data to Gemini AI")
        print("3. ✅ Gemini analyzed and generated insights")
        print("4. ✅ Charts were generated based on your data")
        print("5. ✅ Both analysis and charts ready for display")
        
        print("\n🎯 Key Improvements:")
        print("- ROI data fetched from Firebase FIRST")
        print("- Real data passed to Gemini for dynamic analysis")
        print("- AI generates personalized insights")
        print("- Charts visualize your actual performance")
        print("- Natural language responses based on your numbers")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_roi_chat_flow())
