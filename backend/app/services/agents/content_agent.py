from typing import List, Optional
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage

from app.core.config import settings
from app.services.tools.content_tool import generate_content
from app.services.tools.image_tool import generate_social_image, should_generate_image


class ContentAgent:
    """
    Modern LangChain 1.0+ SME Marketing Assistant with image generation support.
    
    Features:
    - RAG-powered content generation
    - Imagen 4.0 image generation
    - Intelligent keyword detection
    - User confirmation flow for images
    """

    def __init__(self):
        api_key = settings.google_api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found.")

        # LLM with system instruction
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=api_key,
            temperature=0.7,
        )

        # Modern LangChain 1.0+ tool binding - bind both tools
        self.llm_with_tools = self.llm.bind_tools([generate_content, generate_social_image])
        
        # Chat history storage
        self.chat_history: List[BaseMessage] = []
        
        # Track if we offered image generation in last response
        self.awaiting_image_confirmation: bool = False
        
        # System message
        self.system_message = SystemMessage(content="""You are BossolutionAI, an AI-powered marketing assistant for SMEs.

Your capabilities:
- Generate high-performing social media content using data-driven insights
- Create AI-generated images for posts using Google Imagen 4.0
- Provide scheduling recommendations based on engagement analysis
- Format responses professionally in Markdown

When users request content generation, use the generate_content tool to access RAG examples and create optimized posts.
When users mention images/visuals/graphics, offer to generate custom images using generate_social_image tool.""")

    async def run(self, user_message: str) -> str:
        """
        Run the agent with the user's message.
        
        Args:
            user_message: User's input message
            
        Returns:
            str: AI response with optional image generation
        """
        # Detection keywords
        content_keywords = ['write', 'create', 'generate', 'post', 'caption', 'draft']
        confirmation_keywords = ['yes', 'sure', 'ok', 'confirm', 'proceed', 'go ahead']
        wants_image = should_generate_image(user_message)
        wants_content = any(kw in user_message.lower() for kw in content_keywords)
        is_confirming = any(kw in user_message.lower() for kw in confirmation_keywords)
        
        # CASE 1: User is confirming image generation (PRIORITY CHECK)
        # Check if we're awaiting confirmation OR if they explicitly mention image with confirmation
        if (self.awaiting_image_confirmation and is_confirming) or (wants_image and is_confirming and len(self.chat_history) > 0):
            # Extract platform if mentioned
            platform = self._extract_platform(user_message)
            
            # Get the last generated content from history
            last_content = self._get_last_content_from_history()
            
            if not last_content:
                return "⚠️ I need some content first! Please describe what you'd like to create, and I'll generate both content and image."
            
            # Generate image using the tool
            # Use first 500 chars of content as image prompt
            image_prompt = last_content[:500] if len(last_content) > 500 else last_content
            
            # Invoke the image generation tool
            tool_input = {"prompt": image_prompt, "platform": platform}
            result = generate_social_image.invoke(tool_input)
            
            # Reset the flag
            self.awaiting_image_confirmation = False
            
            return result
        
        # CASE 2: User wants content (with potential image)
        elif wants_content:
            # Generate content using RAG tool
            tool_input = {"user_input": user_message}
            examples_context = generate_content.invoke(tool_input)
            
            # Let LLM create final post using examples
            messages = [
                SystemMessage(content="You are a marketing expert. Use the examples below to create an engaging social media post."),
                HumanMessage(content=f"{examples_context}\n\nCreate the final post now.")
            ]
            
            response = await self.llm.ainvoke(messages)
            content_response = response.content
            
            # Update chat history
            self.chat_history.append(HumanMessage(content=user_message))
            self.chat_history.append(AIMessage(content=content_response))
            
            # CASE 1A: User also wants an image
            if wants_image:
                image_offer = "\n\n---\n\n🎨 **Image Generation Available!**\n\n"
                image_offer += "Would you like me to generate a custom image for this post? "
                image_offer += "Just reply with:\n"
                image_offer += "- `yes` or `generate image`\n"
                image_offer += "- Specify platform: `generate for instagram` or `create facebook image`\n\n"
                image_offer += "*Powered by Google Imagen 4.0*"
                
                # Set flag to expect confirmation
                self.awaiting_image_confirmation = True
                
                return content_response + image_offer
            
            # Reset flag if no image offered
            self.awaiting_image_confirmation = False
            return content_response
            
            
            return content_response
        
        # CASE 3: Normal conversation
        else:
            messages = [self.system_message] + self.chat_history + [HumanMessage(content=user_message)]
            
            response = await self.llm.ainvoke(messages)
            
            # Update chat history
            self.chat_history.append(HumanMessage(content=user_message))
            self.chat_history.append(AIMessage(content=response.content))
            
            return response.content

    def _extract_platform(self, user_message: str) -> str:
        """
        Extract platform name from user message.
        
        Args:
            user_message: User's input
            
        Returns:
            str: Platform name (default: instagram)
        """
        platforms = ["instagram", "facebook", "linkedin", "twitter", "tiktok", "youtube", "pinterest"]
        
        user_message_lower = user_message.lower()
        for platform in platforms:
            if platform in user_message_lower:
                return platform
        
        return "instagram"  # Default platform

    def _get_last_content_from_history(self) -> Optional[str]:
        """
        Get last AI-generated content from chat history.
        
        Returns:
            str: Last content or None
        """
        # Search backwards through history for AI message
        for message in reversed(self.chat_history):
            if isinstance(message, AIMessage) and len(message.content) > 50:
                return message.content
        
        return None