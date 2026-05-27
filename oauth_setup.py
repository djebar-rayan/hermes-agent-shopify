"""OAuth2 user-consent flow for Google Search Console — setup à exécuter une fois.

Génère un refresh_token persistant pour le compte propriétaire de la
propriété GSC. Contourne le bug Google du 23/04/2026 qui empêche
d'ajouter un service account comme utilisateur GSC ("email not found").

Le refresh_token sauvegardé dans `.gsc_token.json` (chmod 600) permet à
`gsc_client.py` de s'authentifier automatiquement pour tous les futurs
appels GSC, sans interaction humaine — idéal pour les crons.

Prérequis Google Cloud Console (projet existant ou nouveau):

  1. https://console.cloud.google.com/apis/credentials/consent
     - User Type: External (compte Gmail standard) OU Internal (Workspace)
     - App name, support email, developer email
     - Scopes: ajouter `https://www.googleapis.com/auth/webmasters.readonly`
     - Test users: ajouter le compte propriétaire de la propriété GSC
       (sinon l'autorisation OAuth sera refusée tant que l'app est
       en mode "Testing")

  2. https://console.cloud.google.com/apis/credentials
     - + CREATE CREDENTIALS > OAuth client ID
     - Application type: Desktop app
     - Name: "Hermes GSC OAuth"
     - DOWNLOAD JSON → renomme en `client_secret.json` à côté de ce script
       (ou indique son chemin via env GSC_OAUTH_CLIENT_SECRET)

Usage:
  pip install google-auth-oauthlib
  python oauth_setup.py

Au lancement, un browser s'ouvre. Connecte-toi avec le compte propriétaire
de la propriété GSC, accepte le consentement. Le script récupère
automatiquement le code, l'échange contre un refresh_token, et le sauve.

Variables d'environnement:
  GSC_OAUTH_CLIENT_SECRET   chemin du client_secret.json (défaut: ./client_secret.json)
  GSC_TOKEN_PATH            chemin où sauver le token   (défaut: ./.gsc_token.json)
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
        print(f"ERREUR: client_secret introuvable: {client_secret!r}")
        print()
        print("Crée-le depuis Google Cloud Console:")
        print("  1. https://console.cloud.google.com/apis/credentials/consent")
        print("     User Type=External, scopes=webmasters.readonly,")
        print("     test user = compte propriétaire de la propriété GSC")
        print("  2. https://console.cloud.google.com/apis/credentials")
        print("     + CREATE CREDENTIALS > OAuth client ID > Desktop app")
        print("     > Download JSON > renomme en 'client_secret.json'")
        print(f"  3. Place le fichier à côté de ce script (ou via env)")
        return 1

    flow = InstalledAppFlow.from_client_secrets_file(client_secret, GSC_SCOPES)

    print(f"Ouverture du browser pour consentement OAuth…")
    print(f"Scope demandé: {GSC_SCOPES[0]}")
    print("Connecte-toi avec le compte PROPRIÉTAIRE de la propriété GSC.")
    print()

    # access_type='offline' + prompt='consent' garantit un refresh_token,
    # même si l'app a déjà été autorisée par ce compte précédemment.
    creds = flow.run_local_server(
        port=0,
        prompt="consent",
        access_type="offline",
        open_browser=True,
        authorization_prompt_message="Va sur cette URL pour autoriser: {url}",
        success_message="Autorisation OK — tu peux fermer cet onglet.",
    )

    if not creds.refresh_token:
        print()
        print("WARN: aucun refresh_token reçu malgré access_type=offline.")
        print("Révoque l'accès sur https://myaccount.google.com/permissions")
        print("puis relance ce script.")
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

    # chmod 600 sur Unix; no-op sous Windows mais sans erreur
    try:
        os.chmod(token_path, stat.S_IRUSR | stat.S_IWUSR)
    except (OSError, NotImplementedError):
        pass

    print()
    print(f"OK — refresh_token sauvegardé dans {token_path}")
    print(f"     (chmod 600 si Unix)")
    print()
    print("Étapes suivantes :")
    print(f"  1. Pousse {token_path} sur ton VPS, par ex.:")
    print(f"       scp {token_path} root@vps:/root/.hermes/.gsc_token.json")
    print(f"       ssh root@vps 'chmod 600 /root/.hermes/.gsc_token.json'")
    print(f"  2. Configure gsc_client.py via env: GSC_TOKEN_PATH=/root/.hermes/.gsc_token.json")
    print(f"  3. Lance: python gsc_client.py (devrait afficher les top queries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
