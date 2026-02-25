"""
API v1 routers package.
"""
from .chat import router as chat_router
from .campaigns import router as campaigns_router

# Note: Simple chat router removed - all chat now goes through multi-agent system

__all__ = ["chat_router", "campaigns_router"]
