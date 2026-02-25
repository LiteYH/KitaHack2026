"""
API v1 routers package.
"""
from .chat import router as chat_router
from .campaigns import router as campaigns_router
from .crons import router as crons_router
from .roi import router as roi_router
from .youtube_report import router as youtube_report_router

__all__ = [
    "chat_router",
    "campaigns_router",
    "crons_router",
    "roi_router",
    "youtube_report_router",
]
