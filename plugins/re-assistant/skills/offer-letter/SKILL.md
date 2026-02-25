---
name: offer-letter
description: >-
  This skill should be used when a user asks to "write an offer letter", "draft
  the offer letter to the listing agent", "compose an offer letter", "write a
  letter presenting our offer", "draft the agent-to-agent offer letter", or says
  "I need to send an offer" and needs the letter written. Drafts a professional,
  concise offer letter from the agent to a listing agent using the saved agent
  profile.
---

## Purpose

Produce a short, executive-quality offer letter written agent-to-agent. The letter is clean, mobile-readable, and positions the offer as strong and easy to close — without hype or marketing language.

## Step 0 — Load Agent Profile

Before doing anything else, read `~/.claude/re-assistant.local.md` using the Read tool.

- If the file does not exist or `agent_name` is not set in the YAML frontmatter, stop and tell the user:

  > "This plugin requires setup before use. Please run `/re-assistant:setup` to save your agent profile, then try again."

- If the file exists and `agent_name` is set, extract these values from the YAML frontmatter — these become the **Sender Context** for the letter:
  - `agent_name` — used as the sender name and in the sign-off
  - `team_name` — included in the sign-off if set (e.g., "Team Name | Brokerage")
  - `brokerage_name` — used in the opening and sign-off
  - `agent_email` — available if the user wants it included

## Step 1 — Collect Offer Inputs

Ask the user for the following. All fields are required. Do not draft the letter until all are provided:

- **Listing agent name** — used in the greeting
- **Client name(s)** — who the agent is representing
- **Property address** — the subject property
- **Offer price** — exact dollar amount
- **Close of escrow timeline** — e.g., "30 days"
- **Target close date** — e.g., "March 15, 2025" (if applicable)
- **Contingencies** — list each contingency and its timeline, or state "No contingencies" if clean; also note any removed (e.g., "Inspection contingency removed")
- **Buyer broker fee (BBF)** — who is responsible and the amount or percentage

If any field is missing, ask specifically for that field before proceeding.

## Step 2 — Draft the Letter

Write the letter following this exact structure:

---

**Greeting**
Hi [LISTING_AGENT_NAME],

**Opening** (2 lines maximum)
- Introduce [AGENT_NAME] and their brokerage (include team name if set)
- Express that [AGENT_NAME] is pleased to present an offer on behalf of the client

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
[AGENT_NAME]
[TEAM_NAME | ][BROKERAGE_NAME]
*(If team_name is set: "Team Name | Brokerage Name". If no team: just "Brokerage Name")*

---

## Step 3 — Send the Letter

Ask the user if they would like to send this offer letter via email or save it:
- Send via email (save the letter to the user's clipboard for easy copy-paste)
- Draft a docx file
- Draft a pdf file

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

- No long paragraphs anywhere in the letter
- No emojis
- No marketing or salesy language
- Maximum one exclamation point total — optional
- Total letter length: very short (fits comfortably on mobile)
- Bullets must be crisp and readable on mobile
- Do not add unnecessary pleasantries or filler sentences

## Error Handling

- If any required input is missing, ask for it specifically before drafting — do not guess or leave placeholders
- If the user provides contradictory contingency information (e.g., "clean offer" but also lists contingencies), ask for clarification before writing
- If the user wants to adjust tone or structure after reviewing the draft, apply the requested changes and re-present the letter
