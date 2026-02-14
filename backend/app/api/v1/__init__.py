from fastapi import APIRouter
from .routers import chat_router
from .routers.roi import router as roi_router

# Create main v1 router
api_router = APIRouter()

# Include all routers
api_router.include_router(chat_router)
api_router.include_router(roi_router)

__all__ = ["api_router"]
