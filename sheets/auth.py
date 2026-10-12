import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]
TOKEN_PATH = Path(__file__).parent.parent / ".google_sheets_token.json"
REDIRECT_PORT = 8080

CLIENT_ID = os.getenv("GOOGLE_SHEETS_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("GOOGLE_SHEETS_CLIENT_SECRET", "")


def _client_config() -> dict:
    return {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [f"http://localhost:{REDIRECT_PORT}/"],
        }
    }


def get_credentials() -> Credentials:
    """Return cached credentials, refreshing or running the interactive
    OAuth consent flow (browser + local callback server) as needed.

    If the cached token was issued for a narrower scope than SCOPES
    (e.g. Sheets-only, before Docs/Drive were added), it's treated as
    stale and a fresh consent flow is triggered automatically.
    """
    creds = None
    stored_scopes = []
    if TOKEN_PATH.exists():
        # Read the scopes Google actually granted directly from the token
        # file — from_authorized_user_file(path, SCOPES) below overrides
        # creds.scopes with whatever SCOPES we pass in, so it can't be used
        # to detect a stale/narrower token; the raw file is the source of truth.
        try:
            stored_scopes = json.loads(TOKEN_PATH.read_text()).get("scopes", [])
        except Exception:
            stored_scopes = []
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    has_all_scopes = bool(stored_scopes) and set(SCOPES).issubset(set(stored_scopes))

    if creds and creds.valid and has_all_scopes:
        return creds

    if creds and creds.expired and creds.refresh_token and has_all_scopes:
        try:
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json())
            return creds
        except RefreshError:
            # Refresh token itself has been revoked/expired (not just the
            # access token) — fall through to a fresh interactive consent
            # flow instead of crashing.
            creds = None

    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError(
            "GOOGLE_SHEETS_CLIENT_ID / GOOGLE_SHEETS_CLIENT_SECRET not set in .env"
        )

    flow = InstalledAppFlow.from_client_config(_client_config(), SCOPES)
    creds = flow.run_local_server(port=REDIRECT_PORT, prompt="consent")
    TOKEN_PATH.write_text(creds.to_json())
    return creds
