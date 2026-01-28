"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.doc_analysis.config import settings
from src.doc_analysis.api import routes

# Create FastAPI app
app = FastAPI(
    title="Document Analysis Service",
    description="Word document parsing service with numbered sections extraction",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(routes.router)

# Root endpoint
@app.get("/")
def root():
    """Root endpoint."""
    return {
        "service": "Document Analysis Service",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "api": settings.api_prefix,
            "docs": "/docs",
        },
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    import logging
    logging.basicConfig(level=settings.log_level)
    logger = logging.getLogger(__name__)
    logger.info("Starting Document Analysis Service")
