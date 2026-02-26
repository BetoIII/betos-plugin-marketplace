---
name: manage-list
description: Create and manage contact lists for organizing contacts into groups for campaigns, segments, and events.
user_invocable: true
---

# Manage Contact Lists

Create and manage lists of contacts for targeted campaigns, segmentation, and event tracking. Lists are stored in the Notion Lists database.

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

Use these IDs directly in all Notion operations below instead of searching by database name.

## Available Actions

### List All Lists

Use `notion-fetch` with `lists_db_id` from config to access the Lists database and fetch all rows. Display:

```
Lists:
| Name                 | Type     | Status | Description               |
|----------------------|----------|--------|---------------------------|
| Enterprise Prospects | Segment  | Active | Decision-makers at 200+ orgs |
| Conference Leads     | Event    | Active | Met at SaaStr 2024        |
| Q1 Campaign          | Campaign | Active | January outreach targets  |
```

### Create a List

Ask the user for:
1. **List name** — e.g., "Enterprise Prospects"
2. **Description** (optional)
3. **Type** — Campaign, Segment, Event, or Custom

Use `notion-create-pages` to create a new row in the Lists database.

### View List Members

Ask the user which list they want to view. Use `notion-fetch` with `contacts_db_id` from config to query contacts, filtering for those whose `Lists` multi_select property contains the list name.

```
Enterprise Prospects (25 contacts):
1. John Smith — VP Sales, Acme Corp — john@acme.com — 555-1234
2. Sarah Jones — CTO, Beta Inc — sarah@beta.io — 555-5678
...
```

### Add Contacts to a List

Options:
- **By name**: "Add John Smith to the Enterprise Prospects list"
  - Use `notion-search` to find the contact, then `notion-update-page` to add the list name to their `Lists` multi_select property
- **By criteria**: "Add all Hot contacts to the Enterprise Prospects list"
  - Use `notion-search` to find matching contacts, then update the `Lists` property on each

### Remove Contacts from a List

Use `notion-update-page` to remove the list name from the contact's `Lists` multi_select property.

### Archive a List

Use `notion-update-page` to set the list's Status to "Archived".

## Arguments

- `/manage-list` — Show all lists
- `/manage-list [name]` — Show members of a specific list
- `/manage-list create` — Create a new list
