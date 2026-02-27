# Beto's Plugin Marketplace

A collection of Claude Code plugins for messaging, CRM, and real estate workflows.

## Installation

Add this marketplace to your Claude Code instance, then install any plugin:

```
/plugin marketplace add BetoIII/betos-plugin-marketplace
/plugin install <plugin-name>@BetoIII/betos-plugin-marketplace
```

---

## Plugins

### [bulk-messenger](plugins/bulk-messenger)

Send personalized bulk SMS messages to multiple contacts via Apple Messages.app — directly from Claude.

**Install:**
```
/plugin install bulk-messenger@BetoIII/betos-plugin-marketplace
```

**Skills:**
- `/send-messages` — Collect recipients, compose a template with `{{variables}}`, preview every message, and send one-by-one via AppleScript
- `/web-builder` — Visual SMS composer and message preview tool (used internally by `send-messages`)

**Requirements:** macOS + Messages.app configured with SMS enabled

---

### [notion-crm-helper](plugins/notion-crm-helper)

Notion-powered CRM for managing contacts, opportunities, and activities — all conversationally through Claude.

**Install:**
```
/plugin install notion-crm-helper@BetoIII/betos-plugin-marketplace
```

**Skills:**
- `/setup` — First-time configuration: creates 5 Notion databases (Contacts, Opportunities, Lists, Templates, Activities) and saves config to `.claude/settings.json`
- `/crm-status` — Check system health and database record counts
- `/crm-assistant` — Conversational CRM: manage contacts, pipeline, activities, and bulk imports from CSV or JSON

**Requirements:** Notion MCP connector (Claude Code will prompt for OAuth on first use)

---

### [re-assistant](plugins/re-assistant)

Real estate assistant for buyer's agents — disclosure package summaries, MLS comparable analysis, and offer letters.

> Configured for David Raygorodsky / The Nolan Group / Vanguard Properties. The `offer-letter` skill has sender identity hardcoded by design.

**Install:**
```
/plugin install re-assistant@BetoIII/betos-plugin-marketplace
```

**Skills:**
- `/re-assistant:disclosure-package-summary` — Analyzes disclosure PDFs and produces a 13-section client-ready bullet summary
- `/re-assistant:comparable-analysis` — Reviews MLS comps to determine market value relative to an offer price
- `/re-assistant:offer-letter` — Drafts a concise agent-to-agent offer letter
- `/re-assistant:setup` — Configure your agent profile

---

## License

MIT License — see [LICENSE](LICENSE) file for details.
