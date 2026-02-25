---
name: comparable-analysis
description: >-
  This skill should be used when a user asks to "analyze comps", "run a comp
  analysis", "compare similar properties", "look at the comparables", "do a
  CMA", "evaluate the comparables", "review the MLS comps", or attaches an
  MLS PDF for a property they are buying or writing an offer on. Analyzes MLS
  comparable properties to determine market value and assess whether an offer
  price is below, at, or above market.
---

## Purpose

Produce a professional comparable property analysis using an attached MLS PDF as the primary data source. Output includes a value conclusion, detailed breakdown of each comparable, and a clean summary table — suitable for sharing with clients or informing offer strategy.

## Step 0 — Load Agent Profile

Before doing anything else, read `~/.claude/re-assistant.local.md` using the Read tool.

- If the file does not exist or `agent_name` is not set in the YAML frontmatter, stop and tell the user:

  > "This plugin requires setup before use. Please run `/re-assistant:setup` to save your agent profile, then try again."

- If the file exists and `agent_name` is set, extract these values from the YAML frontmatter and use them throughout this skill:
  - `agent_name`
  - `team_name` (may be empty)
  - `brokerage_name`
  - `agent_email`
  - `zenlist_username` (may be empty — if empty, omit all Zenlist links from output)

## Step 1 — Collect Subject Property Details

Ask the user for the following. Accept whatever is available:

- Property address
- Offer price (if known)
- Beds
- Baths
- Sq Ft
- Lot size (if known)
- Parking: number of spaces and type
- Year built

## Step 2 — Collect the MLS PDF

Ask the user to attach the MLS comparables PDF. This is the authoritative data source for all numerical data (prices, sq ft, beds, baths, $/sf, lot size, parking, MLS listing ID, sold date).

Do not proceed with analysis until the PDF is attached.

## Step 3 — Analyze Each Comparable

For each comparable in the MLS PDF, extract:

- Address
- Sold price
- Cost per sq ft ($/SF)
- Sq ft
- Beds / Baths
- Parking type and count
- MLS Listing ID (state "MLS ID Not Provided" if missing)
- Sold date (confirm via Zillow or Redfin if needed)

Use Zillow or Redfin only for:
- 2-sentence property description summaries
- Confirming sold date
- Identifying notable features: yard, parking type, condition, updates, fixer status

Do not use Zillow or Redfin for numerical data — use the MLS PDF only. Do not fabricate or guess details. If data is missing from the PDF, write "Not Provided."

## Step 4 — Produce the Three-Section Output

### Section 1 — Value Conclusion

Write 5–8 sentences of analytical reasoning:

- Analyze price per square foot trends across all comps
- Note mental adjustments for condition, updates, lot, parking, layout, and other qualitative factors
- Identify high and low outliers and explain why they may have traded at those levels
- Estimate a likely value range for the subject property
- State whether the offer price appears: **Below market / At market / Above market**
- Provide a concise professional explanation supporting the conclusion

Be analytical, not promotional. No emojis. No hedging disclaimers.

### Section 2 — Comparable Property Breakdown

For each comparable, use this exact format:

---

**[PROPERTY ADDRESS]**

```
Address | Price | Cost/SqFt | Sq Ft | Bed | Bath | Parking
[example: 123 Main St | $1,250,000 | $865/SF | 1,445 SF | 3 Bed | 2 Bath | 2 Car Garage]
```

**Zenlist Link:**
`https://zenlist.com/listing/mlslistings:[MLSLISTINGID]?as=[ZENLIST_USERNAME]`
*(Omit this line entirely if `zenlist_username` is not set in the agent profile)*

**2-Sentence Public Description Summary (Zillow/Redfin):**
[Concise, neutral 2-sentence summary]

**Sold Date:**
[Date sold]

**Key Property Features:**
- Yard: Yes/No + type
- Parking: detail
- Condition: Updated / Original / Fixer / Fully Renovated
- Kitchen/Bath Condition: brief note
- Notable Upgrades: if any
- Lot Characteristics: Flat / Sloped / Large / Small
- Other Standout Features: views, ADU potential, etc.

**Analyst POV:**
[2–4 sentences: professional opinion comparing this comp to the subject. Note strengths, weaknesses, and whether it likely traded high, low, or at fair market value.]

---

Repeat this block for every comparable in the MLS PDF.

### Section 3 — Summary Table

At the bottom, output a clean markdown table:

| Address | Sold Price | $/SF | Bed | Bath | Sq Ft | Parking | Sold Date |
|---------|------------|------|-----|------|-------|---------|-----------|
|         |            |      |     |      |       |         |           |

This section is optional — include it if there are 3 or more comparables.

## Output Rules

- Use the MLS PDF as the authoritative source for all numerical data
- Do not hallucinate features or prices
- Do not use Zillow/Redfin for numerical data
- If MLS Listing ID is missing, write "MLS ID Not Provided"
- Be concise, analytical, and professional
- No emojis
- No long paragraphs in comp descriptions — keep bullets crisp

## Error Handling

- If the subject property details are missing, ask before proceeding — they are needed for the value conclusion
- If no MLS PDF is attached, ask the user to provide it
- If a comparable is missing key data (price, sq ft), include it anyway and mark the missing fields as "Not Provided" rather than omitting the comp
- If the MLS PDF contains more than 10 comparables, focus on the most recent sales (within 6 months) and flag any older comps as potentially less relevant
