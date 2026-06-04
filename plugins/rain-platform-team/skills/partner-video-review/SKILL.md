---
name: partner-video-review
description: >
  Reviews a partner's sandbox onboarding screen recording against Rain's compliance requirements.
  Use this skill whenever a user uploads or shares a video file and asks to review, check, validate,
  audit, or give feedback on their onboarding demo, sandbox recording, KYC flow, or consent screens.
  Also trigger when a user says things like "does this pass?", "is our flow correct?", "can you review
  our demo video?", "check our onboarding recording before we go live", or submits a video as part of
  their onboarding submission. The skill extracts frames from the video, analyzes each screen in the
  flow, and produces a structured pass/fail compliance report with specific, actionable feedback.
---

# Partner Onboarding Video Review

You are reviewing a partner's screen recording of their sandbox onboarding integration against Rain's compliance requirements. Your job is to watch the flow carefully, check every requirement, and give clear, specific feedback so the partner knows exactly what passes, what fails, and what they need to fix.

## Step 1: Determine the flow type

If the user hasn't already told you, ask which flow type the video covers:
- **Business** (covers both US and International business — same requirements for both)
- **US Consumer**
- **International Consumer**

If the video obviously shows one type (e.g., non-US passport + international card terms = International Consumer; company/UBO registration form = Business), you can infer it and state your assumption clearly.

## Step 2: Extract frames — use a TWO-PASS approach for longer videos

Consent screens are the most critical part of the review and they always appear late in the flow (after KYC completes). A single coarse extraction can skip over them entirely. Always do both passes:

**Pass 1 — Broad survey (understand the full flow structure):**
```bash
mkdir -p /tmp/video-review-frames/pass1
ffmpeg -i "<VIDEO_PATH>" -vf "fps=1/10,scale=600:-1" /tmp/video-review-frames/pass1/frame_%03d.jpg -y
echo "Pass 1 frames: $(ls /tmp/video-review-frames/pass1/ | wc -l)"
```

**Pass 2 — Dense extraction of the final third (catch consent screens):**
First, get the video duration:
```bash
ffprobe -v quiet -show_entries format=duration -of csv=p=0 "<VIDEO_PATH>"
```
Then extract the final third at 1 frame/3 seconds:
```bash
DURATION=<result from above>
START=$(python3 -c "print(int($DURATION * 2/3))")
mkdir -p /tmp/video-review-frames/pass2
ffmpeg -i "<VIDEO_PATH>" -ss $START -vf "fps=1/3,scale=600:-1" /tmp/video-review-frames/pass2/frame_%03d.jpg -y
echo "Pass 2 frames: $(ls /tmp/video-review-frames/pass2/ | wc -l)"
```

For short videos (<2 minutes), a single pass at `fps=1/5` is fine — skip Pass 2.

## Step 3: Read ALL frames from BOTH passes

Read every frame from Pass 1 first (to understand the overall structure), then every frame from Pass 2 (to carefully evaluate the consent screen and card creation). Do not skip frames in Pass 2 — this is where the critical compliance details live.

As you read, build a mental map of:
- What screens appeared and in what order
- The KYC/KYB outcome state (look for "approved", "verified", green checkmark screens)
- The exact text of every consent checkbox — word for word, including the partner/brand name used
- The order of checkboxes and whether any were pre-checked vs. requiring user action
- Whether a card was explicitly shown/issued at the end (a card face/number, not just a dashboard)
- Whether the video spans multiple apps or platforms (common for Business flows)

**For Business flows**: The video may show TWO separate platforms — (1) a consumer/user-facing app where individual representatives go through KYC, and (2) a business admin platform where company/UBO information is submitted. Evaluate BOTH portions. The individual KYC approval AND the company KYB approval must both be shown.

## Step 4: Load the requirements

Read the reference file for the flow type — **always treat the reference file as the source of truth for that program** rather than relying on memory:
- Business: `references/business-requirements.md`
- US Consumer: `references/us-consumer-requirements.md`
- International Consumer: `references/international-consumer-requirements.md`

**Do not generalize the consent-screen structure from one program type to another.** The required checkboxes and their order differ across programs — most notably, US Consumer includes an "Account Opening Privacy Notice" checkbox at position #2 that International Consumer and Business do not. Open the right reference file first and compare the video against that — never against a remembered template.

## Step 5: Produce the compliance report

Use the format below. Be specific — quote exact text seen in the video, reference frame numbers or pass numbers, and explain precisely what was seen vs. what is required.

---

## Report format

```
# Onboarding Video Compliance Review
**Partner:** [App/brand name visible in video]
**Flow Type:** [Business / US Consumer / International Consumer]
**Reviewed:** [today's date]
**Overall Status:** ✅ PASS / ❌ FAIL / ⚠️ PASS WITH NOTES

---

## Summary
[2–3 sentences describing what the video showed and the main issues found.]

---

## Checklist

### KYC/KYB Flow
| Requirement | Status | Notes |
|---|---|---|
| [requirement] | ✅ Pass / ❌ Fail / ⚠️ Partial | [specific observation, frame reference] |

### Consent Flow
| Requirement | Status | Notes |
|---|---|---|
| [requirement] | ✅ Pass / ❌ Fail / ⚠️ Partial | [specific observation, quote exact checkbox text] |

### Card Creation
| Requirement | Status | Notes |
|---|---|---|
| [requirement] | ✅ Pass / ❌ Fail / ⚠️ Partial | [specific observation] |

---

## Issues to Fix
[Numbered list of every failure. For each: what was observed → what is required → what to change.]

---

## What Looked Good
[Brief callout of things done correctly, especially commonly missed items.]
```

---

## Key things to check carefully

### KYC/KYB approval state
The most common fail. You must see an explicit "approved", "verified", or "verification complete" screen — not just "submitted", "under review", or "pending". For Business flows, look for this at TWO levels:
- **Individual KYC**: Each representative/UBO must reach an approved state
- **Company KYB**: The business entity itself must also reach an approved state (not just "details submitted" or "verification required for UBOs")

### Consent checkpoint — if you can't find consent screens, look harder
Consent screens appear late in the flow, after KYC completes. If Pass 1 doesn't show them, Pass 2 (dense extraction of the final third) should catch them. If you still don't see a consent/T&C screen after both passes, only then report it as missing — and be explicit that you couldn't find it despite thorough extraction.

### Consent checkbox affirmative action
All checkboxes must require the user to actively click them — **pre-checked checkboxes are a hard fail**. If a checkbox already has a checkmark when the screen first loads, that's non-compliant regardless of the text. Similarly, if a required checkbox is visibly unchecked when the user taps "Continue" or "Done", that's a fail.

### Consent checkbox list depends on program type — do not assume one structure fits all
The exact set and order of consent checkboxes differs across the three programs. Look these up in the reference file every time — never apply a memorized template across program types.

- **US Consumer (5 items)**: E-Sign → **Account Opening Privacy Notice** → [Partner] Card Terms + Issuer Privacy Policy → Accuracy → Non-solicitation
- **International Consumer (4 items)**: E-Sign → [Partner] Card Terms + Issuer Privacy Policy → Accuracy → Non-solicitation
- **Business — Business Agreements page (4 items)**: E-Sign → [Partner] Card Terms + Issuer Privacy Policy → Accuracy → Non-solicitation
- **Business — Authorized User Agreements page (1 item)**: Authorized User Agreement

Common false-positive to avoid: in a **US Consumer** flow, the second checkbox is **"I accept the Account Opening Privacy Notice"** — that is the correct structure, not an "extra" checkbox or a misplacement. Do not report the Card Terms + Issuer Privacy Policy checkbox as "missing from position #2" in a US Consumer flow; it is expected at position #3.

The Card Terms + Issuer Privacy Policy can appear as a single combined checkbox (recommended) **or** as two separate checkboxes — Rain's spec explicitly allows both. Do not fail a flow just because they are split into two boxes.

### E-Sign placement
The E-Sign consent must be a completely standalone checkbox — not merged with any other item — and it must be the very first checkbox in the user/business agreements section.

### Checkbox text and partner name consistency
Read every consent checkbox carefully. The text must use the partner's actual product brand name throughout. If the app is called "Lambi" but checkboxes say "Yunlen Spend Card", that's a fail — the right brand name must be used consistently across all four checkboxes.

### What counts as card creation
The flow should end with a card object explicitly displayed — card face, card number (even masked), card type, network logo, and/or "Active" status. A generic home dashboard without a visible card does not satisfy this.

### Partner-owned extra checkboxes
Rain's official requirements do not specify, require, or prohibit a partner's own privacy-policy checkbox — it is not part of any of the three published consent flows. If a partner includes one, the safe rule is that it must appear **after** all Rain-required checkboxes and must have been pre-approved by Rain Legal. Flag any partner-owned checkbox that appears before the Rain-required items as a question for Rain Legal rather than as an automatic fail.
