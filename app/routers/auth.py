from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.services.google_auth import google_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login():
    """Redirect to Google OAuth consent screen."""
    flow = google_auth_service.create_auth_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def callback(code: str = None, error: str = None):
    """Handle OAuth callback from Google."""
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code received")

    try:
        google_auth_service.exchange_code(code)
        return {
            "success": True,
            "message": "Google authentication successful. You can now use the webhooks.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token exchange failed: {str(e)}")


@router.get("/status")
async def status():
    """Check if Google OAuth is active."""
    authenticated = google_auth_service.is_authenticated()
    return {
        "authenticated": authenticated,
        "message": "Ready" if authenticated else "Not authenticated. Visit /auth/login",
    }
