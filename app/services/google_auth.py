import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

from app.config import get_settings


class GoogleAuthService:
    """Manages Google OAuth2 tokens with file-based persistence."""

    def __init__(self):
        self.settings = get_settings()
        self._ensure_token_dir()

    def _ensure_token_dir(self):
        Path(self.settings.token_path).parent.mkdir(parents=True, exist_ok=True)

    def _client_config(self) -> dict:
        return {
            "web": {
                "client_id": self.settings.google_client_id,
                "client_secret": self.settings.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [f"{self.settings.app_url}/auth/callback"],
            }
        }

    def get_credentials(self) -> Credentials | None:
        """Load credentials from disk, refreshing if expired."""
        if not os.path.exists(self.settings.token_path):
            return None

        creds = Credentials.from_authorized_user_file(
            self.settings.token_path, self.settings.google_scopes
        )

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            self._save_credentials(creds)

        if creds and creds.valid:
            return creds

        return None

    def create_auth_flow(self) -> Flow:
        """Create a new OAuth2 flow for user authorization."""
        flow = Flow.from_client_config(
            self._client_config(),
            scopes=self.settings.google_scopes,
            redirect_uri=f"{self.settings.app_url}/auth/callback",
        )
        return flow

    def exchange_code(self, code: str) -> Credentials:
        """Exchange authorization code for credentials."""
        flow = self.create_auth_flow()
        flow.fetch_token(code=code)
        creds = flow.credentials
        self._save_credentials(creds)
        return creds

    def _save_credentials(self, creds: Credentials):
        """Persist credentials to disk."""
        with open(self.settings.token_path, "w") as f:
            f.write(creds.to_json())

    def is_authenticated(self) -> bool:
        return self.get_credentials() is not None


# Singleton
google_auth_service = GoogleAuthService()
