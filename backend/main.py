from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.firebase import initialize_firebase
from app.api.v1 import api_router


# Initialize Firebase on startup using lifespan event
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_firebase()
    print("🚀 BossolutionAI API is ready!")
    yield
    # Shutdown (cleanup if needed)
    pass


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

# Serve generated images statically for hackathon (local development)
app.mount("/generated_images", StaticFiles(directory="generated_images"), name="generated_images")


if __name__ == "__main__":
    # Allow running `python main.py` for local development.
    # Use --reload with uvicorn for automatic reloads when editing code.
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
