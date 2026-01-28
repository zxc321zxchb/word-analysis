"""FastAPI application entry point."""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.doc_analysis.config import settings
from src.doc_analysis.api import routes
from src.doc_analysis.logger import setup_logging, get_logger
from src.doc_analysis.db.session import init_db


setup_logging()
logger = get_logger(__name__)

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
    logger.info("Starting Document Analysis Service")
    init_db()
    logger.info("Database tables initialized")
