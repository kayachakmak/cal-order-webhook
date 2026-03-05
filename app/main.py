import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, webhook
from app.services.google_auth import google_auth_service

# ── Logging ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ElevenLabs Webhook Server")

    if google_auth_service.is_authenticated():
        logger.info("Google OAuth: authenticated ✓")
    else:
        logger.warning("Google OAuth: NOT authenticated — visit /auth/login")

    yield
    logger.info("Shutting down")


# ── App ─────────────────────────────────────────────────────────
app = FastAPI(
    title="ElevenLabs Warehouse Agent — Webhook Server",
    description=(
        "Receives webhook calls from an ElevenLabs outbound sales agent. "
        "Logs pharmacy orders to Google Sheets and schedules follow-up "
        "calls on Google Calendar."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow ElevenLabs and local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(webhook.router)


# ── Health check ────────────────────────────────────────────────
@app.get("/health", tags=["system"])
async def health():
    return {
        "status": "healthy",
        "google_authenticated": google_auth_service.is_authenticated(),
    }
