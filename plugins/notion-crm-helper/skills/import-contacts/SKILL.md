---
name: import-contacts
description: Import contacts from a CSV file into the Notion CRM. Maps columns, validates data, and creates contact records in the Contacts database.
user_invocable: true
---

# Import Contacts from CSV

Import contacts from a CSV file into your Notion CRM Contacts database.

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

Also silently read `.claude/crm-schema.json`. If it exists, parse it and store as `contact_schema`. Extract:
- `contact_schema.databases.contacts.properties` — valid property names and types for the Contacts database
- `contact_schema.select_option_aliases.contacts` — alias map for resolving select/multi_select values in the Contacts database
- Check `last_validated`: if > 7 days old, warn the user once that the schema may be stale.

If `.claude/crm-schema.json` does not exist, set `contact_schema` to null and continue — column mapping will use the built-in defaults below.

## Flow

### Step 1: Read the CSV File

Accept a file path as argument: `/import-contacts /path/to/contacts.csv`

If no path is provided, ask the user for the CSV file path.

Read and parse the file. Show the first 5 rows as a preview:

```
CSV Preview (5 of 150 rows):
| Name          | Email              | Phone      | Company    | Title     |
|---------------|-------------------|------------|------------|-----------|
| John Smith    | john@acme.com     | 555-1234   | Acme Corp  | VP Sales  |
| Sarah Jones   | sarah@beta.io     | 555-5678   | Beta Inc   | CTO       |
...
```

### Step 2: Map Columns

Propose a column mapping from CSV headers to Notion Contact properties:

```
Proposed mapping:
  CSV "Name"     → Contact Name
  CSV "Email"    → Contact Email
  CSV "Phone"    → Contact Phone
  CSV "Company"  → Company
  CSV "Title"    → Title

Does this look right? (You can adjust mappings)
```

Common mappings:
- name, full_name, contact_name → Contact Name
- email, email_address → Contact Email
- phone, phone_number, mobile → Contact Phone
- company, organization, employer → Company
- title, job_title, position → Title
- linkedin, linkedin_url → LinkedIn
- source, lead_source → Source

**Schema validation (if `contact_schema` is loaded)**: After proposing the mapping, validate each target property name against `contact_schema.databases.contacts.properties`. If a proposed target property does not exist in the schema, flag it to the user: "Note: property '[name]' was not found in your Contacts schema. Please confirm the correct property name." For any `select` or `multi_select` columns being mapped, display the valid options from the schema so the user can preview what values their CSV data will be resolved to:
```
CSV column "Engagement" → Engagement Level (select)
  Valid options: 🔥 Hot, ❄️ Cold, 🌤 Warm
  (Your CSV values will be automatically matched — "Hot" → "🔥 Hot", etc.)
```

### Step 3: Verify the Contacts Database

Use `notion-fetch` with the `contacts_db_id` from config to verify the Contacts database is reachable. If the fetch fails, tell the user to run `/notion-crm-helper:setup` to verify their configuration.

### Step 4: Validate Data

Check for:
- Invalid emails (warn but don't skip)
- Missing required fields (name)
- Duplicate emails within the CSV

Report validation results before importing.

### Step 5: Import

For each contact in batches of 10:
1. Use `notion-search` to check if a contact with the same email already exists.
2. **Account upsert** (if `accounts_db_id` is configured and the contact has a Company value): use `notion-search` to check if an Account with that company name already exists in `accounts_db_id`. If not, create a new Account record using `notion-create-pages`. Track newly created accounts to avoid re-creating them for duplicate companies in the same batch.
3. **Alias resolution** (if `contact_schema` is loaded): before constructing the `notion-create-pages` or `notion-update-page` payload, resolve all `select` and `multi_select` column values using the three-level lookup: `contact_schema.select_option_aliases["contacts"][property_name][raw_csv_value]` (case-insensitive). If a match is found, replace the CSV value with the canonical schema value (e.g., `"Hot"` → `"🔥 Hot"`). If no alias match is found, use the raw value as-is.
4. If the contact exists, use `notion-update-page` to update their record with resolved values.
5. If the contact doesn't exist, use `notion-create-pages` to create a new row in the Contacts database with resolved values.

Report progress every 10 contacts.

### Step 6: Optionally Add to List

Ask: "Would you like to add these imported contacts to a list?"

If yes, use `notion-fetch` with `lists_db_id` from config to access the Lists database, then use `notion-create-pages` or `notion-update-page` to add the contact to the appropriate list.

### Step 7: Report

```
Import Complete!
  Created: 142
  Updated: 5 (existing contacts matched by email)
  Skipped: 3 (duplicate emails in CSV)
  Accounts created: 18 (new company records upserted)

All contacts are now in your Notion CRM.
```
