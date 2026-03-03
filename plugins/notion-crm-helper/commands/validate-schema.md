---
description: Validate your Notion CRM schema against live databases — check connection, detect property drift, and confirm sync status
argument-hint: ""
---

# /notion-crm-helper:validate-schema

Check whether your local CRM schema matches what is currently in Notion. Tests the Notion connection, fetches live database properties, and compares them against `.claude/crm-schema.json` to surface drift.

## Workflow

### Step 1 — Load Configuration
Read `.claude/settings.json` from the current project directory. Extract database IDs from the `env` object:
- `NOTION_CRM_CONTACTS_DB_ID` → contacts
- `NOTION_CRM_ACCOUNTS_DB_ID` → accounts
- `NOTION_CRM_OPPORTUNITIES_DB_ID` → opportunities
- `NOTION_CRM_LISTS_DB_ID` → lists
- `NOTION_CRM_TEMPLATES_DB_ID` → templates
- `NOTION_CRM_ACTIVITIES_DB_ID` → activities (optional)

If `.claude/settings.json` is missing or has no `NOTION_CRM_*` keys, stop:
> Notion CRM Helper is not configured yet. Run `/notion-crm-helper:setup`.

Also read `.claude/crm-schema.json`. Extract `last_validated`, `version`, and `databases`. Compute schema age in days from `last_validated` to today. If the file is missing, note it — skip the mismatch comparison step.

### Step 2 — Test Notion Connection
Call `notion-search` with a broad query to confirm the MCP connection is active. If it fails, stop and report:
> Connection: Failed — re-authorize the Notion connector in Claude Code MCP settings.

### Step 3 — Fetch Live Database Properties
For each database ID from Step 1, call `notion-fetch`. Extract all property definitions: display name, type, and (for `select` / `multi_select`) the full option string list.

If `notion-fetch` returns 404 for a database, mark it as "Not found" in the report. Before concluding the schema is stale, check relation URLs from any successfully-fetched database: if a relation's `collection://` URL matches `schema.databases[db_key].collection_id`, treat that database as valid even if its direct fetch failed.

### Step 4 — Compare Against Schema
If `crm-schema.json` was loaded, compare live properties against `schema.databases[db_key].properties` for each successfully-fetched database. Detect:
- **New properties**: in live database but not in schema
- **Removed properties**: in schema but not in live database
- **Type changes**: property exists in both but `type` field differs
- **Option changes**: for `select`/`multi_select`, compare option arrays — note how many were added/removed

### Step 5 — Report

```
Notion CRM Helper — Schema Validation
======================================
Connection: Connected

Databases:
  Contacts:      Accessible
  Accounts:      Accessible
  Opportunities: Accessible
  Lists:         Accessible
  Templates:     Accessible
  Activities:    Not configured — optional

Schema:
  Status:         Loaded
  Last validated: 2026-01-05T13:14:00.000Z
  Age:            56 days old
  Version:        2.6.0
  Sync status:    Mismatches detected — see below

Schema Mismatches:
  contacts:
    - New property: "LinkedIn URL" (url)
    - Options changed: "Engagement Level" (+1 added, -0 removed)
  opportunities:
    - Type changed: "Lead Source" (select → multi_select)

  To update your schema, run:
    /notion-crm-helper:refresh-schema
```

If no mismatches: `Sync status: In sync — schema matches live databases`

If schema is in-sync but older than 7 days, add: "Schema is in sync but is N days old. Consider running `/notion-crm-helper:refresh-schema` to re-validate property IDs."
