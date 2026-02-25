---
name: setup
description: First-time configuration for the Notion CRM Helper plugin. Verifies the Notion connection, discovers or creates CRM databases, and confirms the workspace is ready.
user_invocable: true
---

# Notion CRM Helper Setup

Run this skill to configure the Notion CRM Helper plugin for first use.

## Prerequisites

- **Notion** must be authorized. Claude Code will prompt you to connect your Notion workspace via OAuth on first use.
- A **Notion page** that will serve as the CRM parent (all databases live under this page).

## Steps

### Step 1: Verify Notion Connection

Call `notion-search` with a broad query (e.g., "CRM") to confirm the Notion connection is active and authorized.

- If it succeeds, proceed.
- If it fails with an auth error, tell the user:
  > The Notion connector doesn't appear to be connected. In Claude Code, check that the `notion` MCP server is authorized. You may need to re-connect Notion via the MCP settings.

### Step 2: Ask for CRM Parent Page

Ask the user for the URL of the Notion page that will contain their CRM databases:

> What is the URL of your Notion CRM parent page? (The 5 CRM databases will be created under this page.)

Extract the page ID from the URL — the 32-character hex string at the end:
- `https://www.notion.so/My-CRM-83a0ac85cdd3464c92083b1336f7bfe7` → `83a0ac85cdd3464c92083b1336f7bfe7`

### Step 3: Discover Existing Databases

Use `notion-search` to look for databases named "Contacts", "Opportunities", "Lists", "Templates", "Activities".

- If all 5 are found, confirm and report their page IDs.
- If any are missing, offer to create them with `/create-crm`.

The 5 CRM databases are:
1. **Contacts** — People, leads, decision-makers
2. **Opportunities** — Sales pipeline and deals
3. **Lists** — Curated contact groups for campaigns
4. **Templates** — Message templates with {{variable}} placeholders
5. **Activities** — Calls, emails, meetings, notes, tasks

### Step 4: Confirm

Tell the user:
> Your Notion CRM Helper is ready! Your CRM databases are connected in Notion.
>
> Try these commands:
> - `/crm-status` — Check system health
> - `/create-crm` — Create any missing databases
> - `/manage-templates` — Create/edit message templates
> - `/import-contacts` — Import contacts from CSV
