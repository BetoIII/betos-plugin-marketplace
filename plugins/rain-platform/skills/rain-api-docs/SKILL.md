---
name: rain-api-docs
description: Search and reference Rain's API documentation for answering questions about Rain's platform, API endpoints, webhooks, smart contracts, compliance, card issuing, KYC/KYB, disputes, transactions, collateral, onramps/offramps, and integration guides. Use this skill whenever the user asks anything about Rain's API, Rain's documentation, how Rain works, how to integrate with Rain, webhook payloads, endpoint parameters, card management, authorization flows, ledgering, or any Rain platform feature. Also trigger when the user says "check the docs", "what does the API say", "Rain docs", "look it up in the docs", or references any Rain API endpoint, resource, or concept. Even if the user doesn't explicitly mention "docs" or "API", use this skill whenever the question is about Rain's platform capabilities, technical behavior, or integration patterns — it's better to search the docs and confirm than to guess.
---

# Rain API Documentation Search

This skill gives you access to Rain's complete API documentation. The docs are cached locally in the user's project so they survive across sessions and stay verifiably fresh against the live docs site.

## Cached Documentation Files

The skill caches two files in `<cache-dir>/`:

- **`llms.txt`** — Index of all ~400 doc pages with titles, URLs, and short descriptions. Read this first to locate relevant pages quickly.
- **`llms-full.txt`** — Complete documentation content (~29,000 lines). Each page starts with `# Title` followed by `Source: <url>`.
- **`.metadata.json`** — Bookkeeping: `fetched_at`, sha256 hashes, ETag, and Last-Modified for each file. Used by the refresh script for cheap conditional-GET freshness checks.

The docs cover: API changelog, webhook schemas, smart contracts changelog, guides (authorization, card management, KYC/KYB, disputes, collateral, ledgering, onramps/offramps, 3DS, shipping, reporting), and the full REST API reference.

## How to Use This Skill

### Step 0: Prepare the cache (run every time before searching)

**Step 0a — Locate the project root and cache directory.**

Run this Bash command to determine the project root:

```bash
git rev-parse --show-toplevel 2>/dev/null || pwd
```

The default cache directory is `<project-root>/rain-api-docs/`.

**Step 0b — First-run setup (only if `<project-root>/rain-api-docs/` does NOT already exist).**

If the cache directory doesn't exist yet, call `AskUserQuestion` with this question:

> *"Where should I cache the Rain API docs? They're ~670 KB total and will be checked against live docs on each use."*

Options:
1. **Use `<project-root>/rain-api-docs/`** (recommended) — persistent across sessions.
2. **Pick a different folder** — user provides an absolute path; use that as `<cache-dir>`.
3. **Use temporary cache** — use `/tmp/rain-api-docs/`. Warn the user this will NOT persist across sandbox sessions.

After the user chooses option 1 or 2, check whether a `.gitignore` exists at the project root. If it does and doesn't already contain `rain-api-docs/`, append the line (with a leading comment `# rain-api-docs skill cache`).

**Step 0c — Verify freshness against live docs.**

Run:

```bash
python3 "<this-skill-dir>/scripts/refresh_cache.py" auto --cache-dir "<cache-dir>" --quiet
```

The script prints exactly one status line to stdout:

| Status | Meaning | What to do |
|---|---|---|
| `fresh` | Cache matches live docs (verified via ETag or content hash). | Proceed to Step 1. |
| `refreshed` | Cache was stale and has just been updated. | Proceed to Step 1. |
| `network-error` | Couldn't reach `docs.rain.xyz`. | If cache files exist, proceed to Step 1 BUT prepend your final answer with: *"Note: I could not verify the Rain docs cache against live docs (network unavailable); the answer is based on the local cache."* If no cache files exist, tell the user the skill can't run in this environment and suggest they run the refresh script from a non-sandboxed shell or paste fresh content. |
| `auth-error` | Mintlify access code was rejected. | Ask the user for the current access code and rerun with `--code NEW_CODE`. |

### Step 1: Classify the query

- **Specific endpoint lookup** — e.g., "How do I create a card?" → find the endpoint in the API reference section
- **Concept/guide lookup** — e.g., "How does authorization work?" → find the relevant guide page
- **Webhook lookup** — e.g., "What's in the transaction.completed webhook?" → find the webhook schema
- **Troubleshooting** — e.g., "Why was my transaction declined?" → check decline reasons, risk rules docs
- **Changelog/what's new** — e.g., "What changed recently?" → check the API and webhook changelogs

### Step 2: Search the index

Read `<cache-dir>/llms.txt` to scan page titles and descriptions and pick targets to dive into.

### Step 3: Search the full docs

Use `Grep` on `<cache-dir>/llms-full.txt` for specific terms — endpoint paths like `/v1/issuing/cards`, field names, error codes, status values, resource names. Use context lines (`-C 15` or more) to capture surrounding documentation.

For broader reading, locate a section by its header pattern (`# Page Title` followed by `Source: URL` on the next line) and use `Read` with offset/limit to read that section.

**Tip:** Each doc page starts with `# Title\nSource: https://docs.rain.xyz/...` — grep `^Source:.*keyword` to find pages by URL path, or `^# .*keyword` to find by title.

### Step 4: Synthesize and cite

Provide accurate answers based on what you found in the docs. Always include the source URL: `[Page Title](https://docs.rain.xyz/...)`. If the docs don't cover something, say so clearly rather than fabricating an answer.

## Common Search Patterns

| User asks about... | Search terms to try |
|---|---|
| Creating/managing cards | `Issuing Cards`, `Managing Cards`, `POST /v1/issuing/cards` |
| Authorization flow | `Authorization`, `Authorizing Transactions`, `partner-managed`, `rain-managed` |
| Webhooks | `webhook`, the specific event name (e.g., `transaction.completed`) |
| KYC/KYB compliance | `Compliance`, `Application States`, `Managing Users`, `Managing Subtenants` |
| Disputes | `disputes`, `dispute.created`, `Decline Reasons` |
| Collateral/crypto | `collateral`, `Managing Collateral`, `onramps`, `offramps`, `contract` |
| Transaction types | `transaction`, `spend`, `payment`, `Force Capture`, `Multi-Capture` |
| Smart contracts | `Smart Contracts`, `EVM`, `Solana`, `Stellar` |
| Reporting | `report`, `BIN Reports`, `Reporting Field Descriptions` |
| Card shipping | `Physical Card Shipping`, `Bulk Shipping` |
| 3DS authentication | `3DS`, `challenge.requested`, `3DS Forwarding` |
| API keys/auth | `Authenticating`, `API Key`, `JWT`, `IP Whitelisting` |
| Ledgering | `Ledgering System`, `Ledgering Best Practices` |
| PIN management | `Managing a Card's PIN` |
| Raindrops/rewards | `raindrops`, `Raindrops Mint`, `Raindrops Activity` |
| Pricing | `Pricing`, `pricing-and-fees` |
| Sandbox vs production | `sandbox`, `Quickstart`, `Pre-Live Setup` |

## Refresh Script Reference

The script at `scripts/refresh_cache.py` supports three subcommands:

- **`auto`** (default) — verify freshness via conditional GETs against `docs.rain.xyz`; re-download only the files that actually changed. This is what Step 0c runs.
- **`check`** — read-only freshness probe. Prints `fresh`, `stale`, `no-cache`, `network-error`, or `auth-error`. Useful for diagnostics.
- **`refresh`** — force a full re-download regardless of cache state. Use when the user explicitly asks to refresh, or when the access code has just changed.

All subcommands require `--cache-dir`. Pass `--code NEW_CODE` if the Mintlify access code has rotated.

If `auto`/`refresh` fails in a sandboxed environment, ask the user to:
1. Open `https://docs.rain.xyz/.well-known/llms.txt` and `llms-full.txt` in a browser.
2. Enter the access code when prompted.
3. Paste the content; you (Claude) write it directly to `<cache-dir>/llms.txt` and `<cache-dir>/llms-full.txt`, then rerun `auto` to regenerate `.metadata.json`.

## Important Notes

- Rain's API base URLs: `https://api.rain.xyz` (production), `https://api-sandbox.rain.xyz` (sandbox). Always distinguish when relevant.
- `llms-full.txt` is large (~29K lines). Always prefer targeted `Grep` searches over reading the whole file.
- When referencing API endpoints, use the full path format: `GET /v1/issuing/...` or `POST /v1/issuing/...`.
- The docs site is hosted on Mintlify at `docs.rain.xyz` behind an access code gate; the refresh script handles authentication automatically.
