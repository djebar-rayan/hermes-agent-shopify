"""Google Search Console API client for Hermes Agent.

Deux modes d'auth supportés, priorité dans cet ordre:
  1. OAuth2 user-consent via refresh_token (.gsc_token.json) — produit par
     oauth_setup.py. Recommandé depuis le bug Google du 23/04/2026 qui
     empêche d'ajouter un service account comme utilisateur GSC.
  2. Service account JSON (legacy), avec ou sans impersonation
     (`with_subject`). L'impersonation nécessite Google Workspace
     Domain-Wide Delegation configurée — incompatible Gmail standard.

Le mode actif est déterminé automatiquement : si GSC_TOKEN_PATH
(ou ./.gsc_token.json) existe, le refresh_token est utilisé. Sinon
fallback service account.
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
    """Erreur d'authentification ou de permission GSC."""


class GSCRateLimitError(Exception):
    """Quota API GSC dépassé après retries."""


class GSCAPIError(Exception):
    """Autre erreur HTTP de l'API GSC."""


def _load_oauth_credentials(token_path: str) -> OAuth2Credentials:
    """Reconstruit des Credentials OAuth2 user à partir du fichier
    `.gsc_token.json` produit par oauth_setup.py."""
    try:
        with open(token_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except OSError as e:
        raise GSCAuthError(f"Token GSC illisible ({token_path}): {e}") from e
    except json.JSONDecodeError as e:
        raise GSCAuthError(f"Token GSC mal formé ({token_path}): {e}") from e

    required = ("refresh_token", "client_id", "client_secret")
    missing = [k for k in required if not payload.get(k)]
    if missing:
        raise GSCAuthError(
            f"Token GSC incomplet — champs manquants: {missing}. "
            f"Relance oauth_setup.py."
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
    """Construit un client GSC authentifié.

    Priorité: (1) refresh_token via .gsc_token.json si présent,
              (2) service account JSON (avec ou sans impersonation).
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
            f"Ni token OAuth ({token}) ni service account ({sa_path}) trouvés. "
            "Lance oauth_setup.py ou fournis GSC_CREDENTIALS_PATH."
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
        raise GSCAuthError(f"Auth GSC (SA) failed: {e}") from e


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
    """Récupère les données Search Analytics GSC.

    Args:
        site_url: identifiant de la propriété, soit `sc-domain:<domain>`
            (Domain property) soit `https://<domain>/` (URL-prefix property).
        start_date / end_date: format ISO `YYYY-MM-DD`.
        dimensions: parmi `query`, `page`, `country`, `device`,
            `searchAppearance`, `date`. Défaut: `["query", "page"]`.
        row_limit: max 25 000 par requête (API GSC).
        impersonate_email: compte à impersonner via Domain-Wide Delegation.
            Mettre `None` si le service account est ajouté directement
            comme utilisateur de la propriété.
        credentials_path: override du chemin du JSON (sinon env
            `GSC_CREDENTIALS_PATH` puis défaut module).
        max_retries: nombre de tentatives en cas de rate-limit (backoff exp).

    Returns:
        Le dict brut renvoyé par `searchanalytics().query()`, contenant
        notamment `rows: [{keys, clicks, impressions, ctr, position}, ...]`.
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
            raise GSCAuthError(f"Token refresh GSC échoué: {e}") from e
        except HttpError as e:
            status = getattr(e.resp, "status", None) if hasattr(e, "resp") else None
            msg = str(e)
            is_rate_limit = status == 429 or (
                status == 403 and ("rateLimitExceeded" in msg or "userRateLimitExceeded" in msg)
            )
            if is_rate_limit:
                if attempt == max_retries:
                    raise GSCRateLimitError(
                        f"Rate-limit GSC après {max_retries} tentatives: {e}"
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
                    f"Auth/permission GSC ({status}): {e}"
                ) from e
            raise GSCAPIError(f"Erreur API GSC ({status}): {e}") from e


def list_sites(impersonate_email: Optional[str] = None,
               credentials_path: Optional[str] = None,
               token_path: Optional[str] = None) -> list[dict]:
    """Liste les propriétés accessibles au compte authentifié."""
    service = _build_service(
        impersonate_email=impersonate_email,
        credentials_path=credentials_path,
        token_path=token_path,
    )
    try:
        resp = service.sites().list().execute()
        return resp.get("siteEntry", [])
    except RefreshError as e:
        raise GSCAuthError(f"Token refresh GSC échoué: {e}") from e
    except HttpError as e:
        status = getattr(e.resp, "status", None) if hasattr(e, "resp") else None
        if status in (401, 403):
            raise GSCAuthError(f"Auth/permission GSC ({status}): {e}") from e
        raise GSCAPIError(f"Erreur API GSC ({status}): {e}") from e


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
        auth_mode = "NONE — aucun credential disponible"

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
            print("Diagnostic: Domain-Wide Delegation non opérationnelle.")
            print(f"  Le compte {impersonate!r} n'est probablement pas dans un")
            print("  Google Workspace, ou la DWD n'est pas configurée pour ce SA.")
            print("  → Recommandé: utiliser le flow OAuth2 user-consent.")
            print("    Lance oauth_setup.py pour générer .gsc_token.json.")
        elif "403" in msg or "forbidden" in msg.lower() or "sufficient permission" in msg.lower():
            print("Diagnostic: 403 Forbidden — le compte authentifié n'a pas")
            print(f"  accès à la propriété {site!r}.")
            print("  → Si tu utilises le service account: ajoute son email à la")
            print("    propriété (mais bug Google connu depuis 23/04/2026 →")
            print("    préfère OAuth user-consent via oauth_setup.py).")
            print("  → Si tu utilises OAuth: vérifie que le compte ayant autorisé")
            print("    est bien propriétaire de la propriété GSC.")
        elif "invalid_grant" in msg.lower():
            print("Diagnostic: refresh_token invalide ou révoqué.")
            print("  → Relance oauth_setup.py pour en générer un nouveau.")
        else:
            print("Diagnostic: voir le message ci-dessus.")
        raise SystemExit(1)
    except GSCRateLimitError as e:
        print(f"RATE LIMIT — {e}")
        raise SystemExit(2)
    except GSCAPIError as e:
        print(f"API ERROR — {e}")
        raise SystemExit(3)

    rows = data.get("rows", [])
    if not rows:
        print("(Aucune donnée — la propriété n'a peut-être pas encore d'historique GSC,")
        print(" ou aucune requête n'a généré d'impression sur la période.)")
        raise SystemExit(0)

    print(f"Top {len(rows)} requêtes (30 derniers jours) sur {site}")
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
