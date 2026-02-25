---
name: manage-templates
description: Create, view, edit, and delete message templates with {{variable}} placeholders for outreach and follow-up copy.
user_invocable: true
---

# Manage Message Templates

Create and manage reusable templates with `{{variable}}` placeholders — for email copy, follow-up messages, meeting notes, or any outreach content. Templates are stored as rows in the Notion Templates database.

## Step 0: Load Configuration

Read the file `~/.claude/notion-crm-helper.local.md`.

- If the file does not exist or the YAML frontmatter does not contain `templates_db_id`, stop and tell the user:
  > Notion CRM Helper is not configured yet. Run `/notion-crm-helper:setup` to connect your Notion databases before using this skill.

- If the file exists, extract `templates_db_id` and `contacts_db_id` from the YAML frontmatter. Use these IDs directly in all Notion operations below instead of searching by database name.

## Available Actions

### List All Templates

Use `notion-fetch` with `templates_db_id` from config to access the Templates database, then fetch its rows. Display in a table:

```
Templates:
| Name              | Variables                    |
|-------------------|------------------------------|
| Follow-up Meeting | first_name, company          |
| New Offering      | first_name, product          |
| Check-in          | first_name                   |
```

### Create a Template

Ask the user for:
1. **Template name** — e.g., "Conference Follow-up"
2. **Template content** — e.g., "Hi {{first_name}}, great meeting you at {{event}}. Let's connect this week!"

Scan the content for `{{variable}}` patterns and list the detected variables.

Use `notion-create-pages` to create a new row in the Templates database with:
- Template Name = provided name
- Content = the template text
- Variables = comma-separated list of detected variables

### Edit a Template

Use `notion-search` scoped to the templates database (using `templates_db_id`) to find the template by name, then use `notion-update-page` to modify its content or name.

### Delete a Template

Use `notion-update-page` to archive the template page (set archived: true).

### Preview a Template

Fetch the template content with `notion-fetch`, then fetch the target contact's record and manually substitute `{{variable}}` placeholders with the contact's actual field values:

```
Template: Follow-up Meeting
For: John Smith (Acme Corp)

"Hi John, great meeting you at the conference. Let's connect this week!"
```

## Arguments

- `/manage-templates` — List all templates
- `/manage-templates create` — Start creating a new template
- `/manage-templates [name]` — Show details for a specific template

## Available Variables

- `{{contact_name}}` — Full name
- `{{first_name}}` — First name (split from contact_name at the first space)
- `{{last_name}}` — Last name (remainder after first space)
- `{{email}}` — Email address
- `{{phone}}` — Phone number
- `{{company}}` — Company name
