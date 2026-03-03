---
description: Refresh your Notion CRM schema — re-fetch live database IDs and properties, update crm-schema.json, and increment the version
argument-hint: ""
---

# /notion-crm-helper:refresh-schema

Re-fetches all live database IDs and property definitions from Notion and writes them to `.claude/crm-schema.json`. Run this when `/notion-crm-helper:validate-schema` reports mismatches, when databases may have moved, or after adding/changing Notion database properties.

## Workflow

### Step 1 — Load Configuration
Read `.claude/settings.json` and `.claude/crm-schema.json`. Hold the full schema object in memory as the base for updates.

If `settings.json` is missing or unconfigured, stop: run `/notion-crm-helper:setup`.
If `crm-schema.json` is missing, stop: run `/notion-crm-helper:setup` to generate it first.

### Step 2 — Search for Current Database IDs
Search Notion for each core database by display name using `notion-search`. Use the name variants from `schema.database_name_mappings`. For each search, extract the `id` from any result whose `object` is `"database"`.

Search for:
1. Contacts — "Contacts", "Contact Database"
2. Accounts — "Accounts", "Accounts (Companies)"
3. Opportunities — "Opportunities", "Opportunities (Pipeline)"
4. Lists — "Lists"
5. Templates — "Templates"
6. Activities — "Activities" (optional — skip gracefully if not found)

If multiple results match, prefer the one whose `id` matches the cached ID. If none match, use the first database result and flag the change.

### Step 3 — Compare IDs
Compare each discovered ID against `schema.databases[db_key].id`. Report inline:

```
Comparing Database IDs:

  Contacts
  ├─ Cached:  2a4e833b-5a49-81dd-a36c-faa344cc523f
  ├─ Current: 2a4e833b-5a49-81dd-a36c-faa344cc523f
  └─ Status:  No change

  Accounts
  ├─ Cached:  2a4e833b-5a49-8131-b2ea-000b8ed052ac
  ├─ Current: ac316070-57a3-449a-980f-61bf01003979
  └─ Status:  CHANGED
```

### Step 4 — Fetch Live Properties
For each database (using the current ID from Step 2), call `notion-fetch`. Extract:
- All property definitions: display name, internal short ID (not UUID), type, options (for `select`/`multi_select`)
- The `collection_id` from any `<data-source url="collection://...">` tag in the response

If `notion-fetch` fails for a database, retain existing property data from the cached schema for that database and note the failure.

### Step 5 — Rebuild Select Option Aliases
For each successfully-fetched database, rebuild `select_option_aliases`:
1. For each `select` and `multi_select` property, iterate all option strings
2. Strip leading emoji characters (U+1F300+, U+2600–U+27BF) and trim whitespace to get the alias
3. If alias ≠ original, add `"alias": "original_with_emoji"` to the map
4. Example: `"🔥 Hot"` → alias `"Hot"` maps to `"🔥 Hot"`; `"Champion"` → unchanged, skip

### Step 6 — Write Updated Schema
Construct the updated schema by merging live data into the cached object:
- Update `databases.[db_key].id` for changed IDs
- Update `databases.[db_key].collection_id` where a new collection URL was found
- Update `databases.[db_key].properties` for each successfully-fetched database
- Replace `select_option_aliases.[db_key]` with rebuilt aliases from Step 5
- Set both `last_updated` and `last_validated` to current ISO 8601 timestamp
- Increment patch version: split `version` on `.`, increment third component by 1, rejoin (e.g., `2.6.0` → `2.6.1`). If version is missing, set `"1.0.1"`.

Write the complete updated object to `.claude/crm-schema.json` using the Write tool.

If all databases failed to fetch, abort before writing and report:
> Unable to fetch live properties from Notion. Schema was not modified. Check your Notion connection and try again.

If the Write tool fails, report the error and output the full JSON so the user can save it manually.

### Step 7 — Verify
Re-read `.claude/crm-schema.json` to confirm `last_validated` and `version` were written correctly. Run a test `notion-fetch` on the Contacts database (or whichever database fetched successfully in Step 4) to confirm connectivity with the updated IDs.

### Step 8 — Report

```
Schema Refresh Complete
========================
Databases searched: 6
Databases updated:  1
Properties refreshed: 5 of 6 databases fetched successfully

ID Changes:
  Contacts:      No change
  Accounts:      Updated (2a4e833b... → ac316070...)
  Opportunities: No change
  Lists:         No change
  Templates:     No change
  Activities:    No change

Schema:
  Version:        2.6.0 → 2.6.1
  Last validated: 2026-03-02T10:00:00.000Z

Verification: Test query successful — Contacts database accessible

Your CRM schema is now current. Run /notion-crm-helper:validate-schema to confirm sync status.
```

If a database was not found during search, suggest: "Run `/notion-crm-helper:setup` to re-discover the correct database IDs."
