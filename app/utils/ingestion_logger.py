# app/utils/ingestion_logger.py

import logging
import os

import httpx

logger = logging.getLogger(__name__)

_INGESTION_URL = os.getenv(
    "LOG_INGESTION_URL",
    "http://log-ingestion-service.ai-monitoring.svc.cluster.local:8081"
)
_ENABLED = os.getenv("LOG_INGESTION_ENABLED", "true").lower() == "true"


def send_log(level: str, message: str, metadata: dict = None):
    """Ship a structured log entry to the ingestion service.
    Fails silently — never interrupts ML service operation.
    """
    if not _ENABLED:
        return

    try:
        httpx.post(
            f"{_INGESTION_URL}/api/v1/logs",
            json={
                "level": level,
                "message": message,
                "service": "isolation-forest-ml",
                "environment": os.getenv("APP_ENV", "local"),
                "metadata": metadata or {},
            },
            timeout=2.0,
            verify=False,
        )
    except Exception as e:
        # Log locally but never propagate — logging must never break predictions
        logger.warning(f"Ingestion logger failed (non-fatal): {e}")
