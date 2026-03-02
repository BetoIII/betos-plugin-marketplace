---
name: crm-status
description: Check the health and status of your Notion CRM — connection status, 
database inventory, and schema validation. Also let's the user refresh the CRM's schema.
---

# CRM Status Check & Schema Refresh

Run this skill to verify your Notion CRM Helper is working correctly. 

You can also use this skill to quickly refresh the CRM's schema.

## Status Check Workflow
### Step 0: Load Configuration

Read the file `.claude/settings.json` from the current project directory.

- If the file does not exist, stop and tell the user:
  > Notion CRM Helper is not configured yet. Run `/notion-crm-helper:setup` to create your configuration.
  > Make sure you have a project folder open — configuration is saved to `.claude/settings.json` in your project directory.

- If the file exists, parse it as JSON and extract database IDs from the `env` object:
  - `NOTION_CRM_CONTACTS_DB_ID` → contacts database ID
  - `NOTION_CRM_ACCOUNTS_DB_ID` → accounts database ID
  - `NOTION_CRM_OPPORTUNITIES_DB_ID` → opportunities database ID
  - `NOTION_CRM_LISTS_DB_ID` → lists database ID
  - `NOTION_CRM_TEMPLATES_DB_ID` → templates database ID
  - `NOTION_CRM_ACTIVITIES_DB_ID` → activities database ID
  - `NOTION_CRM_PARENT_PAGE_ID` → CRM parent page ID

- If `env` is missing or no `NOTION_CRM_*` keys are present, stop and tell the user to run `/notion-crm-helper:setup`.

Use these IDs in all subsequent steps instead of searching for databases by name.

Also silently read `.claude/crm-schema.json`. If it exists, parse it and extract `last_validated` and compute the age in days. Store for the report in Step 4.

### Step 1: Test Notion Connection

Use `notion-search` with an empty or broad query to verify the Notion connection is active.

- If it fails, report the error and suggest re-authorizing the Notion connector.

### Step 2: Schema Mismatch Detection

If `crm-schema.json` was loaded in Step 0, perform a live schema validation:

1. Inspect the properties returned by `notion-fetch` on the database ID.
2. Compare the live properties against `schema.databases[db_key].properties`:
   - **New properties**: properties in the live database that are not in the schema
   - **Removed properties**: properties in the schema that are not in the live database
   - **Type changes**: properties where the `type` has changed (e.g., `select` → `multi_select`)
   - **Select option changes**: for `select`/`multi_select` properties, check if the set of options has changed
3. Record any mismatches found per database.

If **any mismatches are detected**:

1. Report the mismatches clearly in the status output (see Step 3 format).
2. Build a JSON object containing the live property data for the mismatched databases, formatted as the `refresh-schema.js` script expects:
   ```json
   {
     "<db_key>": {
       "id": "<database-uuid>",
       "collection_id": "<collection://url>",
       "name": "<display name>",
       "properties": {
         "PropertyName": { "id": "<short-id>", "type": "<type>", "options": [...] }
       }
     }
   }
   ```
3. Run the refresh script to update their schema. Provide the exact command:
   ```
   node <path-to-refresh-schema.js> .claude/crm-schema.json --data '<the-json>'
   ```
   Where `<path-to-refresh-schema.js>` is the absolute path to this skill's `refresh-schema.js`.
4. After the user runs the script, re-read `.claude/crm-schema.json` and confirm the schema was updated (check that `last_validated` is now current and the version was incremented).

If **no mismatches are detected**, report "Schema is in sync with live databases" in the status output.

### Step 3: Report

Present a status summary:

```
Notion CRM Helper Status
=========================
Connection: Connected

Databases:
  Contacts:      [Accessible / Not found — check your Notion setup]
  Accounts:      [Accessible / Not found — check your Notion setup]
  Opportunities: [Accessible / Not found — check your Notion setup]
  Lists:         [Accessible / Not found — check your Notion setup]
  Templates:     [Accessible / Not found — check your Notion setup]
  Activities:    [Accessible / Not configured — optional]

Schema:
  Status:         [Loaded / Not found]
  Last validated: [ISO timestamp or "N/A"]
  Age:            [N days old or "N/A"]
  Version:        [version string or "N/A"]
  Validation:     [In sync / Mismatches detected — see below]

[If mismatches detected:]
Schema Mismatches:
  [db_name]:
    - New property: "PropertyName" (type)
    - Removed property: "PropertyName"
    - Type changed: "PropertyName" (select → multi_select)
    - Options changed: "PropertyName" (+2 added, -1 removed)

  → Run this command to update your schema:
    node <absolute-path>/refresh-schema.js .claude/crm-schema.json --data '<json>'

Notion MCP: Connected
```
---

## Schema Refresh Workflow

**Trigger phrases**: "refresh CRM schema", "update notion IDs", "fix stale schema", "refresh database IDs"

When the user requests a schema refresh, manually update all database IDs to ensure they match the current Notion workspace.

### Process

1. **Search for all core databases** using Notion MCP `Notion-search`:
   - Search term: "Contact Database"
   - Search term: "Accounts (Companies)"
   - Search term: "Opportunities (Pipeline)"

2. **Extract current database IDs** from search results:
   - Use the `id` field from database objects (NOT `collection_id`)
   - Validate that the search result type is "database"

3. **Compare with cached IDs** from `crm-schema.json`:
   ```
   📊 Comparing Database IDs:

   ⏩ Contact Database
   ├─ Cached:  2a4e833b-5a49-81dd-a36c-faa344cc523f
   ├─ Current: 2a4e833b-5a49-81dd-a36c-faa344cc523f
   └─ Status:  ✅ No change

   🗃️ Accounts (Companies)
   ├─ Cached:  2a4e833b-5a49-8131-b2ea-000b8ed052ac
   ├─ Current: ac316070-57a3-449a-980f-61bf01003979
   └─ Status:  ⚠️  CHANGED
   ```

4. **Update schema file** if changes detected:
   - Update `databases.[db_key].id` for each changed database
   - Update `last_validated` timestamp to current date
   - Increment patch version (e.g., 2.6.0 → 2.6.1)
   - Save updated `crm-schema.json`

5. **Verify updates**:
   - Re-read schema file to confirm changes
   - Run a test query against updated database

### Output Format

```
🔄 Refreshing CRM Schema...

🔍 Searching for databases...
✅ Found: Contact Database
✅ Found: Accounts (Companies)
✅ Found: Opportunities (Pipeline)

📊 Comparing IDs:
✅ Contacts: No change
⚠️  Accounts: ID changed
   Old: 2a4e833b-5a49-8131-b2ea-000b8ed052ac
   New: ac316070-57a3-449a-980f-61bf01003979
✅ Opportunities: No change

📝 Updating schema...
✅ Schema updated successfully
   - Version: 2.6.0 → 2.6.1
   - Last validated: 2026-01-05T13:14:00.000Z
   - 1 database ID updated

🧪 Verifying update...
✅ Test query successful - Accounts database accessible

✅ Schema refresh complete!
```

---

If any databases are missing or returned errors, suggest running `/notion-crm-helper:setup` to update the configuration.

If the schema is not found, suggest running `/notion-crm-helper:setup` to generate it.

If the schema is stale (> 7 days) but no mismatches were found, suggest re-validating with `/notion-crm-helper:crm-status` periodically.
