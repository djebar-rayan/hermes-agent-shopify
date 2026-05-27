---
name: hermes-email-sender
description: Envoi email SMTP Gmail (mode test = $HERMES_TEST_EMAIL_TO, mode prod = production list). Factorisation du snippet inline.
category: messaging
version: 1.0.0
metadata:
  hermes:
    tags: [email, smtp, gmail, test-mode]
    requires_toolsets: [terminal]
---

# <STORE_NAME> Email Sender

## When to Use
- Toute fois qu un skill / cron / prompt requiert un envoi email <STORE_NAME>
- Remplace tous les snippets smtplib inline dispersés dans les prompts

## Test mode flag

Lis OBLIGATOIREMENT `$HERMES_MODE` depuis `/root/.hermes/.env` avant tout envoi :
- Si `HERMES_MODE=test` ou absent : destinataire force = `$HERMES_TEST_EMAIL_TO` (typiquement $EMAIL_TO), sujet prefixe `[TEST]` ou `[TEST PHASE X]`. Ignore le parametre `to_prod` meme s il est fourni.
- Si `HERMES_MODE=prod` : utilise `to_prod` parameter. Necessite mention explicite "mode=prod" dans l input.

## Procedure
Input :
```python
{
  "to_mode": "test" | "prod",   # test = $EMAIL_TO only ; prod = list
  "to_prod": ["..."]?,           # ignored if mode=test
  "subject": "...",
  "body_text": "...",            # plain text obligatoire
  "body_html": "..."?,           # optionnel
  "attachments": ["path", ...]?  # optionnel
}
```

Etapes :
1. Charge env : `set -a; . /root/.hermes/.env; set +a`
2. Construit le message :
   - Si mode test : `to = $EMAIL_TO` (un seul destinataire) ET sujet PREFIXE `[TEST PHASE 3]` ou `[TEST]` selon contexte
   - Si mode prod : `to = liste` (uniquement quand MISSION-HERMES autorise prod)
3. Envoie via smtplib STARTTLS :
   ```python
   import os, smtplib
   from email.message import EmailMessage
   from email.utils import formatdate, make_msgid
   msg = EmailMessage()
   msg["From"] = os.environ["EMAIL_FROM"]
   msg["To"] = ", ".join(recipients)
   msg["Subject"] = subject
   msg["Date"] = formatdate(localtime=True)
   msg["Message-ID"] = make_msgid(domain="gmail.com")
   msg.set_content(body_text)
   if body_html:
       msg.add_alternative(body_html, subtype="html")
   with smtplib.SMTP(os.environ["EMAIL_SMTP_HOST"], int(os.environ["EMAIL_SMTP_PORT"]), timeout=20) as s:
       s.ehlo(); s.starttls(); s.ehlo()
       s.login(os.environ["EMAIL_SMTP_USER"], os.environ["EMAIL_SMTP_PASSWORD"])
       s.send_message(msg)
   print("EMAIL_SMTP_OK")
   ```
4. Termine OBLIGATOIREMENT par `print("EMAIL_SMTP_OK")` sur la sortie standard (rule anti-hallucination — sans cette ligne, aucun email n est confirme).

## Pitfalls
- Mode test = jamais a une liste reelle, jamais en Cc/Bcc.
- En prod : ne PAS hardcoder de liste, prend `to_prod` parameter UNIQUEMENT.
- Sans `EMAIL_SMTP_OK` en stdout = email NON envoye (regle stricte).
- Si SMTP echoue (rate-limit Gmail, mauvais mot de passe) : capture l exception, ne pretendre PAS qu il a ete envoye.
- En cas d echec, retourne `EMAIL_FAIL: <cause exacte>` au lieu de `EMAIL_SMTP_OK`.

## Verification
- stdout contient EXACTEMENT `EMAIL_SMTP_OK` apres succes
- Si echec, stdout contient `EMAIL_FAIL:` suivi du message d erreur reel
- Mode test : un seul destinataire = $EMAIL_TO, sujet contient `[TEST`
