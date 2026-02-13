"""
Multi-Agent Service

Unified service using the **Subagents Pattern** from LangChain.
This is the main entry point for all multi-agent operations.

Architecture:
"A central main agent (supervisor) coordinates subagents by calling them as tools.
The main agent decides which subagent to invoke, what input to provide, 
and how to combine results."

Key features:
- Single supervisor agent maintains conversation context
- Specialized subagents wrapped as tools
- Supervisor intelligently delegates to subagents
- Natural conversation flow across multiple turns
"""

import json
import logging
import uuid
from typing import AsyncGenerator, Optional, List, Dict, Any

from langchain_core.messages import AIMessage

logger = logging.getLogger(__name__)

from app.core.firebase import get_db
from app.core.competitor_agent_memory import HybridMemoryManager
from app.agents.supervisor import create_supervisor_agent


class MultiAgentService:
    """
    Main service for multi-agent system using the Subagents pattern.
    
    The supervisor agent:
    - Maintains full conversation context
    - Calls specialized subagents as tools when needed
    - Handles general questions directly
    - Coordinates complex multi-step workflows
    
    This is the only service the API layer needs to interact with.
    """

    def __init__(self):
        self._supervisor = None
        self._memory_manager: Optional[HybridMemoryManager] = None
        self._cron_service = None
        self._firestore_client = None

    def set_services(self, cron_service=None, firestore_client=None):
        """
        Inject services that are only available after app startup (lifespan).
        Call this from main.py after CronService is initialized.
        """
        self._cron_service = cron_service
        self._firestore_client = firestore_client
        # Reset supervisor so it gets rebuilt with the new services
        self._supervisor = None
        logger.info("[SUPERVISOR] Services injected (CronService, Firestore)")

    def _ensure_init(self, user_id: Optional[str] = None):
        """Lazy initialization of supervisor agent."""
        if self._supervisor is not None:
            # Even if supervisor exists, update user_id for per-request context
            if user_id:
                from app.agents.competitor_monitoring.tools.monitoring_tools import set_monitoring_services
                set_monitoring_services(self._cron_service, self._firestore_client, user_id)
            return
        
        db = self._firestore_client or get_db()
        self._memory_manager = HybridMemoryManager(firestore_client=db)
        self._supervisor = create_supervisor_agent(
            memory_manager=self._memory_manager,
            cron_service=self._cron_service,
            firestore_client=db,
            user_id=user_id,
        )
        logger.info("[SUPERVISOR] Initialized supervisor agent with subagents")

    async def chat(
        self,
        message: str,
        thread_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> str:
        """
        Single-turn chat (non-streaming).

        The supervisor agent handles the request:
        - Maintains conversation context across turns
        - Decides whether to call a subagent or answer directly
        - Returns the complete response

        Args:
            message: User's message
            thread_id: Optional conversation thread ID  
            user_id: Optional user ID

        Returns:
            Agent's response text
        """
        self._ensure_init(user_id=user_id)
        thread_id = thread_id or str(uuid.uuid4())

        logger.info(f"[SUPERVISOR] Processing message in thread {thread_id}")

        result = await self._supervisor.ainvoke(
            {"messages": [{"role": "user", "content": message}]},
            config={"configurable": {"thread_id": thread_id}},
        )

        return self._extract_text(result)

    async def chat_stream(
        self,
        message: str,
        thread_id: Optional[str] = None,
        user_id: Optional[str] = None,
        agent_name: Optional[str] = None,  # Kept for backwards compatibility
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat responses with SSE.

        The supervisor agent handles the request:
        - Maintains conversation context
        - Decides whether to call subagents or answer directly
        - Streams tokens as they're generated

        Yields JSON events:
        - {"type": "metadata", "thread_id": "..."}
        - {"type": "token", "content": "..."}
        - {"type": "interrupt", "data": [...]}  (for HITL)
        - {"type": "done"}

        Args:
            message: User's message  
            thread_id: Optional conversation thread ID
            user_id: Optional user ID
            agent_name: Ignored (kept for backwards compatibility)

        Yields:
            JSON-encoded event strings
        """
        self._ensure_init(user_id=user_id)
        thread_id = thread_id or str(uuid.uuid4())
        
        logger.info(
            f"[SUPERVISOR] Streaming message in thread {thread_id}: {message[:100]}"
        )
        
        # Yield metadata with thread_id
        yield json.dumps({
            "type": "metadata",
            "thread_id": thread_id,
        })

        # Stream from supervisor agent
        config = {"configurable": {"thread_id": thread_id}}

        try:
            async for event in self._supervisor.astream(
                {"messages": [{"role": "user", "content": message}]},
                config=config,
                stream_mode=["messages", "updates"],
                subgraphs=True,
            ):
                if len(event) == 3:
                    _, mode, chunk = event
                else:
                    mode, chunk = event
                if mode == "messages":
                    token, metadata = chunk
                    if isinstance(token, AIMessage) and token.content:
                        content = self._normalize_content(token.content)
                        if content:
                            yield json.dumps({"type": "token", "content": content})

                elif mode == "updates":
                    # Check for HITL interrupts
                    if "__interrupt__" in chunk:
                        logger.info(f"[SUPERVISOR] Interrupt detected: {chunk}")
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
                        
                        logger.info(f"[SUPERVISOR] Sending interrupt data: {interrupt_data}")
                        yield json.dumps({
                            "type": "interrupt",
                            "data": interrupt_data,
                        })
        except Exception as e:
            logger.error(f"[SUPERVISOR] Stream error in thread {thread_id}: {str(e)}", exc_info=True)
            yield json.dumps({
                "type": "error",
                "message": f"Streaming error: {str(e)}"
            })
            return

        # Send done signal
        yield json.dumps({"type": "done"})

    async def resume(
        self,
        agent_name: str,  # Ignored for supervisor pattern
        thread_id: str,
        decisions: List[Dict[str, Any]],
        user_id: Optional[str] = None,
    ) -> str:
        """
        Resume an interrupted execution (non-streaming).

        Used for HITL (Human-in-the-Loop) approvals.

        Args:
            agent_name: Ignored (kept for backwards compatibility)
            thread_id: Thread ID of interrupted conversation
            decisions: List of HITL decisions
            user_id: Optional user ID

        Returns:
            Agent's response after resuming
        """
        self._ensure_init(user_id=user_id)
        
        from langgraph.types import Command
        resume_payload = {"decisions": decisions}
        if decisions and decisions[0].get("interrupt_id"):
            grouped: Dict[str, Dict[str, Any]] = {}
            for decision in decisions:
                interrupt_id = decision.get("interrupt_id")
                if not interrupt_id:
                    continue
                entry = grouped.setdefault(interrupt_id, {"decisions": []})
                entry["decisions"].append(
                    {k: v for k, v in decision.items() if k != "interrupt_id"}
                )
            if grouped:
                resume_payload = grouped

        result = await self._supervisor.ainvoke(
            Command(resume=resume_payload),
            config={"configurable": {"thread_id": thread_id}},
        )

        return self._extract_text(result)

    async def resume_stream(
        self,
        agent_name: str,  # Ignored for supervisor pattern
        thread_id: str,
        decisions: List[Dict[str, Any]],
        user_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Resume an interrupted execution with streaming.

        Used for HITL (Human-in-the-Loop) approvals.

        Args:
            agent_name: Ignored (kept for backwards compatibility)
            thread_id: Thread ID of interrupted conversation
            decisions: List of HITL decisions
            user_id: Optional user ID

        Yields:
            JSON-encoded event strings
        """
        self._ensure_init(user_id=user_id)
        
        from langgraph.types import Command
        resume_payload = {"decisions": decisions}
        if decisions and decisions[0].get("interrupt_id"):
            grouped: Dict[str, Dict[str, Any]] = {}
            for decision in decisions:
                interrupt_id = decision.get("interrupt_id")
                if not interrupt_id:
                    continue
                entry = grouped.setdefault(interrupt_id, {"decisions": []})
                entry["decisions"].append(
                    {k: v for k, v in decision.items() if k != "interrupt_id"}
                )
            if grouped:
                resume_payload = grouped
        config = {"configurable": {"thread_id": thread_id}}

        try:
            async for event in self._supervisor.astream(
                Command(resume=resume_payload),
                config=config,
                stream_mode=["messages", "updates"],
                subgraphs=True,
            ):
                if len(event) == 3:
                    _, mode, chunk = event
                else:
                    mode, chunk = event
                if mode == "messages":
                    token, metadata = chunk
                    if isinstance(token, AIMessage) and token.content:
                        content = self._normalize_content(token.content)
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
        except Exception as e:
            logger.error(
                f"[SUPERVISOR] Resume stream error in thread {thread_id}: {str(e)}",
                exc_info=True,
            )
            yield json.dumps({
                "type": "error",
                "message": f"Resume streaming error: {str(e)}"
            })
            return

        yield json.dumps({"type": "done"})

    @staticmethod
    def _normalize_content(content) -> str:
        """Normalize AIMessage content to plain string."""
        try:
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                parts = []
                for block in content:
                    if isinstance(block, dict):
                        parts.append(block.get("text", ""))
                    elif isinstance(block, str):
                        parts.append(block)
                return "".join(parts)
            return str(content)
        except Exception as e:
            logger.error(f"[SUPERVISOR] Error normalizing content: {e}")
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
multi_agent_service = MultiAgentService()
