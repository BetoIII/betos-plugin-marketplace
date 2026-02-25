---
name: crm-status
description: Check the health and status of your Notion CRM — connection status, database inventory, and record counts.
user_invocable: true
---

# CRM Status Check

Run this skill to verify your Notion CRM Helper is working correctly.

## Steps

### Step 1: Test Notion Connection

Use `notion-search` with an empty or broad query to verify the Notion connection is active.

- If it fails, report the error and suggest re-authorizing the Notion connector.

### Step 2: Database Inventory

Use `notion-search` to locate each of the 5 CRM databases by name:
1. Contacts
2. Opportunities
3. Lists
4. Templates
5. Activities

For each database found, use `notion-fetch` to get its details and approximate record count (number of child pages/rows).

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

If any databases are missing, suggest running `/create-crm` to create them.
