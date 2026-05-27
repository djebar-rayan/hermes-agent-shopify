# Production Checklist — Switch `HERMES_MODE=test` → `prod`

> Checklist to validate BEFORE switching your Hermes instance to production mode. The switch enables persistent Shopify mutations — rollback is possible but costs time.

---

## 1. Pre-switch verifications

### Test phase: minimum recommended duration

Before going to prod, run Hermes in `HERMES_MODE=test` for at minimum:
- **2 complete cycles of the Monday-perf cron** (= 2 weeks)
- **2 complete cycles of the Saturday-ideas cron**
- **2 complete cycles of the Sunday-meta cron**
- **~10 watchdog runs** (= ~2-3 days)

This allows you to observe:
- Are the weekly reports precise and useful?
- Are the Saturday-ideas proposals relevant to your brand?
- Does the meta-review identify real patterns?
- Does the watchdog alert on the right signals?

### Technical checklist

- [ ] **`.env` complete**: all critical vars filled (SHOPIFY_STORE, OPENROUTER_API_KEY, EMAIL_*, TELEGRAM_*, LIVE_THEME_ID, etc.)
- [ ] **Shopify CLI auth OK**: `shopify store info` works
- [ ] **Theme Access token active**: `theme_check_env && theme_list` works
- [ ] **OpenViking healthy**: `curl http://localhost:1933/health` returns 200
- [ ] **Hermes Telegram gateway up**: bot replies to `/start`
- [ ] **v0.14 hooks active**: test interactive session, verify that STANDING is injected
- [ ] **Crons executed at least 2 times without error**: `cat /root/.hermes/cron/jobs.json | jq '.jobs[] | {name, last_status}'`
- [ ] **`learnings.md` contains entries**: proof that the `log-learning` hook works
- [ ] **Gmail App Password valid**: test email send with `EMAIL_SMTP_OK` sentinel

### Content checklist

- [ ] **`MISSION.md` filled**: charter specific to your store
- [ ] **`STORE-BRAND.md` filled**: mandatory vocab + 🟢/🟡/🔴 levels + sensitivities
- [ ] **`brand-knowledge.md` filled**: 5-10 competitors identified with URL + niche + differentiation
- [ ] **`cultural-events.json` filled**: at least the next 3-5 events important to your brand
- [ ] **`MEMORY.md` filled**: store facts (catalog size, currency, timezone, Shopify plan)
- [ ] **Baseline KPI 30d captured**: `$HERMES_WORKSPACE/baseline-kpi-30j.md` exists

### Security checklist

- [ ] **`.env` chmod 600**: not accessible to other users
- [ ] **`~/.hermes/` chmod 700**
- [ ] **No secret in clear text** in already-generated reports (re-read 1-2 test reports)
- [ ] **`TELEGRAM_ALLOWED_USERS` = your user_id only**: no other authorized recipient
- [ ] **Telegram /yes validation tested**: do a dry-run mutation, receive the message, validate /yes, check that the mutation was actually applied (in test mode)

---

## 2. Effective switch

When the entire checklist is validated:

```bash
# 1. Backup current .env
cp /root/.hermes/.env /root/.hermes/.env.bak.$(date +%Y%m%d)

# 2. Modify mode
sed -i 's/^HERMES_MODE=test$/HERMES_MODE=prod/' /root/.hermes/.env

# 3. Verify
grep ^HERMES_MODE /root/.hermes/.env
# Must display: HERMES_MODE=prod

# 4. Log the switch in learnings.md
cat >> $HERMES_WORKSPACE/learnings.md << EOF

- [$(date -u +%Y-%m-%dT%H:%M:%SZ)] PHASE TRANSITION: HERMES_MODE=test → HERMES_MODE=prod
  Before: test exclusive phase (apply+rollback same run since install)
  After: production mode activated, persistent mutations after Telegram /yes
  Conclusion: merchant decision after <N> weeks of validated test
  Future: monitor the first real prod cron run
EOF

# 5. Update MEMORY.md
sed -i "s/Current phase.*/Current phase: PRODUCTION (since $(date -u +%Y-%m-%d))/" $HERMES_WORKSPACE/MEMORY.md
```

---

## 3. Post-switch monitoring

### First day (D)

- [ ] **Check that the next cron runs without error**: observe `last_status: ok` after the first run
- [ ] **Read the generated report**: any unexpected Shopify mutation? All numbers have a cited source?
- [ ] **Check Telegram notifications**: received, formatted correctly
- [ ] **Check the email**: `EMAIL_SMTP_OK` sentinel present

### First week

- [ ] **2-3 Telegram `/yes` validation requests received**: validation workflow functional
- [ ] **At least 1 persistent mutation applied** after /yes: check in Shopify admin that the change is in place
- [ ] **Rollback tested at least 1 time**: use `shopify-batch-rollback` on a recent batch to confirm that the before.json snapshot + rollback script work
- [ ] **Sunday meta-review**: confirm that it correctly identifies the week's patterns

### First month

- [ ] **No unvalidated Shopify mutation**: audit the mutation timeline in learnings.md
- [ ] **Baseline KPI vs M+1**: compare 30d KPIs before vs 30d after switch
- [ ] **OpenRouter cost in line with expectation**: `hermes insights --days 30`, check that cost stays under quota
- [ ] **No leaked secret** in reports / logs (grep audit)

---

## 4. Rollback procedure (prod → test)

If you detect a major problem:

```bash
# 1. Immediate return to test mode
sed -i 's/^HERMES_MODE=prod$/HERMES_MODE=test/' /root/.hermes/.env

# 2. (Optional) Disable all crons during investigation
# Edit /root/.hermes/cron/jobs.json and set "enabled": false on each job

# 3. Rollback recent mutations if serious issue
# For each recent batch:
node /root/.hermes/skills/shopify-batch-rollback/run.js <batch_id>
# OR directly:
bash $HERMES_WORKSPACE/batches/YYYY-Www-batchN-rollback.sh

# 4. Log
cat >> $HERMES_WORKSPACE/learnings.md << EOF

- [$(date -u +%Y-%m-%dT%H:%M:%SZ)] URGENT PHASE TRANSITION: HERMES_MODE=prod → HERMES_MODE=test
  Before: production active
  After: return to test exclusive
  Conclusion: <exact cause of rollback>
  Future: investigation + fix before new switch
EOF
```

---

## 5. Success / failure indicators

### Success (switch successful after 1 month)
- ✅ 4 Monday-perf cron cycles passed without error
- ✅ At least 5 persistent mutations applied and validated
- ✅ 30d KPIs vs baseline: no regression
- ✅ OpenRouter cost within budget
- ✅ No non-trivial watchdog alert
- ✅ User (merchant) satisfied with deliverables

### Failure (signals that justify rollback)
- ❌ Unvalidated persistent mutation applied by mistake
- ❌ 30d KPIs dropping >20% vs baseline with no external cause
- ❌ `EMAIL_SMTP_OK` sentinel regularly missing (lost emails)
- ❌ Telegram /yes validation no longer working (gateway down)
- ❌ OpenRouter cost exceeds 2x the budget
- ❌ Secrets exposed in reports

---

## 6. Communication to the merchant

For the merchant who supervises Hermes in prod, communicate weekly:
- Automatic Telegram summary (Monday-perf cron)
- Automatic email (same)
- Sunday meta-review (Telegram + summary)

And monthly (manual or additional cron to create):
- Monthly audit: M-1 vs M KPIs, cost, top wins/failures
- Decision: continue / adjust / disable crons / create new skills

---

## 7. Versioning and evolution

At every major prod config evolution:
- Back up `.env`, `config.yaml`, `cron/jobs.json`, `STANDING-CORE.md`, `STORE-BRAND.md`, `MISSION.md`
- Log in `learnings.md` with a structured entry
- (Optional) Push the new config to a private git repo (never public unless fully sanitized)

---

## 8. Decision matrix: should you switch to prod?

Answer the following questions after the test phase:

| Question | Desired answer |
|---|---|
| Are the Monday weekly reports precise and actionable? | Yes |
| Do the Saturday-ideas proposals match your brand universe? | Yes |
| Are the 🟢/🟡/🔴 autonomy levels correctly calibrated? | Yes |
| Has Hermes already proposed a mutation consistent with your strategy? | Yes (at least 1) |
| Have you tested a manual /yes validation on a mutation? | Yes |
| Have you tested a manual rollback of a mutation? | Yes |
| Do you trust Hermes to apply mutations without immediate intervention? | Yes |

If ALL answers are "Yes" → you are ready for the switch.
If ONE is "No" → continue test phase + resolve the blocking point before switching.
