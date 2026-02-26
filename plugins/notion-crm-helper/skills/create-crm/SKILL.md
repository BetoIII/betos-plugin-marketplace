---
name: create-crm
description: Create all CRM databases (Contacts, Accounts, Opportunities, Lists, Templates, Activities) in your Notion workspace under the CRM parent page.
user_invocable: false
---

# Create CRM Databases

This skill creates all 6 CRM databases in your Notion workspace under a parent page you specify.

## Prerequisites

- Notion must be authorized.
- `/notion-crm-helper:setup` must have been run at least once so the parent page ID is stored.

## Steps

### Step 0: Load Configuration

Read the file `~/.claude/notion-crm-helper.local.md`.

- If the file does not exist or the YAML frontmatter does not contain `crm_parent_page_id`, stop and tell the user:
  > Notion CRM Helper is not configured yet. Run `/notion-crm-helper:setup` first so the parent page ID is saved before creating databases.

- If the file exists, extract `crm_parent_page_id` from the YAML frontmatter. Use this as the parent page for all database creation below.

### Step 1: Confirm the Parent Page ID

Show the user the parent page ID from config and confirm: "I'll create the CRM databases under Notion page `[crm_parent_page_id]`. Is that correct?"

If they want to use a different page, accept a URL and extract the ID, but remind them to re-run `/notion-crm-helper:setup` to update their saved config.

### Step 2: Create Databases in Order

Use `notion-create-database` to create each database under the parent page. Report progress after each.

1. **Contacts** — Properties:
   - Contact Name (title)
   - Title (rich_text)
   - Contact Email (email)
   - Contact Phone (phone_number)
   - Company (rich_text — should match an Account name)
   - LinkedIn (url)
   - Buying Role (select: Champion, Decision Maker, Influencer, End User, Blocker)
   - Engagement Level (select: Hot, Warm, Cold, Unresponsive)
   - Source (multi_select)
   - Last Contact (date)
   - Lists (multi_select — list names this contact belongs to)

2. **Accounts** — Properties:
   - Account Name (title)
   - Industry (select: Technology, Finance, Healthcare, Retail, Manufacturing, Education, Other)
   - Website (url)
   - Size (select: 1–10, 11–50, 51–200, 201–1000, 1000+)
   - Status (select: Prospect, Active, Partner, Churned)
   - Notes (rich_text)

3. **Opportunities** — Properties:
   - Name (title)
   - Stage (select: Lead, Qualified, Proposal, Negotiation, Closed Won, Closed Lost)
   - Deal Value (number)
   - Company (rich_text — should match an Account name)
   - Expected Close Date (date)
   - Next Step (rich_text)
   - Lead Source (multi_select)
   - Lost Reason (select)

4. **Lists** — Properties:
   - List Name (title)
   - Type (select: Campaign, Segment, Event, Custom)
   - Description (rich_text)
   - Status (select: Active, Archived)

5. **Templates** — Properties:
   - Template Name (title)
   - Content (rich_text)
   - Variables (rich_text — comma-separated list of detected variables)

6. **Activities** — Properties:
   - Title (title)
   - Type (select: Email, Call, Meeting, Note, Task)
   - Date (date)
   - Notes (rich_text)
   - Contact (rich_text — contact name for reference)

### Step 3: Save Database IDs to Config

After each database is created, capture its ID from the API response. Once all databases are created, update `~/.claude/notion-crm-helper.local.md` using the Write tool — preserve the existing `crm_parent_page_id` and fill in all six database IDs with the newly created values.

### Step 4: Verify and Report

Use `notion-fetch` with each newly saved database ID to confirm the databases are reachable. Report:

```
CRM databases created successfully!

  1. Contacts      — People, leads, decision-makers
  2. Accounts      — Companies and organizations
  3. Opportunities — Sales pipeline and deals
  4. Lists         — Contact groups for campaigns
  5. Templates     — Message templates with {{variables}}
  6. Activities    — Calls, emails, meetings, notes, tasks

Database IDs have been saved to ~/.claude/notion-crm-helper.local.md.
All notion-crm-helper skills are now ready to use.
```
