"""
AI Log Monitoring - ML Service
FastAPI application for anomaly detection using Isolation Forest
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from app.api import health, anomaly
from app.services.model_service import ModelService
from app.utils import get_current_timestamp
from app.utils.ingestion_logger import send_log  # ADD

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global model service instance
model_service = None


def _model_dir() -> str:
    """Model storage path: MODEL_PATH (Helm/K8s), MODEL_DIR, or default relative dir."""
    return os.environ.get("MODEL_PATH") or os.environ.get("MODEL_DIR") or "models"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    global model_service

    # Startup
    logger.info("Starting ML Service...")
    model_service = ModelService(model_dir=_model_dir())

    # Try to load existing model
    try:
        model_service.load_model()
        logger.info("Loaded existing model successfully")
        send_log("INFO", "ML Service started — model loaded from disk")  # ADD
    except FileNotFoundError:
        logger.warning("No existing model found. Train a new model using /api/v1/train endpoint")
        send_log("WARN", "ML Service started — no model found, awaiting training")  # ADD
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        send_log("ERROR", f"ML Service startup failed: {str(e)}", {"error": str(e)})  # ADD

    app.state.model_service = model_service
    logger.info("ML Service started successfully")

    yield

    # Shutdown
    logger.info("Shutting down ML Service...")
    send_log("INFO", "ML Service shutting down")  # ADD


# Create FastAPI application
app = FastAPI(
    title="AI Log Monitoring - ML Service",
    description="Machine Learning service for log anomaly detection",
    version="1.0.0",
    lifespan=lifespan
)


def _get_cors_origins() -> list:
    """Get CORS origins from CORS_ORIGINS env var. Default: allow all."""
    origins = os.getenv("CORS_ORIGINS", "*")
    return [o.strip() for o in origins.split(",")] if origins != "*" else ["*"]


# Configure CORS - use CORS_ORIGINS env var in production to restrict origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(anomaly.router, prefix="/api/v1", tags=["Anomaly Detection"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Log Monitoring - ML Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": get_current_timestamp()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

# Made with Bob