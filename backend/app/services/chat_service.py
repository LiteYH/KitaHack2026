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
        user_email: Optional[str] = None
    ) -> Tuple[str, Optional[List[Dict[str, Any]]]]:
        """
        Send a message to Gemini and get a response using LangChain Agent
        The Agent automatically decides when to use the ROI Analysis Tool
        
        Args:
            user_message: The user's input message
            conversation_history: Previous messages for context
            user_id: Optional user ID for personalization
            user_email: Optional user email for ROI data access
            
        Returns:
            Tuple of (AI assistant's response, optional chart configurations)
        """
        try:
            charts = None
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # LANGCHAIN AGENT ORCHESTRATION - Automatic Tool Selection
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            print(f"🎯 [ORCHESTRATOR] Processing user query with LangChain Agent")
            print(f"   ↳ Query: {user_message}")
            
            # Build chat history for the agent
            chat_history = []
            if conversation_history:
                for msg in conversation_history:
                    if msg.role == "user":
                        chat_history.append(HumanMessage(content=msg.content))
                    elif msg.role == "assistant":
                        chat_history.append(AIMessage(content=msg.content))
            
            # Prepare input for the agent
            # If user_email is provided, include it in the context
            if user_email:
                agent_input = {
                    "input": user_message,
                    "chat_history": chat_history,
                    "user_email": user_email  # Pass user email for ROI tool
                }
                print(f"   ↳ User email available: {user_email}")
                print(f"   ↳ Agent will decide if ROI tool is needed")
            else:
                agent_input = {
                    "input": user_message,
                    "chat_history": chat_history
                }
                print(f"   ↳ No user email - ROI tool unavailable")
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Invoke the Agent - AI decides which tool to use (if any)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            # Check if this is an ROI query and we have user email
            if user_email:
                from app.services.roi_analysis_service import roi_analysis_service
                
                if roi_analysis_service.detect_roi_query(user_message):
                    print(f"🎯 [ORCHESTRATOR] ROI query detected - invoking ROI tool directly")
                    
                    # Use the ROI tool directly for better control
                    tool_result = await roi_analysis_tool._arun(
                        user_message=user_message,
                        user_email=user_email
                    )
                    
                    # Parse the tool result
                    result_data = json.loads(tool_result)
                    
                    if result_data.get("success"):
                        response_text = result_data.get("analysis", "")
                        charts = result_data.get("charts", [])
                        print(f"✅ [ORCHESTRATOR] ROI tool executed successfully")
                        return response_text, charts
                    else:
                        # Tool failed, fall back to general AI
                        error_msg = result_data.get("error", "Unknown error")
                        print(f"⚠️ [ORCHESTRATOR] ROI tool failed: {error_msg}")
                        # Continue to general AI response below
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
            print(f"✅ [ORCHESTRATOR] Standard AI response generated")
            
            return response.content, None
            
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
            user_id: Optional user ID for personalization
            
        Yields:
            Chunks of the AI assistant's response
        """
        try:
            # Build LangChain message history
            messages: List[BaseMessage] = [self.system_message]
            
            # Add conversation history if provided
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
