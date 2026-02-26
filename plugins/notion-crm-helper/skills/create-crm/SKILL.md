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

Read the file `.claude/settings.json` from the current project directory. Parse it as JSON and check for `NOTION_CRM_PARENT_PAGE_ID` in the `env` object.

- If the file does not exist or the `env` object does not contain `NOTION_CRM_PARENT_PAGE_ID`, stop and tell the user:
  > Notion CRM Helper is not configured yet. Run `/notion-crm-helper:setup` first so the parent page ID is saved before creating databases.
  > Make sure you have a project folder open — configuration is saved to `.claude/settings.json` in your project directory.

- If the file exists and `NOTION_CRM_PARENT_PAGE_ID` is set, extract its value. Use this as the parent page for all database creation below.

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

After each database is created, capture its ID from the API response. Once all databases are created, read the existing `.claude/settings.json`, merge the six new database IDs into the `env` object (preserving `NOTION_CRM_PARENT_PAGE_ID` and any other existing keys), and write the file back using the Write tool.

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

Database IDs have been saved to .claude/settings.json.
All notion-crm-helper skills are now ready to use.
```
