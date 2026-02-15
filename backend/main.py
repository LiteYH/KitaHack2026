from contextlib import asynccontextmanager
import logging
import os
import sys
import warnings

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load settings first to get API keys
from app.core.config import settings

# Set GOOGLE_API_KEY in environment BEFORE any langchain imports
# This prevents langchain from trying to auto-detect Vertex AI
if settings.google_api_key:
    os.environ["GOOGLE_API_KEY"] = settings.google_api_key
from app.core.firebase import initialize_firebase, get_db
from app.api.v1 import api_router
from app.services import CronService, monitoring_service
from app.services.multi_agent_service import multi_agent_service
from app.services.competitor_agent_service import competitor_agent_service

# Suppress LangChain internal warnings that aren't actual errors
# These are deprecation notices and package availability checks
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain")
warnings.filterwarnings("ignore", message=".*langchain-google-vertexai.*")
warnings.filterwarnings("ignore", message=".*ChatVertexAI.*")

# Configure logging to output to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Global cron service instance
cron_service_instance = None


# Initialize Firebase and CronService on startup using lifespan event
@asynccontextmanager
async def lifespan(app: FastAPI):
    global cron_service_instance
    
    # Startup
    initialize_firebase()
    logger.info("✅ Firebase initialized")
    
    # Initialize CronService
    try:
        db = get_db()
        cron_service_instance = CronService(
            firestore_client=db,
            monitoring_service=monitoring_service,
            competitor_agent_service=competitor_agent_service
        )
        logger.info("✅ CronService initialized")
        
        # Start the scheduler
        await cron_service_instance.start()
        logger.info("✅ APScheduler started")
        
        # Load active jobs from Firestore
        await cron_service_instance.load_jobs_on_startup()
        logger.info("✅ Active monitoring jobs loaded")
        
        # Inject services into multi_agent_service singleton
        multi_agent_service.set_services(
            cron_service=cron_service_instance,
            firestore_client=db,
        )
        logger.info("✅ Services injected into multi_agent_service")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        # Don't fail startup, just log the error
    
    print("🚀 BossolutionAI API is ready!")
    yield
    
    # Shutdown (cleanup)
    if cron_service_instance:
        cron_service_instance.shutdown()
        logger.info("✅ CronService shut down gracefully")


app = FastAPI(
    title=settings.project_name,
    description="BossolutionAI - AI-Powered Marketing and Advertisement API for SMEs",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js default
        "http://localhost:3001",  # Your current frontend port
        "http://localhost:5173",  # Vite default
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"], summary="Service health check")
def health_check():
    return {"status": "ok", "environment": settings.environment}


# Mount API routers
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    # Allow running `python main.py` for local development.
    # Use --reload with uvicorn for automatic reloads when editing code.
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
