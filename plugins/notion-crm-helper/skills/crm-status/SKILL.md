---
name: crm-status
description: Check the health and status of your Notion CRM — connection status, database inventory, and record counts.
user_invocable: true
---

# CRM Status Check

Run this skill to verify your Notion CRM Helper is working correctly.

## Step 0: Load Configuration

Read the file `~/.claude/notion-crm-helper.local.md`.

- If the file does not exist or the YAML frontmatter does not contain `contacts_db_id`, stop and tell the user:
  > Notion CRM Helper is not configured yet. Run `/notion-crm-helper:setup` to connect your Notion databases before using this skill.

- If the file exists, extract these values from the YAML frontmatter:
  - `contacts_db_id`
  - `opportunities_db_id`
  - `lists_db_id`
  - `templates_db_id`
  - `activities_db_id`

Use these IDs in all subsequent steps instead of searching for databases by name.

## Steps

### Step 1: Test Notion Connection

Use `notion-search` with an empty or broad query to verify the Notion connection is active.

- If it fails, report the error and suggest re-authorizing the Notion connector.

### Step 2: Database Inventory

Use `notion-fetch` with each stored database ID to retrieve database details and approximate record count. For any ID that is empty (not configured), mark that database as "Not configured — run `/notion-crm-helper:setup`".

Check:
1. `contacts_db_id` → Contacts
2. `opportunities_db_id` → Opportunities
3. `lists_db_id` → Lists
4. `templates_db_id` → Templates
5. `activities_db_id` → Activities

### Step 3: Report

Present a status summary:

```
Notion CRM Helper Status
=========================
Connection: Connected

Databases:
  Contacts:      [N] records
  Opportunities: [N] records
  Lists:         [N] records  (or "Not found — run /create-crm")
  Templates:     [N] records  (or "Not found — run /create-crm")
  Activities:    [N] records

Notion MCP: Connected
```

If any databases are missing or returned errors, suggest running `/notion-crm-helper:setup` to update the configuration or `/notion-crm-helper:create-crm` to create them.
