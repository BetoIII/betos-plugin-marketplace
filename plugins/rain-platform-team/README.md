# Rain Platform Team

Support operations toolkit for the Rain team — virtual card art compliance checking, partner onboarding video review, Rain API documentation search, collateral contract admin wallet lookup, and Rocketlane project management via natural language.

## Skills

### `card-art-checker`

Reviews digital/virtual card art submissions against Visa Digital Card Brand Standards and Rain's internal requirements. Produces a structured compliance report and extracts RGB fallback color values.

**What it does:**
1. **Gets the image file** — handles direct uploads, URLs, or explicit file paths
2. **Runs the technical spec checker** — validates dimensions (1536×969px), format (PNG), color mode (RGB), and DPI (72)
3. **Visually inspects the design** — checks Visa Brand Mark presence/placement, prohibited elements, orientation, and layout
4. **Extracts RGB fallback colors** — background, foreground, and label colors for card submission

**Trigger phrases:**
- "check this card art" / "review my card design"
- "does this pass" / "card submission review"
- "validate card art" / "is this compliant"
- "what are the RGB fallback colors"

---

### `partner-video-review`

Reviews a partner's sandbox onboarding screen recording against Rain's compliance requirements. Extracts frames from the video, analyzes each screen, and produces a structured pass/fail report.

**What it does:**
1. **Identifies the flow type** — Business, US Consumer, or International Consumer
2. **Extracts frames** — two-pass extraction (broad survey + dense final-third for consent screens)
3. **Checks KYC/KYB approval state, consent checkboxes, and card creation**
4. **Produces a compliance report** — pass/fail per requirement with specific observations and actionable feedback

**Trigger phrases:**
- "review our onboarding video" / "check our sandbox recording"
- "does this pass" / "is our flow correct"
- "can you review our demo video"
- "check our onboarding recording before we go live"

---

### `rain-collateral-admin`

Looks up the collateral contract admin wallet address(es) for a Rain user by querying the Weather Station internal API via a logged-in Chrome session. Returns the EVM wallet plus Solana/Stellar/Tron addresses when set.

**What it does:**
1. **Opens a Chrome tab** — uses Claude in Chrome (`tabs_context_mcp`) to get a tab
2. **Navigates to Weather Station** — ensures the auth session is active (VPN required)
3. **Fetches user data** — runs JS in the tab to call the Weather Station API with the session token
4. **Returns the addresses** — surfaces EVM (collateral admin), Solana, Stellar, and Tron

**Trigger phrases:**
- "what wallet is on this user" / "get the address for user X"
- "collateral admin for [UUID]"
- "what's the wallet attached to user [ID]"
- "find the wallet for this user ID"

---

### `rocketlane-api`

Full read/write access to the Rocketlane API from natural language — project lookups, task management, time tracking, attachments, custom fields, and more. Prompts once for your Rocketlane API key and stores it locally at `~/.config/rain-claude/rocketlane.env` (never in the repo).

**What it does:**
1. **First-run setup** — asks for your Rocketlane API key once, validates it live, persists it outside the repo with `chmod 600`
2. **Maps natural language to endpoints** — projects, tasks, phases, fields, users, time entries, spaces, attachments, invoices
3. **Handles the API's quirks** — auto-pagination, `field.operator=value` filters, the `/api/v1` attachments split, custom-field ID resolution
4. **Write safety** — shows the exact payload and asks for confirmation before any create/update/delete

**Trigger phrases:**
- "find [company] in Rocketlane" / "what's the status of [client]"
- "who's on the team for" / "what stage is [client] at"
- "create a task" / "log time" / "update the stage"
- "download the attachment from [task]"

---

## Installation

```
/plugin install rain-platform-team@BetoIII/betos-plugin-marketplace
```

## Author

betojuareziii
