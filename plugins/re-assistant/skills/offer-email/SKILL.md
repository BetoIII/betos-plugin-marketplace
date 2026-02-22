---
name: offer-email
description: >-
  This skill should be used when a user asks to "write an offer email", "draft
  the offer letter to the listing agent", "compose an offer email", "write an
  email presenting our offer", "draft the agent-to-agent offer email", or says
  "I need to send an offer" and needs the email written. Drafts a professional,
  concise offer email from David Raygorodsky (The Nolan Group, Vanguard
  Properties) to a listing agent.
---

## Purpose

Produce a short, executive-quality offer email written agent-to-agent. The email is clean, mobile-readable, and positions the offer as strong and easy to close — without hype or marketing language.

## Sender Context (always fixed)

- **Sender:** David Raygorodsky
- **Team:** The Nolan Group
- **Brokerage:** Vanguard Properties
- **Partner:** Frank Nolan (President of Vanguard Properties)
- **Positioning:** Experienced, reliable, easy to work with, strong execution track record

## Step 1 — Collect Offer Inputs

Ask the user for the following. All fields are required. Do not draft the email until all are provided:

- **Listing agent name** — used in the greeting
- **Client name(s)** — who the agent is representing
- **Property address** — the subject property
- **Offer price** — exact dollar amount
- **Close of escrow timeline** — e.g., "30 days"
- **Target close date** — e.g., "March 15, 2025" (if applicable)
- **Contingencies** — list each contingency and its timeline, or state "No contingencies" if clean; also note any removed (e.g., "Inspection contingency removed")
- **Buyer broker fee (BBF)** — who is responsible and the amount or percentage

If any field is missing, ask specifically for that field before proceeding.

## Step 2 — Draft the Email

Write the email following this exact structure:

---

**Greeting**
Hi [LISTING_AGENT_NAME],

**Opening** (2 lines maximum)
- Introduce David and The Nolan Group / Vanguard Properties
- Mention Frank Nolan by name
- Express that David is pleased to present an offer on behalf of the client

**Offer Summary** (tight bulleted list)
- Property: [PROPERTY_ADDRESS]
- Price: [OFFER_PRICE]
- Close: [CLOSING_TIMELINE] (target close: [CLOSE_DATE], if provided)
- Contingencies:
  - [Each contingency with its timeline, or "None — fully non-contingent"]
- Buyer broker fee:
  - [BBF_DETAILS]

**Positioning** (1–2 lines maximum)
- State this is a strong, clean offer
- Emphasize ability to execute a smooth and reliable transaction
- Convey genuine interest in working together

**Close** (1 line)
- Express appreciation for their time and consideration

**Sign-off**
Best,
David Raygorodsky
The Nolan Group | Vanguard Properties

---

## Tone and Style Rules

- Extremely concise and skimmable
- Professional, executive, and calm
- Confident but humble — never arrogant
- Collaborative and respectful
- No hype, no fluff, no marketing language
- Written agent-to-agent, not to a client
- Firm and clear

## Hard Rules

- No long paragraphs anywhere in the email
- No emojis
- No marketing or salesy language
- Maximum one exclamation point total — optional
- Total email length: very short (fits comfortably on mobile)
- Bullets must be crisp and readable on mobile
- Do not add unnecessary pleasantries or filler sentences

## Error Handling

- If any required input is missing, ask for it specifically before drafting — do not guess or leave placeholders
- If the user provides contradictory contingency information (e.g., "clean offer" but also lists contingencies), ask for clarification before writing
- If the user wants to adjust tone or structure after reviewing the draft, apply the requested changes and re-present the email
