from datetime import datetime

from googleapiclient.discovery import build

from app.config import get_settings
from app.models import OrderPayload, SHEET_HEADERS
from app.services.google_auth import google_auth_service


class GoogleSheetsService:
    """Writes order data to Google Sheets."""

    def __init__(self):
        self.settings = get_settings()

    def _get_service(self):
        creds = google_auth_service.get_credentials()
        if not creds:
            raise RuntimeError("Google not authenticated. Visit /auth/login first.")
        return build("sheets", "v4", credentials=creds)

    async def ensure_headers(self):
        """Create headers row if the sheet is empty."""
        service = self._get_service()
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=self.settings.google_sheet_id, range="A1:F1")
            .execute()
        )
        values = result.get("values", [])

        if not values:
            service.spreadsheets().values().update(
                spreadsheetId=self.settings.google_sheet_id,
                range="A1:F1",
                valueInputOption="RAW",
                body={"values": [SHEET_HEADERS]},
            ).execute()

    async def append_order(self, order: OrderPayload) -> dict:
        """Append an order row to the sheet."""
        await self.ensure_headers()

        service = self._get_service()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = [
            now,
            order.pharmacy_name,
            order.d_vitamini,
            order.ovulasyon,
            order.dijital_gebelik,
            order.notes or "",
        ]

        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=self.settings.google_sheet_id,
                range="A:F",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": [row]},
            )
            .execute()
        )

        return {
            "updated_range": result.get("updates", {}).get("updatedRange", ""),
            "row_data": dict(zip(SHEET_HEADERS, row)),
        }


sheets_service = GoogleSheetsService()
