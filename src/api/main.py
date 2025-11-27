"""Main FastAPI application for receipt scanning service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import settings
from src.api.routes import scan

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Online receipt scanning API with automatic cropping, deskewing, and OCR",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(scan.router, prefix="/api/v1", tags=["scan"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Receipt Scanner API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
