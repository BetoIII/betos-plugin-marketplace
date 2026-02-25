---
name: setup
description: >-
  This skill should be used when the user says "set up notion crm", "configure
  notion crm helper", "run setup", "update my crm databases", or runs
  /notion-crm-helper:setup. Collects the Notion database IDs for all 5 CRM
  databases and saves them persistently so all notion-crm-helper skills know
  where to find the user's data.
user_invocable: true
---

## Purpose

Collect and save the Notion database IDs for the 5 CRM databases to `~/.claude/notion-crm-helper.local.md`. These IDs are required by all notion-crm-helper skills. Once saved, the config persists across all sessions and can only be updated by running this setup skill again.

## Step 1 — Check for Existing Config

Read the file `~/.claude/notion-crm-helper.local.md`.

- If the file exists and contains a YAML frontmatter block with `contacts_db_id` set, show the current config:

  ```
  Your current Notion CRM configuration:

  - Contacts DB:      [contacts_db_id]
  - Opportunities DB: [opportunities_db_id]
  - Lists DB:         [lists_db_id]
  - Templates DB:     [templates_db_id]
  - Activities DB:    [activities_db_id]
  - Parent Page:      [crm_parent_page_id or "Not set"]
  ```

  Then ask: "Would you like to update your configuration, or keep the current one?"

  - If the user wants to keep it, end the skill: "Your configuration is unchanged. All notion-crm-helper skills will continue using your saved database IDs."
  - If the user wants to update, proceed to Step 2.

- If the file does not exist or is empty, proceed directly to Step 2.

## Step 2 — Verify Notion Connection

Use `notion-search` with a broad query (e.g., "CRM") to confirm the Notion connection is active.

- If it fails with an auth error, tell the user:
  > The Notion connector doesn't appear to be connected. In Claude Code, check that the `notion` MCP server is authorized. You may need to re-connect Notion via the MCP settings.

  Do not proceed until the connection is confirmed working.

## Step 3 — Get the CRM Parent Page

Ask the user:

> What is the URL of your Notion CRM parent page? This is the page where your 5 CRM databases live (or will be created).

Extract the page ID from the URL — the 32-character hex string at the end (remove hyphens if present):
- `https://www.notion.so/My-CRM-83a0ac85cdd3464c92083b1336f7bfe7` → `83a0ac85cdd3464c92083b1336f7bfe7`
- `https://www.notion.so/83a0ac85-cdd3-464c-9208-3b1336f7bfe7` → `83a0ac85cdd3464c92083b1336f7bfe7`

Store this as `crm_parent_page_id`.

## Step 4 — Discover Database IDs

Use `notion-search` to find each of the 5 CRM databases by name. For each result, extract the database ID from the returned object.

Search for:
1. `"Contacts"` → store ID as `contacts_db_id`
2. `"Opportunities"` → store ID as `opportunities_db_id`
3. `"Lists"` → store ID as `lists_db_id`
4. `"Templates"` → store ID as `templates_db_id`
5. `"Activities"` → store ID as `activities_db_id`

For each database found, confirm with the user: "Found **Contacts** database (ID: `abc123...`). Is this the right one?"

If the user says no, ask them to paste the direct Notion database URL for that database and extract the ID manually.

If any databases are **not found**, note them as missing and tell the user:
> The following databases were not found: [names]. You can create them by running `/notion-crm-helper:create-crm` after setup, or paste their Notion URLs now.

For each missing database, ask the user if they want to:
- Paste the database URL now (to set the ID)
- Leave it blank for now (the corresponding skills won't work until it's set)

## Step 5 — Confirm Before Saving

Show the collected values to the user for confirmation before writing:

```
Ready to save your Notion CRM configuration:

- Contacts DB:      [contacts_db_id or "Not set"]
- Opportunities DB: [opportunities_db_id or "Not set"]
- Lists DB:         [lists_db_id or "Not set"]
- Templates DB:     [templates_db_id or "Not set"]
- Activities DB:    [activities_db_id or "Not set"]
- Parent Page:      [crm_parent_page_id or "Not set"]

Save this configuration?
```

If the user confirms, proceed to Step 6. If they want changes, return to Step 4 for the specific database(s) they want to change.

## Step 6 — Save the Configuration

Write the following content to `~/.claude/notion-crm-helper.local.md`, replacing any existing content:

```
---
contacts_db_id: "[CONTACTS_DB_ID]"
opportunities_db_id: "[OPPORTUNITIES_DB_ID]"
lists_db_id: "[LISTS_DB_ID]"
templates_db_id: "[TEMPLATES_DB_ID]"
activities_db_id: "[ACTIVITIES_DB_ID]"
crm_parent_page_id: "[CRM_PARENT_PAGE_ID]"
---

# Notion CRM Helper Configuration

This file stores Notion database IDs for the notion-crm-helper plugin. To update these values, run `/notion-crm-helper:setup`.
```

Leave any IDs as empty strings `""` if the user did not provide them.

Use the Write tool to create or overwrite the file at `~/.claude/notion-crm-helper.local.md`.

## Step 7 — Confirm Success

After writing the file, confirm to the user:

```
Notion CRM configuration saved.

All notion-crm-helper skills will now use your saved database IDs automatically.

Next steps:
- /notion-crm-helper:crm-status — verify all databases are reachable
- /notion-crm-helper:create-crm — create any missing databases
- /notion-crm-helper:import-contacts — import contacts from CSV

To update your configuration in the future, run /notion-crm-helper:setup again.
```

## Error Handling

- If the Write tool fails, tell the user: "Unable to save the configuration to `~/.claude/notion-crm-helper.local.md`. Please check that your `~/.claude/` directory exists and is writable."
- Never save a partial configuration without warning the user — if `contacts_db_id` is blank, note that `/import-contacts` and `/manage-list` skills will not work until it is set.
- If `notion-search` returns multiple databases with the same name, show the user all matches with their IDs and ask them to confirm which one to use.
