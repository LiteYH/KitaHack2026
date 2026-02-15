import os
from typing import List, Optional, AsyncGenerator
import google.generativeai as genai
from app.core.config import settings
from app.schemas.chat import ChatMessage
from dotenv import load_dotenv

from app.services.agents.content_agent import ContentAgent

load_dotenv()


class ChatService:
    """
    Upgraded ChatService using a fully agentic MarketingAgent.

    Features:
    - Multi-tool reasoning: content, analytics, scheduling, competitor analysis
    - RAG integration in content generation
    - Markdown-formatted responses
    - Conversation history support
    - Optional async streaming
    """

    def __init__(self):
        self.agent = ContentAgent()

    async def chat(
        self,
        user_message: str,
        conversation_history: Optional[List[ChatMessage]] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Handle a single chat message through the agent.

        Args:
            user_message: User input
            conversation_history: Previous messages in conversation
            user_id: Optional user ID for personalization

        Returns:
            Formatted AI response
        """
        try:
            # Agent manages its own chat history internally
            # No need to manually add history here
            
            # Run the agent
            response = await self.agent.run(user_message)
            return response

        except Exception as e:
            print(f"Error in ChatService.chat: {str(e)}")
            raise

    async def chat_stream(
        self,
        user_message: str,
        conversation_history: Optional[List[ChatMessage]] = None,
        user_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat responses from the agent.

        Args:
            user_message: User input
            conversation_history: Previous messages in conversation
            user_id: Optional user ID

        Yields:
            Chunks of AI response as they are generated
        """
        try:
            # For now, return the full response (streaming can be added later)
            response = await self.agent.run(user_message)
            yield response

        except Exception as e:
            yield f"Error in ChatService.chat_stream: {str(e)}"


# Singleton instance
chat_service = ChatService()
