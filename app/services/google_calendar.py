from datetime import datetime, timedelta

from googleapiclient.discovery import build

from app.config import get_settings
from app.models import FollowupPayload
from app.services.google_auth import google_auth_service


class GoogleCalendarService:
    """Creates follow-up events on Google Calendar."""

    FOLLOWUP_DURATION_MINUTES = 30

    def __init__(self):
        self.settings = get_settings()

    def _get_service(self):
        creds = google_auth_service.get_credentials()
        if not creds:
            raise RuntimeError("Google not authenticated. Visit /auth/login first.")
        return build("calendar", "v3", credentials=creds)

    async def create_followup(self, payload: FollowupPayload) -> dict:
        """Create a 30-minute follow-up event."""
        service = self._get_service()

        start_dt = datetime.fromisoformat(payload.followup_datetime)
        end_dt = start_dt + timedelta(minutes=self.FOLLOWUP_DURATION_MINUTES)

        description_parts = [f"Eczane: {payload.pharmacy_name}"]
        if payload.notes:
            description_parts.append(f"Not: {payload.notes}")

        event_body = {
            "summary": f"Takip Araması — {payload.pharmacy_name}",
            "description": "\n".join(description_parts),
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": "Europe/Istanbul",
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": "Europe/Istanbul",
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 15},
                ],
            },
        }

        event = (
            service.events()
            .insert(calendarId=self.settings.google_calendar_id, body=event_body)
            .execute()
        )

        return {
            "event_id": event.get("id"),
            "html_link": event.get("htmlLink"),
            "start": start_dt.isoformat(),
            "end": end_dt.isoformat(),
        }


calendar_service = GoogleCalendarService()
