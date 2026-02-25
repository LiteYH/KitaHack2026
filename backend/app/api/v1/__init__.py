from fastapi import APIRouter
from .routers import (
    chat_router,
    campaigns_router,
    crons_router,
    roi_router,
    youtube_report_router,
)

# Create main v1 router
api_router = APIRouter()

api_router.include_router(chat_router)
api_router.include_router(campaigns_router)
api_router.include_router(roi_router)
api_router.include_router(youtube_report_router)
api_router.include_router(crons_router)

__all__ = ["api_router"]
