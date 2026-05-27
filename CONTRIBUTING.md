# Contributing to Hermes Shopify Framework

Thanks for your interest! This project was born from a concrete operational need and has been generalized to serve other merchants. Contributions are welcome.

---

## 🧱 Skill Naming Convention

Hermes uses 2 prefixes:

| Prefix | Usage | Examples |
|---|---|---|
| `shopify-*` | Shopify domain skill (catalog, theme, KPI, Klaviyo, Instagram, SEO, content...) | `shopify-theme-editor`, `shopify-batch-executor`, `shopify-klaviyo-weekly-report` |
| `hermes-*` | Pure framework utility (not specific to Shopify) | `hermes-email-sender`, `hermes-schema-guard`, `hermes-snapshot-diff-validator` |

**Simple rule**: if your skill manipulates Shopify entities (product, collection, theme, customer, order) or e-commerce APIs (Klaviyo, Instagram, GSC) → `shopify-*`. Otherwise → `hermes-*`.

---

## 📝 SKILL.md Structure

Every skill follows this format:

```markdown
---
name: shopify-my-skill
description: Condensed 1-line description — what this skill does and when to invoke it
version: 1.0.0
author: Your name
metadata:
  hermes:
    tags: [shopify, monitoring, mutation]
    category: ecommerce
    requires_toolsets: [terminal, file, messaging]
---

# My Skill

Short description (1-2 paragraphs) of what the skill does.

## When to Use

- Trigger 1 (e.g. Monday perf cron)
- Trigger 2 (e.g. explicit user request "do X")
- DO NOT use for: Y, Z

## Configuration

Required vars from `.env`:
- `VAR_1` (e.g. `SHOPIFY_STORE`)
- `VAR_2`

Helper dependencies:
- `lib/theme.sh` (if applicable)

Companion skills:
- `hermes-schema-guard` (to load BEFORE any mutation)

## Procedure

1. Step 1 (with bash command if applicable)
2. Step 2
3. ...

## Pitfalls

- Known pitfall 1
- Pitfall 2

## Verification

Post-execution checklist:
- [ ] Criterion 1 verified
- [ ] Criterion 2 verified
- [ ] Entry logged in `learnings.md`
```

---

## 🔌 Adding a New API Integration

1. Create a helper in `lib/<service>-fetch.sh` (follow the pattern of `lib/klaviyo-fetch.sh`)
   - Disk cache with TTL (anti rate-limit)
   - Exponential retry on 429
   - Documented exit codes (0=success, 1=missing key, 2=API error, 3=usage)
   - Clear subcommands
2. Add the env variable in `config/.env.template` with a comment
3. Document in `docs/INTEGRATIONS.md` (add a row to the table)
4. Create the corresponding skill in `skills/shopify-<service>-*/SKILL.md`
5. Add a test to the smoke test if applicable

---

## 🛠️ Adding a Reusable Helper

Helpers live in `lib/`. Conventions:

- **Bash** by default (sourceable + executable)
- Header: comment with `# Requires in env: VAR_1, VAR_2`
- `<helper>_check_env` function that validates the presence of critical vars
- Functions prefixed with the helper name (`theme_get`, `theme_push`, `klaviyo_fetch`, ...)
- All functions exported via `export -f` at the end of the file
- Explicit error handling with prefix `[<HELPER>_FAIL: ...]` on stderr

---

## 🚀 Submitting a PR

### Workflow

1. **Fork** the repo
2. **Branch** from `main`: `git checkout -b add-shopify-X`
3. Implement + test locally
4. **Lint**: no hardcoded secret, no reference to a specific store
5. **Commit**: clear message (see format below)
6. **Push** + open a PR against `main`

### Commit Format

```
<type>: <short description 50 chars>

<detailed description if necessary>

<footer e.g. closes #42>
```

Types: `feat` (new skill/feature), `fix` (correction), `docs` (doc), `refactor`, `test`, `chore`.

Examples:
- `feat(skill): add shopify-product-bulk-importer`
- `fix(theme.sh): handle empty theme list gracefully`
- `docs(getting-started): clarify Theme Access setup`

### Acceptance Criteria

- [ ] The skill / helper / doc has a name following the convention
- [ ] No secret in plaintext (env vars are referenced, not their values)
- [ ] No reference to a specific store in generic code (except in `examples/`)
- [ ] Tests / smoke tests pass
- [ ] Documentation updated (`docs/SKILLS-REFERENCE.md` if new skill, `docs/INTEGRATIONS.md` if new API)
- [ ] No regression on existing skills

---

## 📐 Code Style

### Bash

- 2 spaces for indentation
- `set -euo pipefail` at the start of the script (unless a documented reason)
- `UPPER_CASE` variables for constants, `lower_case` for locals
- Always quote variables: `"$var"` not `$var`
- Helper functions return via `echo` (capturable) or via file (`$1` = output path)
- `local` for all function-internal variables

### Markdown

- Headings: `#` for the title, `##` for main sections, `###` for subsections (max 4 levels)
- Tables: align the `|` for readability
- Code blocks: with language tag (` ```bash `, ` ```json `, ...)
- Internal links: use relative paths (`./docs/X.md` rather than absolute URLs)

---

## 🤝 Code of Conduct

- Mutual respect
- No spam / promotion
- Issues are for bugs / features / technical questions
- No free support requests (private consulting via DM if needed)
- Constructive reviews, no "it doesn't work" without details

---

## 🙏 Credits

This framework was created by **Rayan Djebar** during an internship at Azamoul (French Amazigh culture brand), then generalized to serve other merchants. Contributors are listed in the "Contributors" section of the GitHub repo page.

---

## ❓ Questions

- GitHub issue for bug / feature / skill proposal
- For larger contributions (full new skill, major new integration), open a discussion issue first before coding
- No dedicated chat channel (Discord/Slack) for now
