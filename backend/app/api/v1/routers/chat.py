from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest, ChatResponse, CampaignDataAttachment
from app.services.chat_service import chat_service
import json

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse, summary="Send a chat message")
async def send_message(request: ChatRequest):
    """
    Send a message to the AI assistant and get a response
    
    Args:
        request: ChatRequest containing the message and optional conversation history
        
    Returns:
        ChatResponse with the AI's response and optional campaign data
    """
    try:
        response_text, campaign_context = await chat_service.chat(
            user_message=request.message,
            conversation_history=request.conversation_history,
            user_id=request.user_id
        )
        
        # Build campaign data attachment if available
        campaign_data = None
        if campaign_context:
            # Determine if this is an edit request or just analytics
            intent = campaign_context.get("intent", {})
            data_type = "edit_request" if intent.get("wants_to_modify", False) else "analytics"
            show_visualization = intent.get("wants_visualization", False)
            
            campaign_data = CampaignDataAttachment(
                type=data_type,
                campaigns=campaign_context["campaigns"],
                metrics=campaign_context["metrics"],
                summary=campaign_context["summary"],
                intent=intent,
                show_visualization=show_visualization
            )
        
        return ChatResponse(
            message=response_text,
            conversation_id=None,  # Could implement conversation tracking later
            campaign_data=campaign_data
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.post("/stream", summary="Stream chat responses")
async def stream_message(request: ChatRequest):
    """
    Stream responses from the AI assistant in real-time
    
    Args:
        request: ChatRequest containing the message and optional conversation history
        
    Returns:
        StreamingResponse with chunks of the AI's response
    """
    try:
        async def generate():
            async for chunk in chat_service.chat_stream(
                user_message=request.message,
                conversation_history=request.conversation_history,
                user_id=request.user_id
            ):
                # Send each chunk as a JSON object
                yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"
            
            # Send final done signal
            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stream chat message: {str(e)}"
        )


@router.get("/health", summary="Check chat service health")
async def health_check():
    """Check if the chat service is operational"""
    try:
        # Simple test to see if the service is initialized
        return {
            "status": "healthy",
            "service": "chat",
            "model": "gemini-2.5-flash-lite"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Chat service unavailable: {str(e)}"
        )
