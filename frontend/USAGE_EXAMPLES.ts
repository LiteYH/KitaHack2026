/**
 * Example: Using the Campaign-Aware Chatbot
 * 
 * This shows how the frontend can interact with the new orchestrator-based backend
 * that automatically fetches campaign data when users ask campaign-related questions.
 */

import { streamChatMessage, getCampaigns } from '@/lib/api';

// ============================================================================
// EXAMPLE 1: Simple Chat with Automatic Campaign Fetching
// ============================================================================

async function example1_SimpleCampaignChat(userId: string) {
  console.log('Example 1: User asks about campaign optimization');
  
  // User asks a campaign-related question
  // The backend will automatically:
  // 1. Detect that this is about campaigns
  // 2. Fetch the user's ongoing campaigns
  // 3. Calculate metrics (CTR, CVR, ROAS)
  // 4. Provide personalized recommendations
  
  let fullResponse = '';
  
  await streamChatMessage(
    {
      message: "How can I optimize my current ongoing campaigns?",
      user_id: userId
    },
    (chunk) => {
      fullResponse += chunk;
      console.log(chunk); // Stream to UI
    },
    () => {
      console.log('✅ Response complete!');
      console.log('Full response:', fullResponse);
    }
  );
}

// ============================================================================
// EXAMPLE 2: Platform-Specific Query
// ============================================================================

async function example2_PlatformSpecificQuery(userId: string) {
  console.log('Example 2: User asks about Instagram campaigns');
  
  // The orchestrator will detect "Instagram" and filter campaigns by platform
  await streamChatMessage(
    {
      message: "How are my Instagram campaigns performing?",
      user_id: userId
    },
    (chunk) => process.stdout.write(chunk),
    () => console.log('\n✅ Done!')
  );
}

// ============================================================================
// EXAMPLE 3: Status-Specific Query (Paused Campaigns)
// ============================================================================

async function example3_PausedCampaigns(userId: string) {
  console.log('Example 3: User asks about paused campaigns');
  
  // The orchestrator will detect "paused" status and filter accordingly
  await streamChatMessage(
    {
      message: "Show me the performance of my paused campaigns",
      user_id: userId
    },
    (chunk) => process.stdout.write(chunk),
    () => console.log('\n✅ Done!')
  );
}

// ============================================================================
// EXAMPLE 4: Direct Campaign API Access
// ============================================================================

async function example4_DirectCampaignAccess(userId: string) {
  console.log('Example 4: Directly fetch campaign data for dashboard');
  
  try {
    // Fetch all ongoing campaigns
    const response = await getCampaigns({
      user_id: userId,
      status: 'ongoing'
    });
    
    console.log(`Found ${response.total_count} ongoing campaigns`);
    console.log('Summary:', response.metrics_summary);
    
    // Display campaigns in your UI
    response.campaigns.forEach(campaign => {
      console.log(`- ${campaign.campaignName}: ${campaign.platform} (${campaign.status})`);
      console.log(`  Budget: $${campaign.totalBudget} | Spent: $${campaign.amountSpent}`);
    });
    
  } catch (error) {
    console.error('Failed to fetch campaigns:', error);
  }
}

// ============================================================================
// EXAMPLE 5: Conversation with Context
// ============================================================================

async function example5_ConversationWithContext(userId: string) {
  console.log('Example 5: Multi-turn conversation maintaining context');
  
  const conversationHistory: Array<{role: 'user' | 'assistant'; content: string}> = [];
  
  // First message
  console.log('\n👤 User: How are my campaigns doing?');
  let response1 = '';
  await streamChatMessage(
    {
      message: "How are my campaigns doing?",
      user_id: userId,
      conversation_history: conversationHistory
    },
    (chunk) => { response1 += chunk; },
    () => {
      console.log('🤖 Assistant:', response1);
      conversationHistory.push({ role: 'user', content: "How are my campaigns doing?" });
      conversationHistory.push({ role: 'assistant', content: response1 });
    }
  );
  
  // Follow-up question
  console.log('\n👤 User: Which one should I focus on improving?');
  let response2 = '';
  await streamChatMessage(
    {
      message: "Which one should I focus on improving?",
      user_id: userId,
      conversation_history: conversationHistory
    },
    (chunk) => { response2 += chunk; },
    () => {
      console.log('🤖 Assistant:', response2);
    }
  );
}

// ============================================================================
// EXAMPLE 6: React Component Example
// ============================================================================

export function ExampleChatComponent() {
  // This is how you'd use it in a React component
  
  const handleSendMessage = async (message: string, userId: string) => {
    let responseText = '';
    
    await streamChatMessage(
      {
        message,
        user_id: userId,
        conversation_history: [] // Pass your conversation history state
      },
      // onChunk callback
      (chunk) => {
        responseText += chunk;
        // Update UI with streaming text
        // setMessages(prev => [...prev, { role: 'assistant', content: responseText }])
      },
      // onComplete callback
      () => {
        console.log('Response complete:', responseText);
        // Final UI update if needed
      },
      // onError callback
      (error) => {
        console.error('Chat error:', error);
        // Show error to user
      }
    );
  };
  
  // Return your JSX...
  return null;
}

// ============================================================================
// TEST ALL EXAMPLES
// ============================================================================

async function runAllExamples() {
  const TEST_USER_ID = "DT4DNex2L1N2rZ9kPddEzqougK22";
  
  console.log('🧪 Running all examples...\n');
  
  await example1_SimpleCampaignChat(TEST_USER_ID);
  console.log('\n' + '='.repeat(80) + '\n');
  
  await example2_PlatformSpecificQuery(TEST_USER_ID);
  console.log('\n' + '='.repeat(80) + '\n');
  
  await example3_PausedCampaigns(TEST_USER_ID);
  console.log('\n' + '='.repeat(80) + '\n');
  
  await example4_DirectCampaignAccess(TEST_USER_ID);
  console.log('\n' + '='.repeat(80) + '\n');
  
  await example5_ConversationWithContext(TEST_USER_ID);
  
  console.log('\n✅ All examples completed!');
}

// Uncomment to run:
// runAllExamples();

// ============================================================================
// KEY TAKEAWAYS
// ============================================================================

/*
1. ✅ NO CHANGES NEEDED in your current chat UI
   - The backend automatically detects campaign queries
   - Just pass user_id in the ChatRequest

2. ✅ Queries are automatically enhanced with campaign data
   - "optimize my campaigns" → fetches ongoing campaigns
   - "my paused campaigns" → filters by status="paused"
   - "Instagram campaigns" → filters by platform="Instagram"

3. ✅ AI receives full context automatically
   - Campaign performance metrics
   - CTR, CVR, ROAS calculations
   - Budget utilization data

4. ✅ Optional: Use Campaign API directly for dashboards
   - getCampaigns() for campaign lists
   - getCampaignById() for specific campaign
   - getCampaignMetrics() for calculated metrics

5. ✅ Works with conversation history
   - Pass previous messages for context
   - Follow-up questions work naturally
*/
