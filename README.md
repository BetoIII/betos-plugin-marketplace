# Beto's Plugin Marketplace

A collection of Claude Code plugins for messaging, CRM, real estate, and fintech support workflows.

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
- `/notion-crm-helper:setup` — First-time configuration: creates Notion databases (Contacts, Accounts, Opportunities) and saves config to `.claude/settings.json`
- `/notion-crm-helper:crm-helper` — Conversational CRM: manage contacts, pipeline, activities, and bulk imports from CSV or JSON

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
- `/re-assistant:offer-email` — Drafts a professional agent-to-agent offer email
- `/re-assistant:setup` — Configure your agent profile

---

### [rain-platform](plugins/rain-platform)

Support operations toolkit for the Rain team — Pylon issue triage, virtual card art compliance checking, and partner onboarding video review.

**Install:**
```
/plugin install rain-platform@BetoIII/betos-plugin-marketplace
```

**Skills:**
- `triage-pylon-issues` — Fetches Pylon issues, classifies them to Horatio or Rain based on the support scope agreement, and tags them for routing
- `virtual-card-art-checker` — Reviews virtual/digital card art submissions against Visa Digital Card Brand Standards (Sept 2025); validates technical specs, visual compliance, extracts RGB fallback colors, and generates an output review image with bleed border and sample PAN overlay
- `partner-video-review` — Analyzes partner sandbox onboarding screen recordings against Rain's compliance requirements; frame-extracts the video and produces a structured pass/fail report

---

## License

MIT License — see [LICENSE](LICENSE) file for details.
