---
name: setup
description: >-
  This skill should be used when the user says "set up notion crm", "configure
  notion crm helper", "run setup", "update my crm databases", or runs
  /notion-crm-helper:setup. Collects the Notion database IDs for all 6 CRM
  databases and saves them persistently so all notion-crm-helper skills know
  where to find the user's data.
user_invocable: true
---

## Purpose

Collect and save the Notion database IDs for the 6 CRM databases to `.claude/settings.json` in the current project directory. These IDs are required by all notion-crm-helper skills. Once saved, the config persists for the project and can only be updated by running this setup skill again.

The expected format is documented in `examples/settings.json` inside the notion-crm-helper plugin.

## Step 1 — Check for Existing Config

Read the file `.claude/settings.json` from the current project directory. Parse it as JSON and check for the presence of `NOTION_CRM_CONTACTS_DB_ID` in the `env` object.

- If the project directory does not have a `.claude/settings.json` file, or the file exists but has no `env` key, proceed directly to Step 2.

- If the file exists and `NOTION_CRM_CONTACTS_DB_ID` is set in `env`, show the current config:

  ```
  Your current Notion CRM configuration:

  - Contacts DB:      [NOTION_CRM_CONTACTS_DB_ID]
  - Accounts DB:      [NOTION_CRM_ACCOUNTS_DB_ID or "Not set"]
  - Opportunities DB: [NOTION_CRM_OPPORTUNITIES_DB_ID]
  - Lists DB:         [NOTION_CRM_LISTS_DB_ID]
  - Templates DB:     [NOTION_CRM_TEMPLATES_DB_ID]
  - Activities DB:    [NOTION_CRM_ACTIVITIES_DB_ID or "Not set"] (optional)
  - Parent Page:      [NOTION_CRM_PARENT_PAGE_ID or "Not set"]
  ```

  Then ask: "Would you like to update your configuration, or keep the current one?"

  - If the user wants to keep it, end the skill: "Your configuration is unchanged. All notion-crm-helper skills will continue using your saved database IDs."
  - If the user wants to update, proceed to Step 2.

- If no project folder is loaded (no `.claude/` directory is accessible), stop and tell the user:
  > No project folder detected. Please open a project directory in Claude Code first — configuration is saved to `.claude/settings.json` in your project folder.

## Step 2 — Verify Notion Connection

Use `notion-search` with a broad query (e.g., "CRM") to confirm the Notion connection is active.

- If it fails with an auth error, tell the user:
  > The Notion connector doesn't appear to be connected. In Claude Code, check that the `notion` MCP server is authorized. You may need to re-connect Notion via the MCP settings.

  Do not proceed until the connection is confirmed working.

## Step 3 — Get the CRM Parent Page

Ask the user:

> What is the URL of your Notion CRM parent page? This is the page where your 6 CRM databases live (or will be created).

Extract the page ID from the URL — the 32-character hex string at the end (remove hyphens if present):
- `https://www.notion.so/My-CRM-83a0ac85cdd3464c92083b1336f7bfe7` → `83a0ac85cdd3464c92083b1336f7bfe7`
- `https://www.notion.so/83a0ac85-cdd3-464c-9208-3b1336f7bfe7` → `83a0ac85cdd3464c92083b1336f7bfe7`

Store this as the value for `NOTION_CRM_PARENT_PAGE_ID`.

## Step 4 — Discover Database IDs

Use `notion-search` to find each of the 6 CRM databases by name. For each result, extract the database ID from the returned object.

Search for:
1. `"Contacts"` → store ID as `NOTION_CRM_CONTACTS_DB_ID`
2. `"Accounts"` → store ID as `NOTION_CRM_ACCOUNTS_DB_ID`
3. `"Opportunities"` → store ID as `NOTION_CRM_OPPORTUNITIES_DB_ID`
4. `"Lists"` → store ID as `NOTION_CRM_LISTS_DB_ID`
5. `"Templates"` → store ID as `NOTION_CRM_TEMPLATES_DB_ID`
6. `"Activities"` → store ID as `NOTION_CRM_ACTIVITIES_DB_ID` *(optional — if not found, skip without flagging as missing)*

For each database found, confirm with the user: "Found **Contacts** database (ID: `abc123...`). Is this the right one?"

If the user says no, ask them to paste the direct Notion database URL for that database and extract the ID manually.

If any **required** databases (Contacts, Accounts, Opportunities, Lists, Templates) are **not found**, note them as missing and tell the user:
> The following databases were not found: [names]. You can create them by running `/notion-crm-helper:create-crm` after setup, or paste their Notion URLs now.

If **Activities** is not found, note it as optional:
> Activities database not found — this is optional. Activity logging won't be available until it's configured.

For each missing required database, ask the user if they want to:
- Paste the database URL now (to set the ID)
- Leave it blank for now (the corresponding skills won't work until it's set)

## Step 5 — Confirm Before Saving

Show the collected values to the user for confirmation before writing:

```
Ready to save your Notion CRM configuration:

- Contacts DB:      [NOTION_CRM_CONTACTS_DB_ID or "Not set"]
- Accounts DB:      [NOTION_CRM_ACCOUNTS_DB_ID or "Not set"]
- Opportunities DB: [NOTION_CRM_OPPORTUNITIES_DB_ID or "Not set"]
- Lists DB:         [NOTION_CRM_LISTS_DB_ID or "Not set"]
- Templates DB:     [NOTION_CRM_TEMPLATES_DB_ID or "Not set"]
- Activities DB:    [NOTION_CRM_ACTIVITIES_DB_ID or "Not set"] (optional)
- Parent Page:      [NOTION_CRM_PARENT_PAGE_ID or "Not set"]

Save this configuration?
```

If the user confirms, proceed to Step 6. If they want changes, return to Step 4 for the specific database(s) they want to change.

## Step 6 — Save the Configuration

Read the existing `.claude/settings.json` file if it exists (to preserve other keys such as `$schema`, `permissions`, or unrelated `env` entries). Parse it as JSON.

Merge the `NOTION_CRM_*` env vars into the `env` object, leaving all other keys untouched. If the file does not exist, create it with a `$schema` key and an `env` object.

Write the result back to `.claude/settings.json`. The file should look like:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "env": {
    "NOTION_CRM_CONTACTS_DB_ID": "[CONTACTS_DB_ID]",
    "NOTION_CRM_ACCOUNTS_DB_ID": "[ACCOUNTS_DB_ID]",
    "NOTION_CRM_OPPORTUNITIES_DB_ID": "[OPPORTUNITIES_DB_ID]",
    "NOTION_CRM_LISTS_DB_ID": "[LISTS_DB_ID]",
    "NOTION_CRM_TEMPLATES_DB_ID": "[TEMPLATES_DB_ID]",
    "NOTION_CRM_ACTIVITIES_DB_ID": "[ACTIVITIES_DB_ID]",
    "NOTION_CRM_PARENT_PAGE_ID": "[CRM_PARENT_PAGE_ID]"
  }
}
```

Leave any IDs as empty strings `""` if the user did not provide them.

Use the Write tool to save the file at `.claude/settings.json` in the current project directory.

## Step 7 — Confirm Success

After writing the file, confirm to the user:

```
Notion CRM configuration saved to .claude/settings.json.

All notion-crm-helper skills will now use your saved database IDs automatically.

Next steps:
- /notion-crm-helper:crm-status — verify all databases are reachable
- /notion-crm-helper:create-crm — create any missing databases
- /notion-crm-helper:import-contacts — import contacts from CSV

To update your configuration in the future, run /notion-crm-helper:setup again.
```

## Error Handling

- If the Write tool fails, tell the user: "Unable to save the configuration to `.claude/settings.json`. Please check that your project's `.claude/` directory exists and is writable. Make sure you have a project folder open in Claude Code."
- Never save a partial configuration without warning the user — if `NOTION_CRM_CONTACTS_DB_ID` is blank, note that `/import-contacts` and `/manage-list` skills will not work until it is set. `NOTION_CRM_ACTIVITIES_DB_ID` is optional and may be left blank without blocking setup.
- If `notion-search` returns multiple databases with the same name, show the user all matches with their IDs and ask them to confirm which one to use.
