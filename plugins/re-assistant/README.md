# re-assistant

Real estate assistant skills for SF agents — disclosure package summaries, MLS comparable analysis, and offer letters.

> **Note:** This plugin is configured for David Raygorodsky / The Nolan Group / Vanguard Properties. The `offer-letter` skill has the sender identity hardcoded by design.

## Skills

### `re-assistant:disclosure-package-summary`

Analyzes a real estate disclosure package (multiple PDFs) and produces a client-ready bullet summary ready to paste into Google Docs.

**Trigger phrases:** "analyze my disclosure package", "summarize the disclosures", "review the disclosure documents", "create a disclosure summary"

**Inputs collected interactively:**
- Client name(s), property address, list price, MLS sq ft, beds/baths, property type
- Optional: target offer price or $/sf
- Uploaded disclosure PDFs

**Output:** 13-section structured summary covering property snapshot, title, HOA, tenancy, permits, seller disclosures, inspection reports, NHD hazards, repair cost totals, and condition summary (~1,000 words of bullets).

---

### `re-assistant:comparable-analysis`

Analyzes MLS comparable properties to determine market value and assess whether an offer price is below, at, or above market.

**Trigger phrases:** "analyze comps", "run a comp analysis", "do a CMA", "compare similar properties", "look at the comparables", "review the MLS comps"

**Inputs collected interactively:**
- Subject property details (address, offer price, beds, baths, sq ft, lot, parking, year built)
- Attached MLS comparables PDF

**Output:** Value conclusion (5–8 sentences), detailed breakdown of each comparable with Zenlist link and analyst POV, and a summary table.

---

### `re-assistant:offer-letter`

Drafts a professional, concise offer letter from David Raygorodsky (The Nolan Group, Vanguard Properties) to a listing agent.

**Trigger phrases:** "write an offer letter", "draft the offer letter to the listing agent", "compose an offer letter", "I need to send an offer"

**Inputs collected interactively:**
- Listing agent name, client name(s), property address, offer price
- Closing timeline, target close date (optional)
- Contingencies (or "none — clean offer")
- Buyer broker fee details

**Output:** Short, mobile-readable agent-to-agent letter following executive tone guidelines.

## Installation

```bash
claude --plugin-dir /path/to/re-assistant
```

## Author

betojuareziii
