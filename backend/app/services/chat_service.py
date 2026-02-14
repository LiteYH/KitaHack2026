import os
from typing import List, Optional, AsyncGenerator, Dict, Any
import google.generativeai as genai
from app.core.config import settings
from app.schemas.chat import ChatMessage
from app.services.orchestrator_service import orchestrator_service


class ChatService:
    """Service for handling chat interactions with Google Gemini"""
    
    def __init__(self):
        """Initialize the Gemini API with API key"""
        # Get API key from settings (which loads from .env)
        api_key = settings.google_api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in .env file.")
        
        genai.configure(api_key=api_key)
        
        # Initialize the model - using gemini-2.0-flash-exp (latest experimental model)
        # Note: If you want to use gemini-1.5-flash or another model, change the model_name
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash-lite',  # or 'gemini-1.5-flash' for stable version
            system_instruction=self._get_system_instruction()
        )
    
    def _get_system_instruction(self) -> str:
        """Get the system instruction for the AI assistant"""
        return """You are BossolutionAI, an AI-powered marketing assistant designed specifically for SMEs (Small and Medium Enterprises). 

Your capabilities include:
- Content Creation: Generate engaging marketing content, social media posts, ad copy, and campaign ideas
- Competitor Analysis: Analyze competitors' marketing strategies and provide insights
- Campaign Optimization: Suggest improvements for marketing campaigns to maximize ROI
- Content Scheduling: Help with content planning and scheduling strategies
- Performance Analytics: Interpret marketing metrics and provide actionable recommendations
- Market Research: Provide insights on target audiences, trends, and market opportunities

Your personality:
- Professional yet friendly and approachable
- Focus on practical, actionable advice
- Use clear language, avoiding excessive jargon
- Be encouraging and supportive of SME growth
- Provide specific examples and suggestions when possible

IMPORTANT - Formatting Guidelines:
- ALWAYS format your responses using Markdown for better readability
- Use **bold text** for emphasis and important points
- Use bullet points (- or *) or numbered lists (1., 2., 3.) to organize information
- Break long paragraphs into shorter, digestible chunks (2-3 sentences max)
- Use headers (##, ###) to organize different sections of your response
- Add blank lines between sections for better spacing
- Use line breaks to avoid wall-of-text responses
- For lists of tips or steps, use numbered lists (1., 2., 3.)
- For features or benefits, use bullet points (-)
- Use > for important quotes or callouts
- Use `code` for technical terms or specific keywords

Example of good formatting:
## Campaign Strategy

Here's how I can help you:

1. **Target Audience Analysis**
   - Identify key demographics
   - Understand customer pain points

2. **Content Creation**
   - Generate engaging posts
   - Create platform-specific content

Let me know which area you'd like to focus on!

Always aim to:
1. Understand the user's specific needs and context
2. Provide tailored recommendations for SME budgets and resources
3. Offer step-by-step guidance when appropriate
4. Be concise yet comprehensive in your responses
5. Encourage data-driven decision making
6. FORMAT responses with proper spacing, headings, and lists for easy reading"""
    
    async def chat(
        self,
        user_message: str,
        conversation_history: Optional[List[ChatMessage]] = None,
        user_id: Optional[str] = None
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        """
        Send a message to Gemini and get a response with orchestration
        
        Args:
            user_message: The user's input message
            conversation_history: Previous messages for context
            user_id: Optional user ID for personalization and data fetching
            
        Returns:
            Tuple of (AI response text, campaign context dict or None)
        """
        try:
            # Step 1: Use orchestrator to analyze intent and fetch relevant data
            enriched_prompt, campaign_context = await orchestrator_service.orchestrate_response(
                user_message=user_message,
                user_id=user_id,
                conversation_history=conversation_history
            )
            
            # Step 2: Start a chat session
            chat_session = self.model.start_chat(history=[])
            
            # Step 3: Add conversation history if provided
            if conversation_history:
                # Convert history to Gemini format
                for msg in conversation_history:
                    if msg.role == "user":
                        chat_session.send_message(msg.content)
                    # Gemini handles assistant responses automatically in history
            
            # Step 4: Send the enriched message (with campaign context if available)
            response = chat_session.send_message(enriched_prompt)
            
            return response.text, campaign_context
            
        except Exception as e:
            print(f"Error in chat service: {str(e)}")
            raise Exception(f"Failed to get response from AI: {str(e)}")
    
    async def chat_stream(
        self,
        user_message: str,
        conversation_history: Optional[List[ChatMessage]] = None,
        user_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream responses from Gemini with orchestration
        
        Args:
            user_message: The user's input message
            conversation_history: Previous messages for context
            user_id: Optional user ID for personalization and data fetching
            
        Yields:
            Chunks of the AI assistant's response
        """
        try:
            # Step 1: Use orchestrator to analyze intent and fetch relevant data
            enriched_prompt, campaign_context = await orchestrator_service.orchestrate_response(
                user_message=user_message,
                user_id=user_id,
                conversation_history=conversation_history
            )
            
            # Step 2: Start a chat session
            chat_session = self.model.start_chat(history=[])
            
            # Step 3: Add conversation history if provided
            if conversation_history:
                for msg in conversation_history:
                    if msg.role == "user":
                        chat_session.send_message(msg.content)
            
            # Step 4: Stream the response using enriched prompt
            response = chat_session.send_message(enriched_prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            print(f"Error in chat stream service: {str(e)}")
            yield f"Error: {str(e)}"


# Singleton instance
chat_service = ChatService()
