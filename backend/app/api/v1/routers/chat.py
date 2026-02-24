"""
Chat Router - Multi-Agent System

Provides the unified multi-agent chat endpoints:
- POST /chat/message       — single-turn invoke (non-streaming)
- POST /chat/stream        — SSE streaming
- POST /chat/resume        — resume after HITL interrupt (non-streaming)
- POST /chat/resume/stream — resume with streaming
- GET  /chat/messages      — fetch monitoring update messages

All chat requests are routed through the orchestrator → specialized agent pipeline.
"""
import json
import logging
import uuid

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional

from app.schemas.chat import (
    AgentChatRequest,
    AgentChatResponse,
    AgentResumeRequest,
    AgentResumeResponse,
)
from app.services.multi_agent_service import multi_agent_service
from app.core.auth import get_current_user_id
from app.core.firebase import get_db

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


@router.post("/message", response_model=AgentChatResponse)
async def agent_chat(request: AgentChatRequest):
    """
    Single-turn chat (non-streaming).

    Routes through orchestrator → specialized agent and returns
    the complete response.
    """
    thread_id = request.thread_id or str(uuid.uuid4())
    logger.info(f"💬 Chat request received - Thread: {thread_id}, Message: {request.message[:50]}...")

    try:
        response_text = await multi_agent_service.chat(
            message=request.message,
            thread_id=thread_id,
            user_id=request.user_id,
        )
        logger.info(f"✅ Chat completed - Thread: {thread_id}")
        return AgentChatResponse(
            message=response_text,
            thread_id=thread_id,
        )
    except Exception as e:
        logger.error(f"❌ Chat error - Thread: {thread_id}, Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def agent_chat_stream(request: AgentChatRequest):
    """
    Streaming chat via Server-Sent Events (SSE).

    Streams JSON payloads:
    - data: {"type": "routing", "agent": "...", "task": "...", "confidence": 0.9}
    - data: {"type": "token",   "content": "partial text..."}
    - data: {"type": "done"}
    """
    thread_id = request.thread_id or str(uuid.uuid4())
    logger.info(f"🌊 Stream chat request - Thread: {thread_id}, Message: {request.message[:50]}...")

    async def event_generator():
        try:
            async for data in multi_agent_service.chat_stream(
                message=request.message,
                thread_id=thread_id,
                user_id=request.user_id,
                user_email=request.user_email,
            ):
                yield f"data: {data}\n\n"
            logger.info(f"✅ Stream completed - Thread: {thread_id}")
        except Exception as e:
            logger.error(f"❌ Stream error - Thread: {thread_id}, Error: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/resume", response_model=AgentResumeResponse)
async def agent_chat_resume(request: AgentResumeRequest):
    """
    Resume an interrupted execution (non-streaming).

    Used when the agent hits a human-in-the-loop interrupt and needs
    user approval/edit/rejection to continue.
    """
    logger.info(f"🔄 Resume request - Thread: {request.thread_id}, Agent: {request.agent_name}")
    
    try:
        # Convert Pydantic models to dicts and map edit args -> edited_action
        decisions = []
        for decision in request.decisions:
            decision_data = decision.model_dump()
            if decision_data.get("type") == "edit" and decision_data.get("args"):
                decision_data["edited_action"] = {
                    "name": decision_data.get("action"),
                    "args": decision_data["args"],
                }
            decisions.append(decision_data)
        
        response_text = await multi_agent_service.resume(
            agent_name=request.agent_name,
            thread_id=request.thread_id,
            decisions=decisions,
            user_id=request.user_id,
        )
        
        logger.info(f"✅ Resume completed - Thread: {request.thread_id}")
        return AgentResumeResponse(
            message=response_text,
            thread_id=request.thread_id,
            completed=True,  # If it reaches here without exception, it completed
        )
    except Exception as e:
        logger.error(f"❌ Resume error - Thread: {request.thread_id}, Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resume/stream")
async def agent_chat_resume_stream(request: AgentResumeRequest):
    """

    Streams JSON payloads:
    - data: {"type": "token",   "content": "partial text..."}
    - data: {"type": "interrupt", "data": [...]}  (if another interrupt occurs)
    - data: {"type": "done"}
    """
    logger.info(f"🌊 Resume stream request - Thread: {request.thread_id}, Agent: {request.agent_name}")
    
    async def event_generator():
        try:
            # Convert Pydantic models to dicts and map edit args -> edited_action
            decisions = []
            for decision in request.decisions:
                decision_data = decision.model_dump()
                if decision_data.get("type") == "edit" and decision_data.get("args"):
                    decision_data["edited_action"] = {
                        "name": decision_data.get("action"),
                        "args": decision_data["args"],
                    }
                decisions.append(decision_data)
            
            async for data in multi_agent_service.resume_stream(
                agent_name=request.agent_name,
                thread_id=request.thread_id,
                decisions=decisions,
                user_id=request.user_id,
            ):
                yield f"data: {data}\n\n"
            logger.info(f"✅ Resume stream completed - Thread: {request.thread_id}")
        except Exception as e:
            logger.error(f"❌ Resume stream error - Thread: {request.thread_id}, Error: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/messages")
async def get_chat_messages(
    user_id: str = Depends(get_current_user_id),
    limit: int = Query(50, description="Maximum number of messages to return"),
    message_type: Optional[str] = Query(None, description="Filter by message type (e.g., 'monitoring_update')")
):
    """
    Get chat messages for the current user.
    
    Retrieves monitoring update messages and other system messages
    that should appear in the chat interface.
    
    Args:
        user_id: Current user's ID (from auth token)
        limit: Maximum number of messages to return
        message_type: Optional filter by message type
    
    Returns:
        List of chat messages ordered by timestamp (newest first)
    """
    try:
        db = get_db()
        
        # Build query
        query = db.collection('chat_messages').where('user_id', '==', user_id)
        
        if message_type:
            query = query.where('type', '==', message_type)
        
        query = query.order_by('timestamp', direction='DESCENDING').limit(limit)
        
        # Execute query
        messages_docs = query.get()
        
        messages = []
        for doc in messages_docs:
            data = doc.to_dict()
            data['id'] = doc.id
            # Convert timestamp to ISO string if it exists
            if data.get('timestamp'):
                data['timestamp'] = data['timestamp'].isoformat()
            messages.append(data)
        
        logger.info(f"Retrieved {len(messages)} chat messages for user {user_id}")
        return messages
        
    except Exception as e:
        logger.error(f"Failed to get chat messages for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve messages: {str(e)}")


@router.get("/history/{thread_id}")
async def get_thread_history(
    thread_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get chat history for a specific thread.
    
    Retrieves all messages (user, assistant, tool calls, etc.) for a conversation thread.
    Used to restore chat history when loading a previous conversation.
    
    Args:
        thread_id: Thread/conversation ID
        user_id: Current user's ID (from auth token)
    
    Returns:
        List of messages ordered by timestamp (oldest first)
    """
    try:
        if not multi_agent_service._chat_history:
            raise HTTPException(status_code=503, detail="Chat history service not initialized")
        
        messages = await multi_agent_service._chat_history.get_thread_messages(
            thread_id=thread_id,
            user_id=user_id,
            # limit=limit
        )
        
        logger.info(f"Retrieved {len(messages)} messages from thread {thread_id} for user {user_id}")
        return messages
        
    except Exception as e:
        logger.error(f"Failed to get thread history for {thread_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve thread history: {str(e)}")


@router.delete("/history/{thread_id}")
async def clear_thread_history(
    thread_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Clear all messages in a thread.
    
    Deletes all chat history for a specific conversation thread.
    Also removes the thread metadata from Firestore.
    
    Args:
        thread_id: Thread/conversation ID to clear
        user_id: Current user's ID (from auth token)
    
    Returns:
        Status message with count of deleted messages
    """
    try:
        if not multi_agent_service._chat_history:
            raise HTTPException(status_code=503, detail="Chat history service not initialized")
        
        deleted_count = await multi_agent_service._chat_history.clear_thread(
            thread_id=thread_id,
            user_id=user_id
        )
        
        logger.info(f"Cleared {deleted_count} messages from thread {thread_id} for user {user_id}")
        return {
            "status": "success",
            "thread_id": thread_id,
            "deleted_count": deleted_count,
            "message": f"Cleared {deleted_count} messages"
        }
        
    except Exception as e:
        logger.error(f"Failed to clear thread {thread_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to clear thread: {str(e)}")
