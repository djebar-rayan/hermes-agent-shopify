"""OAuth2 user-consent flow for Google Search Console — one-time setup script.

Generates a persistent refresh_token for the account that owns the
GSC property. Bypasses the Google bug from 2026-04-23 that prevents
adding a service account as a GSC user ("email not found").

The refresh_token saved in `.gsc_token.json` (chmod 600) lets
`gsc_client.py` authenticate automatically for all future GSC
API calls, without human interaction — ideal for crons.

Google Cloud Console prerequisites (existing or new project):

  1. https://console.cloud.google.com/apis/credentials/consent
     - User Type: External (standard Gmail account) OR Internal (Workspace)
     - App name, support email, developer email
     - Scopes: add `https://www.googleapis.com/auth/webmasters.readonly`
     - Test users: add the account that owns the GSC property
       (otherwise OAuth authorization will be denied while the app
       is in "Testing" mode)

  2. https://console.cloud.google.com/apis/credentials
     - + CREATE CREDENTIALS > OAuth client ID
     - Application type: Desktop app
     - Name: "Hermes GSC OAuth"
     - DOWNLOAD JSON → rename to `client_secret.json` next to this script
       (or provide its path via env GSC_OAUTH_CLIENT_SECRET)

Usage:
  pip install google-auth-oauthlib
  python oauth_setup.py

On launch, a browser opens. Sign in with the account that owns the GSC
property, accept the consent. The script automatically retrieves the
code, exchanges it for a refresh_token, and saves it.

Environment variables:
  GSC_OAUTH_CLIENT_SECRET   path to client_secret.json (default: ./client_secret.json)
  GSC_TOKEN_PATH            path to save the token     (default: ./.gsc_token.json)
"""

from __future__ import annotations

import json
import os
import stat
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

GSC_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
DEFAULT_CLIENT_SECRET = "client_secret.json"
DEFAULT_TOKEN_PATH = ".gsc_token.json"


def main() -> int:
    client_secret = os.environ.get("GSC_OAUTH_CLIENT_SECRET", DEFAULT_CLIENT_SECRET)
    token_path = os.environ.get("GSC_TOKEN_PATH", DEFAULT_TOKEN_PATH)

    if not os.path.isfile(client_secret):
        print(f"ERROR: client_secret not found: {client_secret!r}")
        print()
        print("Create it from Google Cloud Console:")
        print("  1. https://console.cloud.google.com/apis/credentials/consent")
        print("     User Type=External, scopes=webmasters.readonly,")
        print("     test user = account owning the GSC property")
        print("  2. https://console.cloud.google.com/apis/credentials")
        print("     + CREATE CREDENTIALS > OAuth client ID > Desktop app")
        print("     > Download JSON > rename to 'client_secret.json'")
        print(f"  3. Place the file next to this script (or set the env var)")
        return 1

    flow = InstalledAppFlow.from_client_secrets_file(client_secret, GSC_SCOPES)

    print(f"Opening browser for OAuth consent…")
    print(f"Requested scope: {GSC_SCOPES[0]}")
    print("Sign in with the GSC property OWNER account.")
    print()

    # access_type='offline' + prompt='consent' guarantees a refresh_token,
    # even if the app was already authorized by this account before.
    creds = flow.run_local_server(
        port=0,
        prompt="consent",
        access_type="offline",
        open_browser=True,
        authorization_prompt_message="Go to this URL to authorize: {url}",
        success_message="Authorization OK — you can close this tab.",
    )

    if not creds.refresh_token:
        print()
        print("WARN: no refresh_token received despite access_type=offline.")
        print("Revoke access at https://myaccount.google.com/permissions")
        print("then re-run this script.")
        return 2

    payload = {
        "refresh_token": creds.refresh_token,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "token_uri": creds.token_uri,
        "scopes": list(creds.scopes or GSC_SCOPES),
    }
    with open(token_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    # chmod 600 on Unix; no-op on Windows but no error
    try:
        os.chmod(token_path, stat.S_IRUSR | stat.S_IWUSR)
    except (OSError, NotImplementedError):
        pass

    print()
    print(f"OK — refresh_token saved in {token_path}")
    print(f"     (chmod 600 on Unix)")
    print()
    print("Next steps:")
    print(f"  1. Push {token_path} to your VPS, e.g.:")
    print(f"       scp {token_path} root@vps:/root/.hermes/.gsc_token.json")
    print(f"       ssh root@vps 'chmod 600 /root/.hermes/.gsc_token.json'")
    print(f"  2. Configure gsc_client.py via env: GSC_TOKEN_PATH=/root/.hermes/.gsc_token.json")
    print(f"  3. Run: python gsc_client.py (should display top queries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
