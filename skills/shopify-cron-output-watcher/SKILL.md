---
name: shopify-cron-output-watcher
description: Pattern to monitor and validate autonomous execution of triggered crons.
version: 0.1.0
author: Hermes auto-meta grand-run-2026-W20
category: devops
tags:
  - auto-proposed
  - grand-run-2026-W20

---

### When to Use
Use this pattern when triggering one of the 4 main <STORE_NAME> crons (lundi-perf, samedi-ideas, dimanche-meta, watchdog-conversion) to validate their successful execution.

### Procedure
1. Trigger the cron script or command.
2. Poll the defined output directory (e.g. /root/shopify-cron-logs/).
3. Parse the generated result file (e.g. ## Response header).
4. Confirm the output is correctly formatted and that actions (email/log) were indeed triggered.

### Pitfalls
- Don't fail to wait for log file generation (allow a slight polling delay).
- Don't purge old logs before triggering, which would mislead the timestamp.
- Don't ignore silent errors in stderr when exit code is 0.

### Verification
- Output file present and timestamped.
- File content free of "Traceback" or "AuthenticationError" type errors.
- Actions described in the report (e.g. email sent) match the test expectation.
