---
name: hermes-email-sender
description: Gmail SMTP email send (test mode = $HERMES_TEST_EMAIL_TO, prod mode = production list). Refactor of the inline snippet.
category: messaging
version: 1.0.0
metadata:
  hermes:
    tags: [email, smtp, gmail, test-mode]
    requires_toolsets: [terminal]
---

# <STORE_NAME> Email Sender

## When to Use
- Whenever a skill / cron / prompt requires sending a <STORE_NAME> email
- Replaces all inline smtplib snippets scattered across the prompts

## Test mode flag

MANDATORY: read `$HERMES_MODE` from `/root/.hermes/.env` before any send:
- If `HERMES_MODE=test` or absent: recipient is forced to `$HERMES_TEST_EMAIL_TO` (typically $EMAIL_TO), subject prefixed `[TEST]` or `[TEST PHASE X]`. Ignores the `to_prod` parameter even if supplied.
- If `HERMES_MODE=prod`: uses `to_prod` parameter. Requires explicit "mode=prod" mention in the input.

## Procedure
Input:
```python
{
  "to_mode": "test" | "prod",   # test = $EMAIL_TO only ; prod = list
  "to_prod": ["..."]?,           # ignored if mode=test
  "subject": "...",
  "body_text": "...",            # plain text mandatory
  "body_html": "..."?,           # optional
  "attachments": ["path", ...]?  # optional
}
```

Steps:
1. Load env: `set -a; . /root/.hermes/.env; set +a`
2. Build the message:
   - If test mode: `to = $EMAIL_TO` (single recipient) AND subject PREFIXED `[TEST PHASE 3]` or `[TEST]` per context
   - If prod mode: `to = list` (only when MISSION-HERMES authorizes prod)
3. Send via smtplib STARTTLS:
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
4. MANDATORILY end with `print("EMAIL_SMTP_OK")` on stdout (anti-hallucination rule — without this line, no email is confirmed).

## Pitfalls
- Test mode = never to a real list, never in Cc/Bcc.
- In prod: do NOT hardcode a list, take `to_prod` parameter ONLY.
- Without `EMAIL_SMTP_OK` on stdout = email NOT sent (strict rule).
- If SMTP fails (Gmail rate-limit, wrong password): capture the exception, do NOT claim it was sent.
- On failure, return `EMAIL_FAIL: <exact cause>` instead of `EMAIL_SMTP_OK`.

## Verification
- stdout contains EXACTLY `EMAIL_SMTP_OK` after success
- If failure, stdout contains `EMAIL_FAIL:` followed by the actual error message
- Test mode: single recipient = $EMAIL_TO, subject contains `[TEST`
