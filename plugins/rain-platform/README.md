# Rain Platform

Support operations toolkit for the Rain team — Pylon issue triage, card art compliance checking, and partner onboarding video review.

## Skills

### `triage-pylon-issues`

Classifies incoming Pylon support issues and routes them to the correct team (Horatio or Rain) based on the shared support scope agreement.

**What it does:**
1. **Fetches the issue** — reads both metadata (`get_issue`) and the full conversation (`get_issue_messages`) before making a call
2. **Classifies by domain** — matches the issue to a domain (General CX, Technical Support, Compliance, Disputes, Account Management) and determines the owning team
3. **Tags the issue** — adds the team name and domain as tags via `update_issue`, always preserving existing tags

**Trigger phrases:**
- "triage issues" / "triage incoming tickets"
- "categorize a Pylon issue" / "classify support tickets"
- "who handles this issue" / "route a ticket"
- "is this a Horatio or Rain issue"
- "check the new tickets"

---

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

## Installation

```
/plugin install rain-platform@BetoIII/betos-plugin-marketplace
```

## Author

betojuareziii
