from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# ── Product catalog ──────────────────────────────────────────────
PRODUCTS = {
    "d_vitamini": "D-VİTAMİNİ HIZLI TEST KASETİ",
    "ovulasyon": "OVULASYON HIZLI TEST KASETİ",
    "dijital_gebelik": "DİJİTAL GEBELİK TESTİ",
}

SHEET_HEADERS = [
    "Tarih",
    "Eczane Adı",
    "Telefon",
    "D-Vitamini Test (adet)",
    "Ovulasyon Test (adet)",
    "Dijital Gebelik Testi (adet)",
    "Toplam Adet",
    "Notlar",
]


# ── Webhook payloads ────────────────────────────────────────────
class OrderPayload(BaseModel):
    """Payload sent by ElevenLabs agent when logging a pharmacy order."""

    pharmacy_name: str = Field(..., description="Name of the pharmacy")
    pharmacy_phone: Optional[str] = Field(None, description="Phone number")
    d_vitamini: int = Field(0, ge=0, description="Qty: D-Vitamini Hızlı Test Kaseti")
    ovulasyon: int = Field(0, ge=0, description="Qty: Ovulasyon Hızlı Test Kaseti")
    dijital_gebelik: int = Field(0, ge=0, description="Qty: Dijital Gebelik Testi")
    notes: Optional[str] = Field(None, description="Additional notes from the call")


class FollowupPayload(BaseModel):
    """Payload sent by ElevenLabs agent when scheduling a follow-up."""

    pharmacy_name: str = Field(..., description="Name of the pharmacy")
    pharmacy_phone: Optional[str] = Field(None, description="Phone number")
    followup_datetime: str = Field(
        ..., description="ISO 8601 datetime for the follow-up call"
    )
    notes: Optional[str] = Field(None, description="Context for the follow-up")


# ── Response models ─────────────────────────────────────────────
class WebhookResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
