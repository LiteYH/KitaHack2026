import os
import json
from typing import List, Optional, AsyncGenerator, Tuple, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from app.core.config import settings
from app.schemas.chat import ChatMessage
from app.services.roi_tool import roi_analysis_tool


class ChatService:
    """Service for handling chat interactions with Google Gemini using LangChain"""
    
    def __init__(self):
        """Initialize the LangChain Gemini model and ROI Analysis Tool"""
        # Get API key from settings (which loads from .env)
        api_key = settings.google_api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in .env file.")
        
        # Initialize LangChain ChatGoogleGenerativeAI model
        # Using gemini-2.5-flash-lite for fast, cost-effective responses
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=api_key,
            temperature=0.7,  # Balanced creativity and consistency
            max_output_tokens=2048,  # Reasonable response length
            convert_system_message_to_human=True  # Required for Gemini system messages
        )
        
        # Store system instruction as a reusable message
        self.system_message = SystemMessage(content=self._get_system_instruction())
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # LANGCHAIN TOOLS SETUP - Available tools for orchestrator
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        # Pass AI model to ROI tool for generating insights
        roi_analysis_tool.set_model(self.model)
        
        # Register available LangChain tools
        self.tools = {
            "roi_analysis": roi_analysis_tool
        }
        
        print("✅ [ORCHESTRATOR] LangChain service initialized with ROI Analysis Tool")
        print(f"   Available tools: {list(self.tools.keys())}")
    
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
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        confirmation_response: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Optional[List[Dict[str, Any]]], bool, Optional[Dict[str, Any]]]:
        """
        Send a message to Gemini and get a response using LangChain Agent
        Supports Human-in-the-Loop (HITL) confirmation for sensitive data access
        
        Args:
            user_message: The user's input message
            conversation_history: Previous messages for context
            user_id: Optional user ID for personalization
            user_email: Optional user email for ROI data access
            confirmation_response: User's response to a pending confirmation request
            
        Returns:
            Tuple of (response_text, charts, requires_confirmation, confirmation_request)
        """
        try:
            charts = None
            requires_confirmation = False
            confirmation_request = None
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # HITL: Handle confirmation response (user confirmed/denied)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            if confirmation_response:
                action_id = confirmation_response.get("action_id")
                confirmed = confirmation_response.get("confirmed", False)
                
                print(f"🔐 [HITL] Processing confirmation response: action_id={action_id}, confirmed={confirmed}")
                
                if not confirmed:
                    # User denied the request
                    print(f"❌ [HITL] User denied data access request")
                    return (
                        "I understand. I won't access your ROI data. Feel free to ask me anything else about marketing strategies, content creation, or general business advice! 😊",
                        None,
                        False,
                        None
                    )
                
                # User confirmed - process the ROI query
                print(f"✅ [HITL] User confirmed - processing ROI analysis")
                
                from app.services.roi_analysis_service import roi_analysis_service
                
                # Process the confirmed action
                analysis_data, charts = await roi_analysis_service.process_confirmed_roi_query(action_id)
                
                if not analysis_data.get("found_data"):
                    error_msg = analysis_data.get("error", "No ROI data found")
                    return (
                        f"⚠️ {error_msg}\n\nPlease make sure you have uploaded video performance data to get insights.",
                        None,
                        False,
                        None
                    )
                
                # Generate AI insights from the data
                system_prompt = """You are a data analyst expert specializing in YouTube content ROI analysis.
Your task is to analyze the provided ROI data and generate insightful, actionable recommendations.

Guidelines:
- Provide a clear, conversational summary of the key findings
- Highlight strengths and areas for improvement
- Use emojis appropriately (📊, 💰, 🎯, ✅, ⚠️, 📈)
- Focus on actionable insights
- Keep the tone professional but friendly
- Structure your response with markdown formatting
- Reference specific numbers to support your analysis"""

                user_prompt = f"""User Question: {analysis_data.get('user_query', user_message)}

{analysis_data.get('data_summary', '')}

Please provide an insightful analysis of this ROI data, directly addressing the user's question. Include:
1. A brief overview of overall performance
2. Key insights and patterns
3. Actionable recommendations
4. Mention that visualizations are provided below"""

                ai_messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt)
                ]
                
                # Invoke AI model
                ai_response = await self.model.ainvoke(ai_messages)
                response_text = ai_response.content
                
                print(f"✅ [HITL] Analysis complete with {len(charts)} charts")
                
                return response_text, charts, False, None
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # LANGCHAIN AGENT ORCHESTRATION - Automatic Tool Selection
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            print(f"🎯 [ORCHESTRATOR] Processing user query with LangChain Agent")
            print(f"   ↳ Query: {user_message}")
            
            # Check if this is an ROI query and we have user email
            if user_email:
                from app.services.roi_analysis_service import roi_analysis_service
                
                if roi_analysis_service.detect_roi_query(user_message):
                    print(f"🔒 [ORCHESTRATOR] ROI query detected - initiating HITL confirmation")
                    
                    # Request confirmation before accessing data
                    analysis_data, charts, confirmation_req = await roi_analysis_service.process_roi_query(
                        user_message=user_message,
                        user_email=user_email,
                        skip_confirmation=False  # Require confirmation
                    )
                    
                    if confirmation_req:
                        # Need user confirmation
                        print(f"⏸️ [ORCHESTRATOR] Waiting for user confirmation")
                        return (
                            confirmation_req["message"],
                            None,
                            True,
                            confirmation_req
                        )
                else:
                    print(f"🎯 [ORCHESTRATOR] General query - using standard AI response")
            else:
                print(f"🎯 [ORCHESTRATOR] No user email - using standard AI response")
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Fall back to standard AI response (no tools needed)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            messages: List[BaseMessage] = [self.system_message]
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history:
                    if msg.role == "user":
                        messages.append(HumanMessage(content=msg.content))
                    elif msg.role == "assistant":
                        messages.append(AIMessage(content=msg.content))
            
            # Add current message
            messages.append(HumanMessage(content=user_message))
            
            # Invoke the model
            response = await self.model.ainvoke(messages)
            print(f"\u2705 [ORCHESTRATOR] Standard AI response generated")
            
            return response.content, None, False, None
            
        except Exception as e:
            print(f"❌ [ORCHESTRATOR ERROR] {str(e)}")
            raise Exception(f"Failed to get response from AI: {str(e)}")
    
    async def chat_stream(
        self,
        user_message: str,
        conversation_history: Optional[List[ChatMessage]] = None,
        user_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream responses from Gemini using LangChain
        
        Args:
            user_message: The user's input message
            conversation_history: Previous messages for context
            user_id: Optional user ID for personalization and data fetching
            
        Yields:
            Chunks of the AI assistant's response
        """
        try:
            # Build LangChain message history
            messages: List[BaseMessage] = [self.system_message]
            
            # Step 3: Add conversation history if provided
            if conversation_history:
                for msg in conversation_history:
                    if msg.role == "user":
                        messages.append(HumanMessage(content=msg.content))
                    elif msg.role == "assistant":
                        messages.append(AIMessage(content=msg.content))
            
            # Add the current user message
            messages.append(HumanMessage(content=user_message))
            
            # Stream the response using LangChain's async streaming
            async for chunk in self.model.astream(messages):
                if chunk.content:
                    yield chunk.content
                    
        except Exception as e:
            print(f"Error in chat stream service: {str(e)}")
            yield f"Error: {str(e)}"


# Singleton instance
chat_service = ChatService()
