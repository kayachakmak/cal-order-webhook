# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI webhook server for ElevenLabs conversational AI agent. Handles outbound sales calls for a warehouse - logs pharmacy orders to Google Sheets and creates follow-up calendar events.

## Commands

```bash
# Run with Docker (production)
docker compose up --build -d

# Run locally (development)
uvicorn app.main:app --reload --port 8000

# Install dependencies
pip install -r requirements.txt
```

## Architecture

```
ElevenLabs Agent ──webhook──▶ FastAPI Server
                                  ├──▶ Google Sheets (order log)
                                  └──▶ Google Calendar (follow-up event)
```

### Key Components

- **app/main.py** - FastAPI app with CORS middleware and lifespan handler
- **app/config.py** - Pydantic Settings loading from `.env`
- **app/models.py** - Request/response models and product catalog (PRODUCTS dict)
- **app/routers/webhook.py** - Two endpoints: `/webhook/log-order` and `/webhook/schedule-followup`, both verify `X-Webhook-Secret` header
- **app/routers/auth.py** - Google OAuth flow: `/auth/login`, `/auth/callback`, `/auth/status`
- **app/services/google_auth.py** - Singleton `google_auth_service` manages OAuth tokens with file persistence
- **app/services/google_sheets.py** - Singleton `sheets_service` appends orders to configured spreadsheet
- **app/services/google_calendar.py** - Singleton `calendar_service` creates 30-minute follow-up events (Europe/Istanbul timezone)

### Authentication Flow

1. User visits `/auth/login` → redirects to Google OAuth consent
2. Google redirects to `/auth/callback` with code
3. Token saved to `TOKEN_PATH` (default: `/data/token.json`)
4. All webhook calls require `X-Webhook-Secret` header matching `WEBHOOK_SECRET` env var

### Product Keys

Used in `OrderPayload` for quantities: `d_vitamini`, `ovulasyon`, `dijital_gebelik`
