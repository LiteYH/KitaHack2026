"""
Test script to verify the orchestrator and campaign fetching functionality
"""

import asyncio
from app.services.orchestrator_service import orchestrator_service
from app.services.campaign_service import campaign_service
from app.core.firebase import initialize_firebase

# Test user ID (from your seeded data)
TEST_USER_ID = "DT4DNex2L1N2rZ9kPddEzqougK22"


async def test_orchestrator():
    """Test the orchestrator with different queries"""
    
    print("=" * 80)
    print("🧪 TESTING ORCHESTRATOR & CAMPAIGN INTEGRATION")
    print("=" * 80)
    
    # Initialize Firebase
    initialize_firebase()
    
    # Test queries
    test_queries = [
        "How can I optimize my current ongoing campaigns?",
        "Show me my paused campaigns performance",
        "What's my Instagram campaign doing?",
        "Currently how many campaigns are ongoing? And how many campaigns are paused?",
        "Tell me about AI in marketing",  # This shouldn't fetch campaigns
        "Analyze my competitors' marketing strategies",  # This shouldn't fetch campaigns
        "Which campaigns are running on Facebook?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {query}")
        print(f"{'='*80}\n")
        
        # Analyze intent
        intent = orchestrator_service.analyze_intent(query)
        print(f"📊 Intent Analysis:")
        print(f"   Needs Campaign Data: {intent['needs_campaign_data']}")
        print(f"   Status Filter: {intent['status_filter']}")
        print(f"   Platform Filter: {intent['platform_filter']}")
        print(f"   Intent Type: {intent['intent_type']}")
        print(f"   Is Simple Query: {intent.get('is_simple_query', False)}")
        
        # Fetch campaigns if needed
        if intent['needs_campaign_data']:
            campaigns, metrics, summary = await orchestrator_service.get_relevant_campaigns(
                user_id=TEST_USER_ID,
                intent=intent
            )
            
            print(f"\n📈 Fetched {len(campaigns)} campaign(s)")
            
            if campaigns:
                print(f"\n🎯 Campaign Summary:")
                print(f"   Total Budget: ${summary.get('total_budget', 0):,}")
                print(f"   Total Spent: ${summary.get('total_spent', 0):,}")
                print(f"   Overall ROAS: {summary.get('overall_roas', 0)}x")
                print(f"   Overall CTR: {summary.get('overall_ctr', 0)}%")
                
                print(f"\n📋 Campaigns Found:")
                for campaign in campaigns[:3]:  # Show first 3
                    print(f"   • {campaign.campaignName} ({campaign.status}) - {campaign.platform}")
            
            # Build enriched prompt
            enriched_prompt = orchestrator_service.build_context_prompt(
                user_message=query,
                campaigns=campaigns,
                metrics=metrics,
                summary=summary,
                intent=intent
            )
            
            print(f"\n✨ Enriched Prompt Length: {len(enriched_prompt)} characters")
            print(f"   (Original: {len(query)} characters)")
        else:
            print(f"\n💬 No campaign data needed - will respond generally")
    
    print(f"\n{'='*80}")
    print("✅ ALL TESTS COMPLETED!")
    print(f"{'='*80}\n")


async def test_campaign_service():
    """Test the campaign service directly"""
    
    print("\n" + "=" * 80)
    print("🧪 TESTING CAMPAIGN SERVICE DIRECTLY")
    print("=" * 80 + "\n")
    
    # Initialize Firebase
    initialize_firebase()
    
    # Test 1: Get all campaigns
    print("Test 1: Fetching all campaigns...")
    campaigns, metrics = await campaign_service.get_campaigns_with_metrics(
        user_id=TEST_USER_ID
    )
    print(f"✅ Found {len(campaigns)} total campaigns\n")
    
    # Test 2: Get only ongoing campaigns
    print("Test 2: Fetching ongoing campaigns...")
    ongoing_campaigns, ongoing_metrics = await campaign_service.get_campaigns_with_metrics(
        user_id=TEST_USER_ID,
        status="ongoing"
    )
    print(f"✅ Found {len(ongoing_campaigns)} ongoing campaigns\n")
    
    # Test 3: Get Instagram campaigns
    print("Test 3: Fetching Instagram campaigns...")
    ig_campaigns, ig_metrics = await campaign_service.get_campaigns_with_metrics(
        user_id=TEST_USER_ID,
        platform="Instagram"
    )
    print(f"✅ Found {len(ig_campaigns)} Instagram campaigns\n")
    
    # Test 4: Calculate metrics summary
    print("Test 4: Generating metrics summary...")
    summary = campaign_service.generate_metrics_summary(campaigns, metrics)
    print(f"✅ Summary generated:")
    print(f"   Total Budget: ${summary.get('total_budget', 0):,}")
    print(f"   Total Spent: ${summary.get('total_spent', 0):,}")
    print(f"   Overall ROAS: {summary.get('overall_roas', 0)}x")
    print(f"   Average CTR: {summary.get('average_ctr', 0)}%")
    
    print("\n" + "=" * 80)
    print("✅ CAMPAIGN SERVICE TESTS COMPLETED!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    print("\n🚀 Starting Tests...\n")
    
    # Run campaign service tests
    asyncio.run(test_campaign_service())
    
    # Run orchestrator tests
    asyncio.run(test_orchestrator())
    
    print("\n🎉 All tests completed successfully!\n")
