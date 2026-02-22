---
name: disclosure-package-summary
description: >-
  This skill should be used when a user asks to "analyze disclosure documents",
  "summarize the disclosure package", "review the disclosures", "create a
  disclosure summary", "analyze the inspection reports", "run a disclosure
  review", or when the user uploads disclosure PDFs for a property. Produces a
  structured, client-ready Disclosure Package Summary covering title,
  inspections, permits, seller disclosures, and a repair cost summary. Designed
  for San Francisco residential real estate transactions.
---

## Purpose

Produce a structured, bullet-only Disclosure Package Summary from uploaded disclosure PDFs. Output is ready to paste into Google Docs and follows the 13-section format defined in `references/output-template.md`.

## Step 1 — Collect Deal Inputs

Ask the user for the following. Accept whatever is available; infer the rest where possible:

- Client name(s)
- Property address
- List price
- MLS square footage
- Beds / Baths (from MLS)
- Property type: Condo / SFH / TIC / Duplex / Multi / Other
- Target offer price (optional)
- Target offer $/sf (optional)

Assume San Francisco, CA unless the user states otherwise.

## Step 2 — Collect Disclosure Documents

Ask the user to attach or upload all disclosure package PDFs. Accept whatever is provided. Common documents include:

- Preliminary Title Report
- Home Inspection report
- Pest / Termite report
- Roof, Sewer, Electrical, Structural, HVAC (specialty reports)
- Transfer Disclosure Statement (TDS)
- AVID (Agent Visual Inspection Disclosure)
- San Francisco Seller Disclosure
- CC&Rs and HOA docs (if condo/TIC)
- Estoppels / Rent rolls / Leases (if tenant-occupied or multi-unit)
- 3R Report (permits)
- NHD Report

If only non-inspection documents are provided (e.g., title report only), proceed with the available sections and note which inspection sections could not be completed.

## Step 3 — Perform Required Calculations

Calculate the following before writing:

- Asking $/sf = List Price ÷ MLS Sq Ft (if both provided)
- If target offer price given: Offer $/sf = Offer Price ÷ MLS Sq Ft
- If target $/sf given: Offer amount = Target $/sf × MLS Sq Ft
- Estimated property taxes at list price: ~1.18% of purchase price per year — output annual and monthly
- If offer price provided: also compute taxes at offer price

Repeat all numbers exactly as written in source documents, with units (sf, $, %, amps, etc.).

## Step 4 — Search for Property Details

Search Realtor.com, Zillow, or Redfin for the property address to find confirmed bedroom, bathroom, and price data for the executive summary. If web search is unavailable, skip this step and rely on MLS data provided by the user in Step 1.

## Step 5 — Analyze Documents by Priority

Process uploaded documents in this order. Skip any type not present — do not note its absence:

1. Preliminary Title Report
2. Home Inspection
3. Pest / Termite report
4. Specialty reports: Roof, Sewer, Plumbing, Electrical, Structural, Foundation, HVAC
5. Transfer Disclosure Statement (TDS)
6. AVID
7. San Francisco Seller Disclosure
8. CC&Rs + HOA docs (if condo/TIC)
9. Estoppels / Rent rolls / Leases (if multi-unit or tenant-occupied)
10. 3R Report
11. NHD Report
12. Any other repair or defect documents

When a report uses strong or precise language, include short exact quotes (3–20 words) in quotation marks — prioritize high-signal language, do not overquote. Write "Not found in uploaded docs" when information is missing. Do not guess.

## Step 6 — Produce the Summary

Write the output using the 13-section structure defined in `references/output-template.md`. Verify all calculations before output.

**Output rules:**
- Bullets only throughout (except Section 13, which allows 2–4 short sentences)
- No URLs, no "see page X," no links
- No guessing — write "Not found in uploaded docs" when info is absent
- Target 1,000–2,000 words; prioritize completeness for inspection sections (Section 9) over hitting the word count

## Error Handling

- If deal inputs are missing, ask before proceeding — calculations require them
- If no PDFs are attached, ask the user to upload the disclosure documents
- If a required calculation cannot be performed (missing sq ft or price), skip that calculation and note "Not provided"
- If a document is illegible or corrupted, note "Unable to read [doc name]" and continue with available documents
