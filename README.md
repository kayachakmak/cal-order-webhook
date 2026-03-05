# ElevenLabs Agent Webhook Server

FastAPI webhook server for ElevenLabs conversational AI agent.  
Handles outbound sales calls for a warehouse — logs orders to Google Sheets and creates follow-up events on Google Calendar.

## Products
| Product | Key |
|---|---|
| D-VİTAMİNİ HIZLI TEST KASETİ | `d_vitamini` |
| OVULASYON HIZLI TEST KASETİ | `ovulasyon` |
| DİJİTAL GEBELİK TESTİ | `dijital_gebelik` |

## Architecture

```
ElevenLabs Agent ──webhook──▶ FastAPI Server (Docker)
                                  ├──▶ Google Sheets (order log)
                                  └──▶ Google Calendar (follow-up event)
```

## Quick Start

### 1. Google Cloud Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable **Google Sheets API** and **Google Calendar API**
3. Create **OAuth 2.0 Client ID** (Web application)
4. Add `https://webhook.yourdomain.com/auth/callback` to **Authorized redirect URIs**
5. Download the credentials JSON

### 2. Configure Environment
```bash
cp .env.example .env
```
Edit `.env` with your values:
- `GOOGLE_CLIENT_ID` — from your OAuth credentials
- `GOOGLE_CLIENT_SECRET` — from your OAuth credentials
- `GOOGLE_SHEET_ID` — the ID from your Google Sheet URL
- `GOOGLE_CALENDAR_ID` — usually your email, or a specific calendar ID
- `WEBHOOK_SECRET` — a random string to verify ElevenLabs requests
- `DOMAIN` — your public domain (e.g. `webhook.yourdomain.com`)
- `APP_URL` — full URL with https (e.g. `https://webhook.yourdomain.com`)

### 3. Run with Docker (behind Traefik)
```bash
docker compose up --build -d
```
Traefik will automatically:
- Route traffic from your domain to the container
- Provision a Let's Encrypt TLS certificate
- Redirect HTTP → HTTPS

### 4. Authenticate Google
Open `https://webhook.yourdomain.com/auth/login` in your browser and complete the OAuth flow.  
Tokens are persisted in a Docker volume so you only do this once.

### 5. Configure ElevenLabs Agent
In your ElevenLabs agent, add two **Server Tools**:

#### Tool 1: `log_order`
- **URL:** `https://your-domain.com/webhook/log-order`
- **Method:** POST
- **Description:** Log a pharmacy order to the spreadsheet
- **Parameters:**
  - `pharmacy_name` (string, required) — Name of the pharmacy
  - `pharmacy_phone` (string, optional) — Phone number
  - `d_vitamini` (integer, optional, default 0) — Quantity of D-Vitamini Hızlı Test Kaseti
  - `ovulasyon` (integer, optional, default 0) — Quantity of Ovulasyon Hızlı Test Kaseti
  - `dijital_gebelik` (integer, optional, default 0) — Quantity of Dijital Gebelik Testi

#### Tool 2: `schedule_followup`
- **URL:** `https://your-domain.com/webhook/schedule-followup`
- **Method:** POST
- **Description:** Schedule a follow-up call with the pharmacy
- **Parameters:**
  - `pharmacy_name` (string, required) — Name of the pharmacy
  - `pharmacy_phone` (string, optional) — Phone number
  - `followup_datetime` (string, required) — ISO 8601 datetime for the follow-up

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/auth/login` | Start Google OAuth flow |
| `GET` | `/auth/callback` | OAuth callback |
| `GET` | `/auth/status` | Check auth status |
| `POST` | `/webhook/log-order` | Log order to Google Sheets |
| `POST` | `/webhook/schedule-followup` | Create follow-up calendar event |

## Environment Variables

| Variable | Description | Required |
|---|---|---|
| `GOOGLE_CLIENT_ID` | OAuth 2.0 Client ID | ✅ |
| `GOOGLE_CLIENT_SECRET` | OAuth 2.0 Client Secret | ✅ |
| `GOOGLE_SHEET_ID` | Target Google Sheet ID | ✅ |
| `GOOGLE_CALENDAR_ID` | Target Calendar ID | ✅ |
| `WEBHOOK_SECRET` | Secret to verify webhook calls | ✅ |
| `DOMAIN` | Public domain (used in Traefik labels) | ✅ |
| `APP_URL` | Full public URL with https | ✅ |
| `TOKEN_PATH` | Path to store OAuth tokens | `/data/token.json` |
# cal-order-webhook
