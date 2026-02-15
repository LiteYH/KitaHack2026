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
        # Build messages list
        messages = [self.system_message] + self.chat_history + [HumanMessage(content=user_message)]
        
        # Invoke LLM (it will decide whether to use tools)
        response = await self.llm_with_tools.ainvoke(messages)
        
        # Handle tool calls if LLM decided to use them
        if response.tool_calls:
            # Add AI response with tool calls to messages
            messages.append(response)
            
            # Execute each tool call
            for tool_call in response.tool_calls:
                if tool_call["name"] == "generate_content":
                    # Invoke the tool
                    tool_result = generate_content.invoke(tool_call["args"])
                    
                    # Add tool result to messages
                    messages.append(
                        ToolMessage(
                            content=str(tool_result),
                            tool_call_id=tool_call["id"]
                        )
                    )
            
            # Get final response from LLM with tool results
            response = await self.llm_with_tools.ainvoke(messages)
        
        # Update chat history
        self.chat_history.append(HumanMessage(content=user_message))
        self.chat_history.append(AIMessage(content=response.content))
        
        return response.content