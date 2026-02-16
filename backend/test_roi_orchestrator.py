"""
Test script for ROI Chatbot Orchestrator
Run this to verify the complete ROI analysis pipeline
"""

import asyncio
from app.services.roi_analysis_service import roi_analysis_service

async def test_roi_orchestrator():
    """Test the ROI orchestrator with sample queries"""
    
    # Replace with your test email (the one you used when populating ROI data)
    test_email = input("Enter your email (used in ROI data): ").strip()
    
    if not test_email:
        print("❌ Email is required")
        return
    
    print("\n" + "="*60)
    print("🧪 Testing ROI Chatbot Orchestrator")
    print("="*60)
    
    # Test 1: Detect ROI query
    test_queries = [
        "What is my ROI in the last 7 days?",
        "Show me my revenue breakdown",
        "How are my videos performing?",
        "What's my best performing video?",
        "Hello, how are you?"  # Non-ROI query
    ]
    
    print("\n📝 Test 1: ROI Query Detection")
    print("-" * 60)
    for query in test_queries:
        is_roi = roi_analysis_service.detect_roi_query(query)
        status = "✅" if is_roi else "❌"
        print(f"{status} '{query}' -> ROI Query: {is_roi}")
    
    # Test 2: Time period extraction
    print("\n📅 Test 2: Time Period Extraction")
    print("-" * 60)
    time_queries = [
        ("What is my ROI in the last 7 days?", 7),
        ("Show me performance for 30 days", 30),
        ("How did I do last week?", 7),
        ("What's my ROI last month?", 30),
    ]
    
    for query, expected in time_queries:
        days = roi_analysis_service.extract_time_period(query)
        status = "✅" if days == expected else "⚠️"
        print(f"{status} '{query}' -> {days} days (expected: {expected})")
    
    # Test 3: Full ROI processing
    print("\n🔍 Test 3: Full ROI Query Processing")
    print("-" * 60)
    
    test_query = "What is my ROI in the last 7 days?"
    print(f"Query: {test_query}")
    print(f"Email: {test_email}")
    print("\nProcessing...")
    
    try:
        text_summary, charts = await roi_analysis_service.process_roi_query(
            test_query, 
            test_email
        )
        
        print("\n✅ ROI Query Processed Successfully!")
        print("\n📊 Text Summary:")
        print("-" * 60)
        print(text_summary[:500] + "..." if len(text_summary) > 500 else text_summary)
        
        print("\n📈 Charts Generated:")
        print("-" * 60)
        if charts:
            for i, chart in enumerate(charts, 1):
                print(f"{i}. {chart['title']} ({chart['type']} chart)")
                print(f"   Data points: {len(chart['data'])}")
        else:
            print("No charts generated (might be no data for this period)")
        
    except Exception as e:
        print(f"\n❌ Error processing ROI query: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ Testing Complete!")
    print("="*60)
    print("\n💡 Next Steps:")
    print("1. Start the backend: uvicorn main:app --reload")
    print("2. Start the frontend: npm run dev")
    print("3. Go to the Chat page and ask ROI questions")
    print("   Example: 'What is my ROI in the last 7 days?'")
    print("\n")

if __name__ == "__main__":
    asyncio.run(test_roi_orchestrator())
