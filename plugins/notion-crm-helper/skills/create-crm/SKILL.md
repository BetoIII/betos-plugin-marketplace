---
name: create-crm
description: Create all CRM databases (Contacts, Opportunities, Lists, Templates, Activities) in your Notion workspace under the CRM parent page.
user_invocable: true
---

# Create CRM Databases

This skill creates all 5 CRM databases in your Notion workspace under a parent page you specify.

## Prerequisites

- Notion must be authorized (run `/setup` if not done yet).
- You need the URL of an existing Notion page to serve as the CRM parent.

## Steps

### Step 1: Get the Parent Page ID

Ask the user for their CRM parent page URL if not already provided. Extract the 32-character ID from the URL.

### Step 2: Create Databases in Order

Use `notion-create-database` to create each database under the parent page. Report progress after each.

1. **Contacts** — Properties:
   - Contact Name (title)
   - Title (rich_text)
   - Contact Email (email)
   - Contact Phone (phone_number)
   - Company (rich_text)
   - LinkedIn (url)
   - Buying Role (select: Champion, Decision Maker, Influencer, End User, Blocker)
   - Engagement Level (select: Hot, Warm, Cold, Unresponsive)
   - Source (multi_select)
   - Last Contact (date)
   - Lists (multi_select — list names this contact belongs to)

2. **Opportunities** — Properties:
   - Name (title)
   - Stage (select: Lead, Qualified, Proposal, Negotiation, Closed Won, Closed Lost)
   - Deal Value (number)
   - Expected Close Date (date)
   - Next Step (rich_text)
   - Lead Source (multi_select)
   - Lost Reason (select)

3. **Lists** — Properties:
   - List Name (title)
   - Type (select: Campaign, Segment, Event, Custom)
   - Description (rich_text)
   - Status (select: Active, Archived)

4. **Templates** — Properties:
   - Template Name (title)
   - Content (rich_text)
   - Variables (rich_text — comma-separated list of detected variables)

5. **Activities** — Properties:
   - Title (title)
   - Type (select: Email, Call, Meeting, Note, Task)
   - Date (date)
   - Notes (rich_text)
   - Contact (rich_text — contact name for reference)

### Step 3: Verify and Report

Use `notion-search` to confirm all 5 databases now exist. Report:

```
CRM databases created successfully!

  1. Contacts      — People, leads, decision-makers
  2. Opportunities — Sales pipeline and deals
  3. Lists         — Contact groups for campaigns
  4. Templates     — Message templates with {{variables}}
  5. Activities    — Calls, emails, meetings, notes, tasks

All databases are ready in Notion. You can manage your CRM from
Claude or view and edit directly in Notion.
```
