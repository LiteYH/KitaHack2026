import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings

load_dotenv()

class IntentSchema(BaseModel):
    intent: str
    platform: Optional[str]
    requires_rag: bool = False
    multi_step: bool = False

class IntentService:

    def __init__(self):
        api_key = settings.google_api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in .env file.")
        
        self.llm = ChatGoogleGenerativeAI(
            model = "gemini-2.5-flash",
            api_key = api_key,
            temperature = 0,
        ).with_structured_output(IntentSchema)
        
        # Can add agent intents here for future development
        self.prompt = ChatPromptTemplate.from_messages([
            ("system",
             """Classify the user's marketing request.

                Available intents:
                - content_generation

                Return structured JSON only."""
             ),
            ("human", "{input}")
        ])

    async def classify(self, user_message: str) -> IntentSchema:
        chain = self.prompt | self.llm
        return await chain.ainvoke({"input": user_message})

intent_service = IntentService()

