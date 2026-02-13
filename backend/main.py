from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers import items
from app.core.config import settings
from app.core.firebase import initialize_firebase

app = FastAPI(
    title=settings.project_name,
    description="BossolutionAI - AI-Powered Marketing and Advertisement API for SMEs",
    version="1.0.0",
)

# Initialize Firebase on startup
@app.on_event("startup")
async def startup_event():
    initialize_firebase()
    print("🚀 BossolutionAI API is ready!")

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
app.include_router(items.router, prefix="/api/v1")


if __name__ == "__main__":
    # Allow running `python main.py` for local development.
    # Use --reload with uvicorn for automatic reloads when editing code.
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
