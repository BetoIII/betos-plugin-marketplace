---
name: crm-status
description: Check the health and status of your Notion CRM — connection status, database inventory, and record counts.
user_invocable: true
---

# CRM Status Check

Run this skill to verify your Notion CRM Helper is working correctly.

## Step 0: Load Configuration

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

Also silently read `.claude/crm-schema.json`. If it exists, parse it and extract `last_validated` and compute the age in days. Store for the report in Step 3.

## Steps

### Step 1: Test Notion Connection

Use `notion-search` with an empty or broad query to verify the Notion connection is active.

- If it fails, report the error and suggest re-authorizing the Notion connector.

### Step 2: Database Inventory

Use `notion-fetch` with each stored database ID to retrieve database details and approximate record count. For any ID that is empty (not configured), mark that database as "Not configured — run `/notion-crm-helper:setup`".

Check:
1. `contacts_db_id` → Contacts
2. `accounts_db_id` → Accounts
3. `opportunities_db_id` → Opportunities
4. `lists_db_id` → Lists
5. `templates_db_id` → Templates
6. `activities_db_id` → Activities *(optional — blank is expected if not configured)*

### Step 3: Report

Present a status summary:

```
Notion CRM Helper Status
=========================
Connection: Connected

Databases:
  Contacts:      [N] records
  Accounts:      [N] records  (or "Not found — run /create-crm")
  Opportunities: [N] records
  Lists:         [N] records  (or "Not found — run /create-crm")
  Templates:     [N] records  (or "Not found — run /create-crm")
  Activities:    [N] records  (or "Not configured — optional")

Schema:
  Status:         [Loaded / Not found]
  Last validated: [ISO timestamp or "N/A"]
  Age:            [N days old or "N/A"]
  Warning:        ["> 7 days old — consider re-running /notion-crm-helper:setup" if stale, else omit]

Notion MCP: Connected
```

If any databases are missing or returned errors, suggest running `/notion-crm-helper:setup` to update the configuration or `/notion-crm-helper:create-crm` to create them.

If the schema is not found or is stale (> 7 days), suggest running `/notion-crm-helper:setup` to generate or refresh it.
