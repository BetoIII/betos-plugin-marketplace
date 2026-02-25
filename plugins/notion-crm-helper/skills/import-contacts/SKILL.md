---
name: import-contacts
description: Import contacts from a CSV file into the Notion CRM. Maps columns, validates data, and creates contact records in the Contacts database.
user_invocable: true
---

# Import Contacts from CSV

Import contacts from a CSV file into your Notion CRM Contacts database.

## Step 0: Load Configuration

Read the file `~/.claude/notion-crm-helper.local.md`.

- If the file does not exist or the YAML frontmatter does not contain `contacts_db_id`, stop and tell the user:
  > Notion CRM Helper is not configured yet. Run `/notion-crm-helper:setup` to connect your Notion databases before using this skill.

- If the file exists, extract `contacts_db_id` and `lists_db_id` from the YAML frontmatter. Use these IDs directly in all Notion operations below instead of searching by database name.

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
1. Use `notion-search` to check if a contact with the same email already exists
2. If it exists, use `notion-update-page` to update their record
3. If it doesn't exist, use `notion-create-pages` to create a new row in the Contacts database

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

All contacts are now in your Notion CRM.
```
