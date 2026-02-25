# Notion CRM Helper

A Claude Code plugin that provides full CRM functionality powered by Notion. Manage contacts, opportunities, lists, templates, and activities — all conversationally through Claude.

Works out of the box with the Notion MCP connector. No extra tools or setup required beyond authorizing Notion.

## Requirements

- **Notion MCP connector** — Uses Notion's official MCP server (`https://mcp.notion.com/mcp`). Claude Code will prompt you to authorize Notion on first use.

## Setup

### 1. Install the Plugin

Install via the Claude Code plugin marketplace.

### 2. Authorize Notion

On first use, Claude Code will prompt you to connect your Notion workspace via OAuth.

### 3. Initialize Your CRM

In Claude Code, run:
```
/setup
```

Then create your databases:
```
/create-crm
```

## Commands

| Command | Description |
|---------|-------------|
| `/setup` | First-time configuration |
| `/create-crm` | Create all CRM databases in Notion |
| `/crm-status` | Check system health and database counts |
| `/import-contacts` | Import contacts from CSV |
| `/manage-templates` | Create/edit message templates |
| `/manage-list` | Manage contact lists |
| `/crm-assistant` | Conversational CRM assistant for contacts, pipeline, and activities |

## CRM Databases

The plugin creates 5 databases under your parent page:

1. **Contacts** — People, leads, decision-makers
2. **Opportunities** — Sales pipeline and deals
3. **Lists** — Contact groups for segmentation
4. **Templates** — Reusable copy with {{variable}} placeholders
5. **Activities** — Calls, emails, meetings, notes, tasks

## Architecture

- **Storage**: All data lives in Notion — no local database
- **MCP Server**: Uses Notion's official hosted MCP at `https://mcp.notion.com/mcp`
- **Skills**: Conversational workflows for common CRM operations
- **crm-assistant**: Conversational skill for autonomous CRM task handling
