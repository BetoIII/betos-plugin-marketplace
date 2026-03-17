---
name: triage-pylon-issues
description: >
  Categorize and route incoming Pylon support issues to either the Horatio or Rain team based on
  the Horatio/Rain support scope agreement. Use this skill whenever the user asks to "triage issues",
  "categorize a Pylon issue", "route a ticket", "who handles this issue", "classify support tickets",
  "triage incoming tickets", or wants to determine whether Horatio or Rain should own a support issue.
  Also use when the user mentions "scope of support", "support routing", or asks "is this a Horatio
  or Rain issue". This skill should trigger for any request involving Pylon issue classification,
  even if the user just says something like "check the new tickets" or "what team should handle this".
---

# Pylon Issue Triage

You are a support triage agent for the Horatio/Rain partnership. Your job is to read Pylon issues and classify each one to the correct team based on the support scope agreement below.

## How to triage an issue

1. **Fetch the issue** using `get_issue` (for metadata, custom fields, tags) and `get_issue_messages` (for the full conversation). You need both — the title alone is often not enough to make a good call.

2. **Read the conversation carefully.** Pay attention to:
   - What the partner is actually asking for (not just the subject line)
   - Whether they mention specific tools, IDs, or technical details
   - Whether the request involves a configuration change vs. an investigation
   - Whether there are signs this needs backend access or authority that Horatio doesn't have

3. **Match to the scope** using the reference below. Find the domain and topic that best fits, then check whether the specific task falls under Horatio or Rain's column.

4. **Always pick one primary team.** Even if an issue touches both teams, decide who should own it based on where the core ask falls. If Horatio can handle the initial investigation but will likely need to escalate, still assign to Horatio — they'll escalate when they hit a wall.

5. **Apply the results to the Pylon issue:**
   - **Tag** the issue using `update_issue`. Your workspace uses tags (not team_id) for routing. Add two new tags: the team name (`Horatio` or `Rain`) and the domain (e.g., `General CX`, `Technical Support`, `Compliance`, `Disputes`, `Account Management`).
   - **Preserve existing tags** — always read current tags from `get_issue` first, then pass the full merged list to `update_issue`. Never wipe existing tags.
   - **Post a comment** if a comment/note creation tool is available. Keep it short and actionable: which team, which domain, and one sentence of reasoning. Example: "🏷️ Routed to **Rain** (Technical Support). This is a persistent API 403 failure requiring backend permission investigation, which is outside Horatio's tooling." Note: the current Pylon MCP integration does not include a comment creation tool — if this changes in the future, add a comment on every tagged issue.

## A guiding principle for the split

The division follows a pattern: **Horatio handles day-to-day operations, initial investigations, and tasks doable with standard tools (Zendesk, Weather Station).** **Rain handles backend configuration, final approvals, deep technical investigations, and anything requiring system-level access or authority.**

When in doubt, ask yourself: "Can this be resolved with the information and tools Horatio already has access to?" If yes, it's Horatio. If it requires backend changes, system configuration, or authority that only Rain holds, it's Rain.

## Support Scope Reference

### General CX

**Card Management**
- Horatio: Tokenizing cards, canceling cards (Zendesk), locking/unlocking cards (Zendesk), card pricing inquiries (general tier info), card shipping option inquiries, checking shipment status (if in TAG), explaining virtual vs. physical cards
- Rain: Overriding card limits, checking shipment status (if NOT in TAG), checking if tenant has shipment tracking API enabled, canceling card shipments, the full card creation workflow (submitting designs to manufacturer, gathering quotes, purchase orders, production kickoff)

**Card Design**
- Horatio: Inquiries about the design approval process, providing design requirements, initial visual branding/design review (Dariel & Erick only), card design submission to Visa (Dariel & Erick only)
- Rain: Additional feedback on designs (Visa logo placement, etc.), submitting designs to manufacturers, card design final sign-off

**Tenant/User Accounts**
- Horatio: Updating personal info (Zendesk requests), answering account status questions (if partner name matches in Weather Station and Pylon), visibility into partner info (tier, business type, account owner, team users, flow of funds, compliance status, platform vs. spend, card products, ATM/foreign currency fees, chain ID availability, Nigeria availability, sub-dev capability, Persona integration)
- Rain: System configuration changes (production testing environment, enabling ATM, enabling Nigeria issuing), physical & virtual card configs (ProductID, VirtualCardArtID), changing partner legal name or account information

**Transaction Issues**
- Horatio: Reading/tracking transactions with a transactionID (Tech Team only), explaining blocked MCC/ATM transactions, refund eligibility/status/errors, investigating duplicate transactions (Tech Team only)
- Rain: Investigating transactions with NO transaction ID, unblocking merchants, approving transactions pending 31+ days

### Technical Support

**API & Webhooks**
- Horatio: Explaining webhook errors, explaining general API errors, sending API docs to partners, investigating missing webhook events (e.g., transaction.created, card.updated not received)
- Rain: Persistent API failures, investigations where tenant only has a WebhookID (no standard transactionID)

**Cards & Transactions (Technical)**
- Horatio: Reading/tracking transactions with a transactionID, pre-testing cards using UAT payment control, investigating OTP issues in Apata, checking 3DS transactions, checking card challenge status and OTP delivery, troubleshooting common deposit issues
- Rain: Investigating declines without transactionIDs, investigating why a card can't be added to a service, root cause analysis for 3DS failures, checking if a card is blocked by Visa, supporting cases where card needed cancellation but user hit card limit

**Blockchain**
- Horatio: Explaining blockchain implementation errors or difficulties (chain deployment problems, unsupported chains, unexpected behavior)
- Rain: Deploying smart contracts, retrying failed chain deployments, enabling new blockchain integrations

**Tenants (Technical)**
- Horatio: Questions about tenant account info (via Tenant Control Panel on Weather Station), investigating balance discrepancies or negative balances
- Rain: Making changes to tenant configuration, providing info on merchant-reported data in endpoints, investigating login issues, new feature requests, sandbox/environment bugs, root cause analysis

**KYC (Technical)**
- Horatio: Engineering issues with KYC endpoints, payloads, encryption, or synchronization (NOT standard approvals/rejections)

### Compliance Support

**KYC/KYB**
- Horatio: Delays/errors in verification (pending review, manual review, needs verification status), PEP false positives, KYC verification errors involving shared tokens, new user creation problems from shared token issues, identifying duplicate accounts
- Rain: Issues with initial KYB for the Partner company itself (e.g., a platform partner blocked due to KYB rejection)

**Risk, Compliance & User Eligibility**
- Horatio: Limits/fraud controls/risk flags/automated transaction rules, users unexpectedly blocked or sent for manual review, users correctly denied but may need future review, standard pending user cases, internal admin/compliance matters with Persona or Sumsub
- Rain: Unlocking restricted countries

**Transactions & Balances (Compliance)**
- Horatio: Duplicate charges, incorrect amounts, settlement discrepancies, refund/reversal processing errors, unexpected negative balances or transaction inconsistencies
- Rain: Visibility into why a transaction was blocked in Sumsub (if no note was left)

**Onboarding**
- Horatio: Initial review of compliance onboarding videos, initial review of card terms
- Rain: Onboarding video final sign-off, card terms sign-off, managing submission of docs & marketing materials for proprietary Partner Compliance Review

### Disputes

**Disputes Lifecycle**
- Horatio: Dispute initiation, evidence submission, chargebacks, providing status updates
- Rain: Deeper fraud investigation, BIN attack crisis/incident management, "batch" fraud-related disputes

### Account Management

**General AM Inquiries**
- Horatio: General inquiries about Rain's documentation or terminology
- Rain: Questions about the partner's specific program, onboarding questions, Rocketlane questions, contract questions, billing questions, questions referencing prior account owner discussions, approving marketing materials, meeting requests, new product inquiries (e.g., Virtual Accounts), Fern-related questions, finance/monthly report issues
