"""Google Search Console API client for Hermes Agent.

Two auth modes supported, priority in this order:
  1. OAuth2 user-consent via refresh_token (.gsc_token.json) — produced by
     oauth_setup.py. Recommended since the Google bug from 2026-04-23 that
     prevents adding a service account as a GSC user.
  2. Service account JSON (legacy), with or without impersonation
     (`with_subject`). Impersonation requires Google Workspace
     Domain-Wide Delegation configured — incompatible with standard Gmail.

Active mode is determined automatically: if GSC_TOKEN_PATH
(or ./.gsc_token.json) exists, the refresh_token is used. Otherwise
falls back to service account.
"""

from __future__ import annotations

import datetime as dt
import json
import logging
import os
import time
from typing import Optional

from google.auth.exceptions import RefreshError
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials as OAuth2Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

GSC_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
DEFAULT_CREDENTIALS_PATH = "hermes-496211-410f33188b58.json"
DEFAULT_TOKEN_PATH = ".gsc_token.json"


class GSCAuthError(Exception):
    """GSC authentication or permission error."""


class GSCRateLimitError(Exception):
    """GSC API quota exceeded after retries."""


class GSCAPIError(Exception):
    """Other GSC API HTTP error."""


def _load_oauth_credentials(token_path: str) -> OAuth2Credentials:
    """Rebuilds OAuth2 user Credentials from the
    `.gsc_token.json` file produced by oauth_setup.py."""
    try:
        with open(token_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except OSError as e:
        raise GSCAuthError(f"GSC token unreadable ({token_path}): {e}") from e
    except json.JSONDecodeError as e:
        raise GSCAuthError(f"GSC token malformed ({token_path}): {e}") from e

    required = ("refresh_token", "client_id", "client_secret")
    missing = [k for k in required if not payload.get(k)]
    if missing:
        raise GSCAuthError(
            f"GSC token incomplete — missing fields: {missing}. "
            f"Re-run oauth_setup.py."
        )

    return OAuth2Credentials(
        token=None,
        refresh_token=payload["refresh_token"],
        token_uri=payload.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=payload["client_id"],
        client_secret=payload["client_secret"],
        scopes=payload.get("scopes", GSC_SCOPES),
    )


def _build_service(impersonate_email: Optional[str] = None,
                   credentials_path: Optional[str] = None,
                   token_path: Optional[str] = None):
    """Builds an authenticated GSC client.

    Priority: (1) refresh_token via .gsc_token.json if present,
              (2) service account JSON (with or without impersonation).
    """
    token = token_path or os.environ.get("GSC_TOKEN_PATH", DEFAULT_TOKEN_PATH)
    sa_path = credentials_path or os.environ.get(
        "GSC_CREDENTIALS_PATH", DEFAULT_CREDENTIALS_PATH
    )

    if os.path.isfile(token):
        creds = _load_oauth_credentials(token)
        logger.info("GSC auth: OAuth2 refresh_token (%s)", token)
        try:
            return build(
                "searchconsole", "v1", credentials=creds, cache_discovery=False
            )
        except Exception as e:
            raise GSCAuthError(f"Build GSC service (OAuth) failed: {e}") from e

    if not os.path.isfile(sa_path):
        raise GSCAuthError(
            f"Neither OAuth token ({token}) nor service account ({sa_path}) found. "
            "Run oauth_setup.py or provide GSC_CREDENTIALS_PATH."
        )

    try:
        creds = service_account.Credentials.from_service_account_file(
            sa_path, scopes=GSC_SCOPES
        )
        if impersonate_email:
            creds = creds.with_subject(impersonate_email)
        logger.info(
            "GSC auth: service account (%s)%s",
            sa_path,
            f" impersonating {impersonate_email}" if impersonate_email else "",
        )
        return build(
            "searchconsole", "v1", credentials=creds, cache_discovery=False
        )
    except GSCAuthError:
        raise
    except Exception as e:
        raise GSCAuthError(f"GSC auth (SA) failed: {e}") from e


def get_search_analytics(
    site_url: str,
    start_date: str,
    end_date: str,
    dimensions: Optional[list[str]] = None,
    row_limit: int = 1000,
    impersonate_email: Optional[str] = None,
    credentials_path: Optional[str] = None,
    token_path: Optional[str] = None,
    max_retries: int = 5,
) -> dict:
    """Fetches GSC Search Analytics data.

    Args:
        site_url: property identifier, either `sc-domain:<domain>`
            (Domain property) or `https://<domain>/` (URL-prefix property).
        start_date / end_date: ISO format `YYYY-MM-DD`.
        dimensions: among `query`, `page`, `country`, `device`,
            `searchAppearance`, `date`. Default: `["query", "page"]`.
        row_limit: max 25,000 per request (GSC API).
        impersonate_email: account to impersonate via Domain-Wide Delegation.
            Set `None` if the service account is added directly as a property
            user.
        credentials_path: override JSON path (otherwise env
            `GSC_CREDENTIALS_PATH` then module default).
        max_retries: number of attempts on rate-limit (exp backoff).

    Returns:
        Raw dict returned by `searchanalytics().query()`, containing
        notably `rows: [{keys, clicks, impressions, ctr, position}, ...]`.
    """
    dimensions = dimensions or ["query", "page"]
    service = _build_service(
        impersonate_email=impersonate_email,
        credentials_path=credentials_path,
        token_path=token_path,
    )
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": dimensions,
        "rowLimit": row_limit,
    }
    for attempt in range(1, max_retries + 1):
        try:
            return (
                service.searchanalytics()
                .query(siteUrl=site_url, body=body)
                .execute()
            )
        except RefreshError as e:
            raise GSCAuthError(f"GSC token refresh failed: {e}") from e
        except HttpError as e:
            status = getattr(e.resp, "status", None) if hasattr(e, "resp") else None
            msg = str(e)
            is_rate_limit = status == 429 or (
                status == 403 and ("rateLimitExceeded" in msg or "userRateLimitExceeded" in msg)
            )
            if is_rate_limit:
                if attempt == max_retries:
                    raise GSCRateLimitError(
                        f"GSC rate-limit after {max_retries} attempts: {e}"
                    ) from e
                wait = min(2 ** attempt, 60)
                logger.warning(
                    "GSC rate-limit attempt %d/%d, retry in %ds",
                    attempt, max_retries, wait,
                )
                time.sleep(wait)
                continue
            if status in (401, 403):
                raise GSCAuthError(
                    f"GSC auth/permission ({status}): {e}"
                ) from e
            raise GSCAPIError(f"GSC API error ({status}): {e}") from e


def list_sites(impersonate_email: Optional[str] = None,
               credentials_path: Optional[str] = None,
               token_path: Optional[str] = None) -> list[dict]:
    """Lists properties accessible to the authenticated account."""
    service = _build_service(
        impersonate_email=impersonate_email,
        credentials_path=credentials_path,
        token_path=token_path,
    )
    try:
        resp = service.sites().list().execute()
        return resp.get("siteEntry", [])
    except RefreshError as e:
        raise GSCAuthError(f"GSC token refresh failed: {e}") from e
    except HttpError as e:
        status = getattr(e.resp, "status", None) if hasattr(e, "resp") else None
        if status in (401, 403):
            raise GSCAuthError(f"GSC auth/permission ({status}): {e}") from e
        raise GSCAPIError(f"GSC API error ({status}): {e}") from e


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    site = os.environ.get("GSC_SITE_URL", "sc-domain:<your_domain>.com")
    impersonate = os.environ.get("GSC_IMPERSONATE_EMAIL") or None
    token_path = os.environ.get("GSC_TOKEN_PATH", DEFAULT_TOKEN_PATH)
    sa_path = os.environ.get("GSC_CREDENTIALS_PATH", DEFAULT_CREDENTIALS_PATH)

    if os.path.isfile(token_path):
        auth_mode = f"OAuth2 refresh_token ({token_path})"
    elif os.path.isfile(sa_path):
        auth_mode = f"Service Account ({sa_path})"
        if impersonate:
            auth_mode += f" impersonating {impersonate}"
    else:
        auth_mode = "NONE — no credential available"

    today = dt.date.today()
    start = (today - dt.timedelta(days=30)).isoformat()
    end = today.isoformat()

    print(f"GSC fetch — site={site}  period={start}→{end}")
    print(f"Auth: {auth_mode}")
    print()

    try:
        data = get_search_analytics(
            site_url=site,
            start_date=start,
            end_date=end,
            dimensions=["query"],
            row_limit=10,
            impersonate_email=impersonate,
            token_path=token_path,
            credentials_path=sa_path,
        )
    except GSCAuthError as e:
        msg = str(e)
        print(f"AUTH ERROR — {e}")
        print()
        if "unauthorized_client" in msg:
            print("Diagnosis: Domain-Wide Delegation not operational.")
            print(f"  The account {impersonate!r} is probably not in a")
            print("  Google Workspace, or DWD is not configured for this SA.")
            print("  → Recommended: use OAuth2 user-consent flow.")
            print("    Run oauth_setup.py to generate .gsc_token.json.")
        elif "403" in msg or "forbidden" in msg.lower() or "sufficient permission" in msg.lower():
            print("Diagnosis: 403 Forbidden — the authenticated account has no")
            print(f"  access to the property {site!r}.")
            print("  → If you're using the service account: add its email to the")
            print("    property (but Google bug known since 2026-04-23 →")
            print("    prefer OAuth user-consent via oauth_setup.py).")
            print("  → If you're using OAuth: check that the account that authorized")
            print("    is indeed the owner of the GSC property.")
        elif "invalid_grant" in msg.lower():
            print("Diagnosis: refresh_token invalid or revoked.")
            print("  → Run oauth_setup.py to generate a new one.")
        else:
            print("Diagnosis: see message above.")
        raise SystemExit(1)
    except GSCRateLimitError as e:
        print(f"RATE LIMIT — {e}")
        raise SystemExit(2)
    except GSCAPIError as e:
        print(f"API ERROR — {e}")
        raise SystemExit(3)

    rows = data.get("rows", [])
    if not rows:
        print("(No data — the property may not have GSC history yet,")
        print(" or no query generated impressions over the period.)")
        raise SystemExit(0)

    print(f"Top {len(rows)} queries (last 30 days) on {site}")
    print()
    print(f"{'Query':<42} {'Clicks':>7} {'Impr.':>8} {'CTR':>7} {'Pos.':>6}")
    print("-" * 74)
    for r in rows:
        query = r["keys"][0] if r.get("keys") else "(none)"
        clicks = r.get("clicks", 0)
        impr = r.get("impressions", 0)
        ctr = r.get("ctr", 0) * 100
        pos = r.get("position", 0)
        print(f"{query[:42]:<42} {int(clicks):>7} {int(impr):>8} {ctr:>6.1f}% {pos:>6.1f}")
