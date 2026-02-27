---
name: validate-schema
description: >-
  Detects CRM schema mismatches (stale IDs, missing properties, outdated select
  options) and automatically refreshes the cached schema by introspecting live
  Notion databases. Use when CRM operations fail with 404s, property errors, or
  when the schema is older than 7 days.
user_invocable: true
---

# Validate & Refresh CRM Schema

Checks `.claude/crm-schema.json` for staleness or mismatches against the live Notion databases, then refreshes it in-place when issues are found.

## Step 0 — Load Configuration

Read `.claude/settings.json` from the current project directory.

- If the file does not exist or has no `NOTION_CRM_*` keys in `env`, stop and tell the user:
  > Notion CRM Helper is not configured yet. Run `/notion-crm-helper:setup` first.

Extract the database IDs:
- `NOTION_CRM_CONTACTS_DB_ID` → contacts
- `NOTION_CRM_ACCOUNTS_DB_ID` → accounts
- `NOTION_CRM_OPPORTUNITIES_DB_ID` → opportunities
- `NOTION_CRM_LISTS_DB_ID` → lists
- `NOTION_CRM_TEMPLATES_DB_ID` → templates
- `NOTION_CRM_ACTIVITIES_DB_ID` → activities (optional)

## Step 1 — Detect Schema Mismatch

Run the detection script against the user's schema file:

```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/validate-schema/resources/detect-schema-mismatch.js" .claude/crm-schema.json
```

The script outputs a JSON result with a `mismatch` boolean and details about what was found. Parse the JSON output.

**If `mismatch` is `false`**: Report to the user that the schema is current and no refresh is needed. Include the schema age. End the skill.

**If `mismatch` is `true`**: Continue to Step 2. Tell the user what was detected:
- `stale` — schema is older than the configured max stale days
- `invalid` — one or more database IDs are empty or missing
- `error_patterns_detected` — Notion API errors suggest ID/property mismatches

## Step 2 — Introspect Live Databases

For each database ID from Step 0 (skip any that are empty), call `notion-fetch` with the database ID to retrieve the full database object. Do this silently — do not report individual fetch progress.

For each database, extract:

1. **collection_id**: Look for a `<data-source url="collection://...">` tag in the response. Extract the full `collection://` URL.

2. **Properties**: For each property, record:
   - Display name (the key)
   - Internal ID (the short opaque Notion-internal ID, e.g. `eDptYQ` — NOT a UUID; use verbatim)
   - Type (`title`, `rich_text`, `select`, `multi_select`, `number`, `date`, `email`, `phone_number`, `url`, `relation`, `checkbox`, etc.)
   - For `select` and `multi_select` types: the exact option strings with all emoji preserved

3. **Database name**: The actual display name from Notion.

Build a JSON object mapping each database key to its introspected data:

```json
{
  "contacts": {
    "id": "<database-uuid>",
    "collection_id": "<collection://url>",
    "name": "<display name>",
    "properties": {
      "Contact Name": { "id": "title", "type": "title", "required": true },
      "Contact Email": { "id": "eDptYQ", "type": "email" },
      "Status": { "id": "xYzAb", "type": "select", "options": ["🔥 Hot", "❄️ Cold"] }
    }
  }
}
```

Include `"options"` only for `select` and `multi_select` types. Include `"required": true` only for the title property.

If `notion-fetch` fails for a database, skip it and note the failure — do not block the refresh.

## Step 3 — Refresh Schema

Pipe the introspected data into the refresh script:

```bash
echo '<introspected-json>' | node "${CLAUDE_PLUGIN_ROOT}/skills/validate-schema/resources/refresh-schema.js" .claude/crm-schema.json
```

The script:
- Compares introspected data against the existing schema
- Updates any changed database IDs, collection IDs, names, or properties
- Rebuilds `select_option_aliases` (strips emoji prefixes to create aliases)
- Bumps the version and updates `last_validated` timestamp
- Writes the updated schema to `.claude/crm-schema.json`

Parse the JSON output to determine what changed.

## Step 4 — Report Results

Present a summary to the user:

```
Schema Validation Complete
==========================

Status:    [Refreshed / No changes needed]
Version:   [new version]
Validated: [timestamp]

Changes:
  - [database]: [field] updated ([old] → [new])
  - ...

All CRM operations will now use the updated schema.
```

If no databases could be fetched (all failed), warn the user:
> Unable to reach any Notion databases. Check your Notion connection and run `/notion-crm-helper:setup` if needed.

## Error Handling

- If the detection script exits with code 2 (schema not found), tell the user to run `/notion-crm-helper:setup` to generate the initial schema.
- If `notion-fetch` returns auth errors, suggest re-authorizing the Notion connector.
- If the refresh script fails to write, warn the user but do not block — the schema can be regenerated via `/notion-crm-helper:setup`.
