"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.services.milvus_client import connect_milvus, get_collection
from app.api.chat import router as chat_router
from app.api.document import router as document_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: startup and shutdown events."""
    settings = get_settings()
    logger.info("=" * 50)
    logger.info("HRAgent Backend Starting...")
    logger.info(f"Environment: {settings.app_env}")

    # Initialize database tables
    await init_db()
    logger.info("Database tables initialized")

    # Connect to Milvus and ensure collection exists
    connect_milvus()
    get_collection()
    logger.info("Milvus collection ready")

    logger.info("HRAgent Backend Started Successfully!")
    logger.info("=" * 50)

    yield

    logger.info("HRAgent Backend Shutting down...")


app = FastAPI(
    title="HRAgent API",
    description="员工手册 / HR 政策智能问答系统 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat_router)
app.include_router(document_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "HRAgent"}
