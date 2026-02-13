from fastapi import APIRouter
from .routers import chat_router
from .routers.crons import router as crons_router

# Create main v1 router
api_router = APIRouter()

# Include multi-agent chat router (all chat goes through multi-agent system)
api_router.include_router(chat_router)

# Include cron jobs management router
api_router.include_router(crons_router)

__all__ = ["api_router"]
