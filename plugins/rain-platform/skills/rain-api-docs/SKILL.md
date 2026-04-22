---
name: rain-api-docs
description: Search and reference Rain's API documentation for answering questions about Rain's platform, API endpoints, webhooks, smart contracts, compliance, card issuing, KYC/KYB, disputes, transactions, collateral, onramps/offramps, and integration guides. Use this skill whenever the user asks anything about Rain's API, Rain's documentation, how Rain works, how to integrate with Rain, webhook payloads, endpoint parameters, card management, authorization flows, ledgering, or any Rain platform feature. Also trigger when the user says "check the docs", "what does the API say", "Rain docs", "look it up in the docs", or references any Rain API endpoint, resource, or concept. Even if the user doesn't explicitly mention "docs" or "API", use this skill whenever the question is about Rain's platform capabilities, technical behavior, or integration patterns — it's better to search the docs and confirm than to guess.
---

# Rain API Documentation Search

This skill gives you access to Rain's complete API documentation cached locally. Use it to answer questions accurately by referencing the actual docs rather than relying on general knowledge.

## Cached Documentation Files

Two files are cached in this skill's `cache/` directory:

- **`cache/llms.txt`** — Index of all ~400 doc pages with titles, URLs, and short descriptions. Read this first to locate relevant pages quickly.
- **`cache/llms-full.txt`** — Complete documentation content (~29,000 lines). Contains every page's full text organized as sections with `# Title` headers followed by `Source: <url>` lines.

The docs cover: API changelog, webhook schemas, smart contracts changelog, guides (authorization, card management, KYC/KYB, disputes, collateral, ledgering, onramps/offramps, 3DS, shipping, reporting), and the full REST API reference.

## How to Search

### Step 1: Classify the query

Figure out what the user needs:

- **Specific endpoint lookup** — e.g., "How do I create a card?" → find the endpoint in the API reference section
- **Concept/guide lookup** — e.g., "How does authorization work?" → find the relevant guide page
- **Webhook lookup** — e.g., "What's in the transaction.completed webhook?" → find the webhook schema
- **Troubleshooting** — e.g., "Why was my transaction declined?" → check decline reasons, risk rules docs
- **Changelog/what's new** — e.g., "What changed recently?" → check the API and webhook changelogs

### Step 2: Search the index

Read `cache/llms.txt` (in this skill's directory) to scan page titles and descriptions. This is fast and tells you which sections to dive into.

### Step 3: Search the full docs

Use `Grep` on `cache/llms-full.txt` for specific terms — endpoint paths like `/v1/issuing/cards`, field names, error codes, status values, resource names. Use context lines (`-C 15` or more) to capture the surrounding documentation.

For broader reading, locate the section by its header pattern (`# Page Title` followed by `Source: URL` on the next line) and use `Read` with an offset/limit to read that section.

**Tip:** Each doc page starts with `# Title\nSource: https://docs.rain.xyz/...` — you can grep for `^Source:.*keyword` to find pages by URL path, or `^# .*keyword` to find by title.

### Step 4: Synthesize and cite

Provide accurate answers based on what you found in the docs. Always include the source URL so the user can read more: `[Page Title](https://docs.rain.xyz/...)`. If the docs don't cover something, say so clearly rather than fabricating an answer.

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

## Refreshing the Cache

The cached docs may become stale. To refresh them:

1. Run: `python3 <this-skill-path>/scripts/refresh_cache.py`
2. The script fetches fresh copies from `https://docs.rain.xyz/.well-known/llms.txt` and `llms-full.txt`
3. The Rain docs are behind a Mintlify access code — the script will use the stored code automatically
4. If the access code has changed, pass the new one: `python3 scripts/refresh_cache.py --code NEW_CODE`
5. If programmatic fetch fails (sandbox restrictions), ask the user to paste updated content and overwrite the cache files directly

## Important Notes

- Rain's API base URL is `https://api.rain.xyz` (production) and `https://api-sandbox.rain.xyz` (sandbox). Always distinguish between them when relevant.
- The `llms-full.txt` file is large (~29K lines). Always prefer targeted `Grep` searches over reading the whole file.
- When referencing API endpoints, use the full path format: `GET /v1/issuing/...` or `POST /v1/issuing/...`
- The docs site is hosted on Mintlify at `docs.rain.xyz` behind an access code gate.
