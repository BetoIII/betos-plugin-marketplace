# Rain

Support operations toolkit for the Rain team — Pylon issue triage, routing, and classification against the Horatio/Rain support scope agreement.

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

## Installation

```
/plugin install rain@BetoIII/betos-plugin-marketplace
```

## Author

betojuareziii
