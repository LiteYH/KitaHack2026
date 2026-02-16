import os
from typing import List, Optional, AsyncGenerator, Tuple, Dict, Any
import google.generativeai as genai
from app.core.config import settings
from app.schemas.chat import ChatMessage


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
        user_id: Optional[str] = None,
        user_email: Optional[str] = None
    ) -> Tuple[str, Optional[List[Dict[str, Any]]]]:
        """
        Send a message to Gemini and get a response, with ROI analysis integration
        
        Args:
            user_message: The user's input message
            conversation_history: Previous messages for context
            user_id: Optional user ID for personalization
            user_email: Optional user email for ROI data access
            
        Returns:
            Tuple of (AI assistant's response, optional chart configurations)
        """
        try:
            # Check if this is an ROI-related query
            charts = None
            enhanced_message = user_message
            
            if user_email:
                from app.services.roi_analysis_service import roi_analysis_service
                
                if roi_analysis_service.detect_roi_query(user_message):
                    # Step 1: Fetch ROI data from Firebase
                    days = roi_analysis_service.extract_time_period(user_message)
                    videos = await roi_analysis_service.fetch_user_roi_data(user_email, days)
                    
                    if videos:
                        # Step 2: Analyze the data and generate charts
                        analysis = roi_analysis_service.analyze_roi_data(videos)
                        charts = roi_analysis_service.generate_chart_config(analysis)
                        
                        # Step 3: Prepare ROI data context for Gemini
                        summary = analysis.get("summary", {})
                        best_video = analysis.get("best_video", {})
                        categories = analysis.get("categories", {})
                        
                        # Create structured data context for Gemini to analyze
                        period_text = f"the last {days} days" if days else "all time"
                        
                        roi_data_context = f"""
The user has asked about their ROI performance. Here is their actual data from Firebase:

**Time Period:** {period_text}

**Overall Metrics:**
- Total Videos: {summary.get('total_videos', 0)}
- Total Views: {summary.get('total_views', 0):,}
- Total Revenue: ${summary.get('total_revenue', 0):,.2f}
- Total Cost: ${summary.get('total_cost', 0):,.2f}
- Net Profit: ${summary.get('total_profit', 0):,.2f}
- Overall ROI: {summary.get('overall_roi', 0):.2f}%

**Revenue Breakdown:**
- Ad Revenue: ${summary.get('ad_revenue', 0):,.2f}
- Sponsorship Revenue: ${summary.get('sponsorship_revenue', 0):,.2f}
- Affiliate Revenue: ${summary.get('affiliate_revenue', 0):,.2f}

**Best Performing Video:**
- Title: {best_video.get('title', 'N/A')}
- ROI: {best_video.get('roi', 0):.2f}%
- Revenue: ${best_video.get('revenue', 0):,.2f}
- Views: {best_video.get('views', 0):,}

**Category Performance:**
"""
                        for category, stats in categories.items():
                            roi_data_context += f"- {category}: Avg ROI {stats['avg_roi']:.2f}%, {stats['count']} videos, ${stats['profit']:.2f} profit\n"
                        
                        roi_data_context += f"""
**Engagement Metrics:**
- Total Likes: {summary.get('total_likes', 0):,}
- Total Comments: {summary.get('total_comments', 0):,}
- Average Retention Rate: {summary.get('avg_retention', 0):.2f}%

Based on this data, please analyze and answer the user's question: "{user_message}"

Provide insights, recommendations, and actionable advice. Use markdown formatting with headers, bullet points, and emphasis for readability. Be specific and reference the actual numbers from their data.
"""
                        enhanced_message = roi_data_context
                    else:
                        # No data found
                        enhanced_message = f"""The user asked: "{user_message}"

However, there is no ROI data found in the Firebase database for this user for the specified period. 

Please inform them politely that:
1. No ROI data was found for their account
2. They may need to upload their video performance data first
3. Suggest they check the ROI dashboard or contact support if they believe this is an error

Keep the response friendly and helpful."""
            
            # Start a chat session
            chat_session = self.model.start_chat(history=[])
            
            # Add conversation history if provided
            if conversation_history:
                # Convert history to Gemini format
                for msg in conversation_history:
                    if msg.role == "user":
                        chat_session.send_message(msg.content)
                    # Gemini handles assistant responses automatically in history
            
            # Send the current message (with ROI context if applicable)
            response = chat_session.send_message(enhanced_message)
            
            return response.text, charts
            
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
        Stream responses from Gemini
        
        Args:
            user_message: The user's input message
            conversation_history: Previous messages for context
            user_id: Optional user ID for personalization
            
        Yields:
            Chunks of the AI assistant's response
        """
        try:
            # Start a chat session
            chat_session = self.model.start_chat(history=[])
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history:
                    if msg.role == "user":
                        chat_session.send_message(msg.content)
            
            # Stream the response
            response = chat_session.send_message(user_message, stream=True)
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            print(f"Error in chat stream service: {str(e)}")
            yield f"Error: {str(e)}"


# Singleton instance
chat_service = ChatService()
