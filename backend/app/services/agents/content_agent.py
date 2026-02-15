from typing import List
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, ToolMessage, SystemMessage

from app.core.config import settings
from app.services.tools.content_tool import generate_content


class ContentAgent:
    """
    Modern LangChain 1.0+ SME Marketing Assistant using tool binding.
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

        # Modern LangChain 1.0+ tool binding
        self.llm_with_tools = self.llm.bind_tools([generate_content])
        
        # Chat history storage
        self.chat_history: List[BaseMessage] = []
        
        # System message
        self.system_message = SystemMessage(content="""You are BossolutionAI, an AI-powered marketing assistant for SMEs.

        Your capabilities:
        - Generate high-performing social media content using data-driven insights
        - Provide scheduling recommendations based on engagement analysis
        - Format responses professionally in Markdown

        When users request content generation, use the generate_content tool to access RAG examples and create optimized posts.""")


    async def run(self, user_message: str) -> str:
        """
        Run the agent with the user's message using modern tool calling.
        """
        # Quick detection: if mentions content creation, force tool use
        content_keywords = ['write', 'create', 'generate', 'post', 'caption', 'draft']
        
        if any(kw in user_message.lower() for kw in content_keywords):
            # Directly invoke tool instead of letting LLM decide
            tool_input = {"user_input": user_message}
            examples_context = generate_content.invoke(tool_input)
            
            # Let LLM create final post using examples
            messages = [
                SystemMessage(content="You are a marketing expert. Use the examples below to create an engaging social media post."),
                HumanMessage(content=f"{examples_context}\n\nCreate the final post now.")
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Update chat history
            self.chat_history.append(HumanMessage(content=user_message))
            self.chat_history.append(AIMessage(content=response.content))
            
            return response.content
        
        else:
            # Normal conversation without tools
            messages = [self.system_message] + self.chat_history + [HumanMessage(content=user_message)]
            
            response = await self.llm.ainvoke(messages)
            
            # Update chat history
            self.chat_history.append(HumanMessage(content=user_message))
            self.chat_history.append(AIMessage(content=response.content))
            
            return response.content