"""
Competitor Monitoring Agent Service

Handles all competitor monitoring specific operations including:
- Competitor research
- Monitoring configuration setup
- HITL approval workflows
"""

import json
import logging
from typing import AsyncGenerator, Optional, List, Dict, Any

from langchain_core.messages import AIMessage
from langgraph.types import Command

logger = logging.getLogger(__name__)

from app.agents.competitor_monitoring import create_competitor_monitoring_agent
from app.core.firebase import get_db


class CompetitorAgentService:
    """
    Service for the Competitor Monitoring Agent.
    
    This agent specializes in:
    - Searching for competitor information
    - Analyzing competitor activities
    - Setting up continuous monitoring configurations
    - Managing HITL approval flows
    """

    def __init__(self):
        self._agent = None

    def _ensure_init(self):
        """Lazy initialization of agent and dependencies."""
        if self._agent is not None:
            return

        db = get_db()
        self._agent = create_competitor_monitoring_agent()

    async def invoke(
        self,
        message: str,
        thread_id: str,
        user_id: Optional[str] = None,
    ) -> str:
        """
        Single-turn invoke (non-streaming).

        Args:
            message: User's message
            thread_id: Conversation thread ID
            user_id: Optional user ID

        Returns:
            Agent's response text
        """
        self._ensure_init()

        result = self._agent.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config={"configurable": {"thread_id": thread_id}},
        )

        return self._extract_text(result)

    async def stream(
        self,
        message: str,
        thread_id: str,
        user_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream agent responses.

        Yields JSON-encoded events:
        - {"type": "token", "content": "..."}
        - {"type": "interrupt", "data": [...]}
        - {"type": "done"}

        Args:
            message: User's message
            thread_id: Conversation thread ID
            user_id: Optional user ID

        Yields:
            JSON strings for SSE streaming
        """
        self._ensure_init()
        
        logger.info(f"[COMPETITOR AGENT] Streaming with thread_id: {thread_id}, user_id: {user_id}, message: {message[:100]}")

        config = {"configurable": {"thread_id": thread_id}}

        for mode, chunk in self._agent.stream(
            {"messages": [{"role": "user", "content": message}]},
            config=config,
            stream_mode=["messages", "updates"],
        ):
            if mode == "messages":
                token, metadata = chunk
                if isinstance(token, AIMessage) and token.content:
                    logger.info(f"[STREAM] Raw content type: {type(token.content).__name__}")
                    logger.info(f"[STREAM] Raw content value (first 200 chars): {str(token.content)[:200]}")
                    content = self._normalize_content(token.content)
                    logger.info(f"[STREAM] Normalized content (first 200 chars): {content[:200] if content else 'EMPTY'}")
                    if content:
                        yield json.dumps({"type": "token", "content": content})

            elif mode == "updates":
                # Check for HITL interrupt
                if "__interrupt__" in chunk:
                    logger.info(f"[STREAM] Interrupt detected: {chunk}")
                    interrupts = chunk["__interrupt__"]
                    interrupt_data = []
                    for interrupt in interrupts:
                        if hasattr(interrupt, 'value'):
                            interrupt_data.append({
                                'id': interrupt.id if hasattr(interrupt, 'id') else None,
                                'value': interrupt.value
                            })
                        else:
                            interrupt_data.append(interrupt)
                    
                    logger.info(f"[STREAM] Sending interrupt data: {interrupt_data}")
                    yield json.dumps({
                        "type": "interrupt",
                        "data": interrupt_data,
                    })

    async def resume(
        self,
        thread_id: str,
        decisions: List[Dict[str, Any]],
        user_id: Optional[str] = None,
    ) -> str:
        """
        Resume an interrupted execution (non-streaming).

        Args:
            thread_id: Thread ID of interrupted conversation
            decisions: List of HITL decisions
            user_id: Optional user ID

        Returns:
            Agent's response after resuming
        """
        self._ensure_init()

        resume_payload = {"decisions": decisions}

        result = self._agent.invoke(
            Command(resume=resume_payload),
            config={"configurable": {"thread_id": thread_id}},
        )

        return self._extract_text(result)

    async def resume_stream(
        self,
        thread_id: str,
        decisions: List[Dict[str, Any]],
        user_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Resume an interrupted execution with streaming.

        Args:
            thread_id: Thread ID of interrupted conversation
            decisions: List of HITL decisions
            user_id: Optional user ID

        Yields:
            JSON strings for SSE streaming
        """
        self._ensure_init()

        resume_payload = {"decisions": decisions}
        config = {"configurable": {"thread_id": thread_id}}

        for mode, chunk in self._agent.stream(
            Command(resume=resume_payload),
            config=config,
            stream_mode=["messages", "updates"],
        ):
            if mode == "messages":
                token, metadata = chunk
                if isinstance(token, AIMessage) and token.content:
                    logger.info(f"[RESUME] Raw content type: {type(token.content).__name__}")
                    logger.info(f"[RESUME] Raw content value (first 200 chars): {str(token.content)[:200]}")
                    content = self._normalize_content(token.content)
                    logger.info(f"[RESUME] Normalized content (first 200 chars): {content[:200] if content else 'EMPTY'}")
                    if content:
                        yield json.dumps({"type": "token", "content": content})

            elif mode == "updates":
                if "__interrupt__" in chunk:
                    interrupts = chunk["__interrupt__"]
                    interrupt_data = []
                    for interrupt in interrupts:
                        if hasattr(interrupt, 'value'):
                            interrupt_data.append({
                                'id': interrupt.id if hasattr(interrupt, 'id') else None,
                                'value': interrupt.value
                            })
                        else:
                            interrupt_data.append(interrupt)
                    
                    yield json.dumps({
                        "type": "interrupt",
                        "data": interrupt_data,
                    })

    @staticmethod
    def _normalize_content(content) -> str:
        """Normalize AIMessage content to a plain string.
        
        LangChain AIMessage.content can be:
        - str: plain text
        - list: content blocks like [{"type": "text", "text": "..."}]
        """
        try:
            if isinstance(content, str):
                logger.debug(f"[NORMALIZE] Content is already string: {content[:100]}...")
                return content
            if isinstance(content, list):
                logger.debug(f"[NORMALIZE] Content is list with {len(content)} blocks")
                parts = []
                for i, block in enumerate(content):
                    if isinstance(block, dict):
                        text = block.get("text", "")
                        logger.debug(f"[NORMALIZE] Block {i}: dict with text='{text[:50]}...'")
                        parts.append(text)
                    elif isinstance(block, str):
                        logger.debug(f"[NORMALIZE] Block {i}: string '{block[:50]}...'")
                        parts.append(block)
                    else:
                        logger.warning(f"[NORMALIZE] Block {i}: unknown type {type(block).__name__}")
                result = "".join(parts)
                logger.debug(f"[NORMALIZE] Joined result: {result[:100]}...")
                return result
            logger.warning(f"[NORMALIZE] Unknown content type: {type(content).__name__}, converting to str")
            return str(content)
        except Exception as e:
            logger.error(f"[NORMALIZE] Error normalizing content: {e}", exc_info=True)
            return ""

    @staticmethod
    def _extract_text(result: dict) -> str:
        """Extract text content from agent result."""
        messages = result.get("messages", [])
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and msg.content:
                content = msg.content
                if isinstance(content, list):
                    parts = []
                    for block in content:
                        if isinstance(block, dict):
                            parts.append(block.get("text", ""))
                        elif isinstance(block, str):
                            parts.append(block)
                    return "".join(parts)
                return content
        return "I wasn't able to generate a response. Please try again."


# Singleton instance
competitor_agent_service = CompetitorAgentService()
