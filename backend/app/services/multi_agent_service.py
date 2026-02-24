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
- Full intermediate event streaming (tool calls, tool results, agent routing, tokens)
"""

import json
import logging
import uuid
from typing import AsyncGenerator, Optional, List, Dict, Any

from langchain_core.messages import AIMessage, AIMessageChunk, ToolMessage, HumanMessage

logger = logging.getLogger(__name__)

from app.core.firebase import get_db
from app.agents.supervisor import create_supervisor_agent
from app.services.chat_history_service import ChatHistoryService


class MultiAgentService:
    """
    Main service for multi-agent system using the Subagents pattern.
    
    The supervisor agent:
    - Maintains full conversation context
    - Calls specialized subagents as tools when needed
    - Handles general questions directly
    - Coordinates complex multi-step workflows
    
    Streams ALL intermediate events to frontend:
    - metadata: thread info
    - token: LLM streaming tokens
    - tool_call: when agent decides to call a tool
    - tool_result: result from tool execution
    - agent_status: which node/agent is running
    - interrupt: HITL approval requests
    - error: errors
    - done: completion signal
    """

    def __init__(self):
        self._supervisor = None
        self._cron_service = None
        self._firestore_client = None
        self._chat_history: Optional[ChatHistoryService] = None

    def set_services(self, cron_service=None, firestore_client=None):
        """
        Inject services that are only available after app startup (lifespan).
        Call this from main.py after CronService is initialized.
        """
        self._cron_service = cron_service
        self._firestore_client = firestore_client
        if firestore_client:
            self._chat_history = ChatHistoryService(firestore_client)
        # Reset supervisor so it gets rebuilt with the new services
        self._supervisor = None
        logger.info("[SUPERVISOR] Services injected (CronService, Firestore, ChatHistory)")

    def _ensure_init(self, user_id: Optional[str] = None):
        """Lazy initialization of supervisor agent."""
        if self._supervisor is not None:
            # Even if supervisor exists, update user_id for per-request context
            if user_id:
                from app.agents.competitor_monitoring.tools.monitoring_tools import set_monitoring_services
                set_monitoring_services(self._cron_service, self._firestore_client, user_id)
            return
        
        db = self._firestore_client or get_db()
        self._supervisor = create_supervisor_agent(
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
        """Single-turn chat (non-streaming)."""
        self._ensure_init(user_id=user_id)
        thread_id = thread_id or str(uuid.uuid4())

        logger.info(f"[SUPERVISOR] Processing message in thread {thread_id}")
        
        # Set this as the user's active thread for monitoring updates
        if self._chat_history and user_id:
            try:
                await self._chat_history.set_active_thread(user_id, thread_id)
            except Exception as e:
                logger.error(f"Failed to set active thread: {e}")

        result = await self._supervisor.ainvoke(
            {"messages": [{"role": "user", "content": message}]},
            config={"configurable": {"thread_id": thread_id}},
        )

        return self._extract_text(result)

    async def _stream_graph(
        self,
        input_data: Any,
        config: dict,
        thread_id: str,
    ) -> AsyncGenerator[str, None]:
        """
        Core streaming method that emits ALL intermediate events.
        
        Uses LangGraph's astream with stream_mode=["messages", "updates"]
        and subgraphs=True to capture every event from the agent graph.
        
        Event types emitted:
        - token: LLM streaming content
        - tool_call: agent decided to invoke a tool (name + args)
        - tool_result: result returned from tool execution
        - agent_status: which graph node is currently executing
        - interrupt: HITL approval needed
        - error: error occurred
        - done: stream complete
        """
        token_count = 0
        seen_tool_calls: set = set()  # Track tool_call IDs to avoid duplicates

        try:
            async for event in self._supervisor.astream(
                input_data,
                config=config,
                stream_mode=["messages", "updates"],
                subgraphs=True,
            ):
                # Defensive event parsing — handle varying tuple lengths
                if not isinstance(event, tuple) or len(event) < 2:
                    continue
                
                if len(event) == 3:
                    namespace, mode, chunk = event
                    # Extract subgraph info from namespace for agent_status
                    ns_str = str(namespace) if namespace else ""
                else:
                    mode, chunk = event
                    ns_str = ""

                if mode == "messages":
                    # chunk is (message, metadata) tuple
                    if isinstance(chunk, tuple) and len(chunk) == 2:
                        token, metadata = chunk
                    else:
                        token = chunk
                        metadata = {}

                    langgraph_node = metadata.get("langgraph_node", "") if isinstance(metadata, dict) else ""

                    # --- AIMessage with tool_calls (agent deciding to call a tool) ---
                    if isinstance(token, (AIMessage, AIMessageChunk)) and hasattr(token, "tool_calls") and token.tool_calls:
                        for tc in token.tool_calls:
                            tc_id = tc.get("id", "")
                            if tc_id and tc_id not in seen_tool_calls:
                                seen_tool_calls.add(tc_id)
                                yield json.dumps({
                                    "type": "tool_call",
                                    "name": tc.get("name", "unknown"),
                                    "args": tc.get("args", {}),
                                    "tool_call_id": tc_id,
                                    "node": langgraph_node,
                                })

                    # --- AIMessage with streaming content tokens ---
                    if isinstance(token, (AIMessage, AIMessageChunk)) and token.content:
                        content = self._normalize_content(token.content)
                        if content:
                            token_count += 1
                            yield json.dumps({
                                "type": "token",
                                "content": content,
                                "node": langgraph_node,
                            })

                    # --- ToolMessage (result from tool execution) ---
                    if isinstance(token, ToolMessage):
                        tool_content = self._normalize_content(token.content) if token.content else ""
                        yield json.dumps({
                            "type": "tool_result",
                            "name": token.name or "unknown",
                            "content": tool_content[:2000],  # Truncate very long results
                            "tool_call_id": token.tool_call_id if hasattr(token, "tool_call_id") else None,
                            "node": langgraph_node,
                        })

                elif mode == "updates":
                    if isinstance(chunk, dict):
                        # --- HITL interrupts ---
                        if "__interrupt__" in chunk:
                            interrupts = chunk["__interrupt__"]
                            interrupt_data = []
                            for interrupt in interrupts:
                                if hasattr(interrupt, 'value'):
                                    interrupt_data.append({
                                        'id': interrupt.id if hasattr(interrupt, 'id') else None,
                                        'value': interrupt.value,
                                    })
                                else:
                                    interrupt_data.append(interrupt)
                            
                            yield json.dumps({
                                "type": "interrupt",
                                "data": interrupt_data,
                            })
                        else:
                            # --- Agent status: emit which node just completed ---
                            for node_name in chunk.keys():
                                if node_name.startswith("__"):
                                    continue
                                yield json.dumps({
                                    "type": "agent_status",
                                    "node": node_name,
                                    "namespace": ns_str,
                                })

        except Exception as e:
            error_msg = str(e)
            # Filter out LangChain internal warnings
            if any(ignore in error_msg.lower() for ignore in [
                'chatvertexai', 'langchain-google-vertexai', 'deprecationwarning',
            ]):
                logger.debug(f"[SUPERVISOR] Suppressed internal warning: {error_msg}")
            else:
                logger.error(f"[SUPERVISOR] Stream error in thread {thread_id}: {error_msg}", exc_info=True)
                yield json.dumps({
                    "type": "error",
                    "message": f"Streaming error: {error_msg}",
                })
            return

        logger.info(f"[SUPERVISOR] Stream completed for thread {thread_id} - {token_count} tokens")
        yield json.dumps({"type": "done"})

    async def _stream_and_save(
        self,
        input_data: Any,
        config: dict,
        thread_id: str,
        user_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Wraps _stream_graph and persists every event type to Firestore,
        including interrupt (HITL) payloads and the final assembled assistant
        message.  Both chat_stream and resume_stream delegate here so the
        saving logic only lives in one place.
        """
        assistant_content: List[str] = []

        async for event_json in self._stream_graph(input_data, config, thread_id):
            if self._chat_history and user_id:
                try:
                    event_data = json.loads(event_json)
                    etype = event_data.get("type")

                    if etype == "token":
                        assistant_content.append(event_data.get("content", ""))

                    elif etype == "tool_call":
                        await self._chat_history.save_message(
                            thread_id=thread_id,
                            user_id=user_id,
                            role='tool_call',
                            content=f"Calling {event_data.get('name', 'unknown')}",
                            agent=event_data.get("name"),
                            tool_args=event_data.get("args"),
                            tool_call_id=event_data.get("tool_call_id"),
                            node=event_data.get("node"),
                        )

                    elif etype == "tool_result":
                        await self._chat_history.save_message(
                            thread_id=thread_id,
                            user_id=user_id,
                            role='tool_result',
                            content=event_data.get("content", ""),
                            agent=event_data.get("name"),
                            tool_call_id=event_data.get("tool_call_id"),
                            node=event_data.get("node"),
                        )

                    elif etype == "agent_status":
                        await self._chat_history.save_message(
                            thread_id=thread_id,
                            user_id=user_id,
                            role='agent_status',
                            content=f"Agent: {event_data.get('node', 'unknown')}",
                            node=event_data.get("node"),
                            metadata={'namespace': event_data.get("namespace")},
                        )

                    elif etype == "interrupt":
                        # Persist the HITL card so it survives a page refresh.
                        # interrupt_data is stored in metadata so the frontend
                        # can reconstruct the approval card from history.
                        await self._chat_history.save_message(
                            thread_id=thread_id,
                            user_id=user_id,
                            role='hitl',
                            content='Approval required for monitoring configuration',
                            metadata={'interrupt_data': event_data.get("data", [])},
                        )

                except Exception as e:
                    logger.error(f"Failed to save event to Firestore: {e}")

            yield event_json

        # Flush final assembled assistant message
        if self._chat_history and user_id and assistant_content:
            try:
                final_content = "".join(assistant_content)
                if final_content.strip():
                    await self._chat_history.save_message(
                        thread_id=thread_id,
                        user_id=user_id,
                        role='assistant',
                        content=final_content,
                    )
            except Exception as e:
                logger.error(f"Failed to save assistant message to Firestore: {e}")

    async def chat_stream(
        self,
        message: str,
        thread_id: Optional[str] = None,
        user_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        user_email: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat responses with ALL intermediate events.
        
        Yields JSON events:
        - {"type": "metadata", "thread_id": "..."}
        - {"type": "token", "content": "...", "node": "..."}
        - {"type": "tool_call", "name": "...", "args": {...}, "tool_call_id": "..."}
        - {"type": "tool_result", "name": "...", "content": "...", "tool_call_id": "..."}
        - {"type": "agent_status", "node": "...", "namespace": "..."}
        - {"type": "interrupt", "data": [...]}
        - {"type": "error", "message": "..."}
        - {"type": "done"}
        """
        self._ensure_init(user_id=user_id)
        thread_id = thread_id or str(uuid.uuid4())
        
        logger.info(f"[SUPERVISOR] Streaming message in thread {thread_id}: {message[:100]}")
        
        # Set this as the user's active thread for monitoring updates
        if self._chat_history and user_id:
            try:
                await self._chat_history.set_active_thread(user_id, thread_id)
            except Exception as e:
                logger.error(f"Failed to set active thread: {e}")
        
        # Save user message to Firestore
        if self._chat_history and user_id:
            try:
                await self._chat_history.save_message(
                    thread_id=thread_id,
                    user_id=user_id,
                    role='user',
                    content=message
                )
            except Exception as e:
                logger.error(f"Failed to save user message to Firestore: {e}")
        
        # Yield metadata with thread_id
        yield json.dumps({"type": "metadata", "thread_id": thread_id})

        config = {"configurable": {"thread_id": thread_id, "user_email": user_email or ""}}

        async for event_json in self._stream_and_save(
            {"messages": [{"role": "user", "content": message}]},
            config,
            thread_id,
            user_id=user_id,
        ):
            yield event_json

    async def resume(
        self,
        agent_name: str,
        thread_id: str,
        decisions: List[Dict[str, Any]],
        user_id: Optional[str] = None,
    ) -> str:
        """Resume an interrupted execution (non-streaming)."""
        self._ensure_init(user_id=user_id)
        
        from langgraph.types import Command
        resume_payload = self._build_resume_payload(decisions)

        result = await self._supervisor.ainvoke(
            Command(resume=resume_payload),
            config={"configurable": {"thread_id": thread_id}},
        )

        return self._extract_text(result)

    async def resume_stream(
        self,
        agent_name: str,
        thread_id: str,
        decisions: List[Dict[str, Any]],
        user_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Resume an interrupted execution with full streaming."""
        self._ensure_init(user_id=user_id)
        
        from langgraph.types import Command
        resume_payload = self._build_resume_payload(decisions)
        config = {"configurable": {"thread_id": thread_id}}

        # Persist the user's HITL decision before streaming the result so that
        # on page refresh the approval card is shown in its resolved state.
        if self._chat_history and user_id and decisions:
            try:
                decision_type = decisions[0].get("type", "approve") if decisions else "approve"
                await self._chat_history.save_message(
                    thread_id=thread_id,
                    user_id=user_id,
                    role='hitl_resolution',
                    content=f"HITL decision: {decision_type}",
                    metadata={'decisions': decisions, 'decision_type': decision_type},
                )
            except Exception as e:
                logger.error(f"Failed to save HITL resolution: {e}")

        async for event_json in self._stream_and_save(
            Command(resume=resume_payload),
            config,
            thread_id,
            user_id=user_id,
        ):
            yield event_json

    @staticmethod
    def _build_resume_payload(decisions: List[Dict[str, Any]]) -> Any:
        """Build resume payload from HITL decisions."""
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
        return resume_payload

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
