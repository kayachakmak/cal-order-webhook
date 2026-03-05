import logging
from fastapi import APIRouter, Header, HTTPException, Depends

from app.config import get_settings, Settings
from app.models import OrderPayload, FollowupPayload, WebhookResponse
from app.services.google_sheets import sheets_service
from app.services.google_calendar import calendar_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook", tags=["webhook"])


async def verify_webhook_secret(
    x_webhook_secret: str = Header(None),
    settings: Settings = Depends(get_settings),
):
    """Verify the webhook request comes from ElevenLabs."""
    if not x_webhook_secret or x_webhook_secret != settings.webhook_secret:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")


# ── Log order to Google Sheets ──────────────────────────────────
@router.post("/log-order", response_model=WebhookResponse)
async def log_order(
    payload: OrderPayload,
    _: None = Depends(verify_webhook_secret),
):
    """
    Called by the ElevenLabs agent to log a pharmacy order.
    Appends a row to the configured Google Sheet.
    """
    logger.info(f"Order received: {payload.pharmacy_name}")

    try:
        result = await sheets_service.append_order(payload)
        logger.info(f"Order logged: {result['updated_range']}")
        return WebhookResponse(
            success=True,
            message=f"Sipariş kaydedildi: {payload.pharmacy_name}",
            data=result,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to log order: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Sheet write failed: {str(e)}")


# ── Schedule follow-up on Google Calendar ───────────────────────
@router.post("/schedule-followup", response_model=WebhookResponse)
async def schedule_followup(
    payload: FollowupPayload,
    _: None = Depends(verify_webhook_secret),
):
    """
    Called by the ElevenLabs agent to schedule a follow-up call.
    Creates a 30-minute event on Google Calendar.
    """
    logger.info(f"Follow-up requested: {payload.pharmacy_name} at {payload.followup_datetime}")

    try:
        result = await calendar_service.create_followup(payload)
        logger.info(f"Event created: {result['event_id']}")
        return WebhookResponse(
            success=True,
            message=f"Takip araması planlandı: {payload.pharmacy_name}",
            data=result,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Invalid datetime: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to create event: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Calendar write failed: {str(e)}")
