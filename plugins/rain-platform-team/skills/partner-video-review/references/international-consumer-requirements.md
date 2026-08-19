# International Consumer Onboarding Requirements

> Source: Rain — *International Consumer User Onboarding Requirements* (Nov 2025 / 2026 release). Always re-confirm against the version of the PDF shared by Rain Legal for the specific program under review — the list and order of consent checkboxes can change per program.

---

## KYC Flow
The video must show the full individual consumer onboarding from start to finish:

- [ ] User sign-up / account creation screen(s)
- [ ] Personal information collection (name, DOB, address, national ID number)
- [ ] **Identity document upload** — user photographs a valid government-issued ID (national ID, passport, residence permit, or driver's license from any supported country)
- [ ] **Selfie capture** — user takes a selfie
- [ ] **Liveness check** — active liveness verification (camera-facing prompt with circular overlay, head movement, or "look straight into the camera" instruction). Distinct from a static selfie.
- [ ] KYC reaches an **approved** or **verified** state — must be shown explicitly on screen (e.g., "Your profile has been verified", "You are approved", green checkmark with confirmation). Screens showing only "under review", "submitted", or "processing" are a FAIL.

## Consent Flow — User Agreements Page

The User Agreements page must contain **these four checkboxes, in this exact order**, each requiring **active user selection** (no pre-checked boxes):

1. [ ] **E-Sign Consent / E-Sign Disclosure** — standalone checkbox, first (canonical text: *"I consent to the E-Sign Disclosure."*). Must link **directly to Rain's hosted notice** at `legal.raincards.xyz/legal/electronic-communications-notice` (document title: "E-Sign & Electronic Communications Notice"). Partners were previously asked to fork this template and rebrand "Rain" as their own name — as of Aug 2026 Rain Legal requires linking to the Rain-hosted document as-is, with no forked/rebranded copies. Cannot be bundled with other items.

2. [ ] **[Partner] Card Terms + Issuer Privacy Policy** — *"I accept the [Partner] Card Terms, and the Issuer Privacy Policy."* Per Rain's spec the Issuer Privacy Policy can be linked as-is and **can** be combined with the Card Terms into one checkbox (recommended), or appear as two separate checkboxes — both are acceptable. The Card Terms link goes to a **partner-hosted** page on the partner's own domain (e.g., `dionapp.com/card-terms-int`) — the document itself is Rain's template redlined by the partner and approved by Rain Legal. The Issuer Privacy Policy link must go **directly to Rain's hosted policy** at `legal.raincards.xyz/legal/privacy-policy` (document title: "Rain Privacy Policy") — not the partner's own policy, and not a partner URL that redirects there (redirects like `third-national.com/privacypolicy` should be flagged; ask the partner to link directly). `[Partner]` must be the partner's actual product brand name.
   > **International Consumer does NOT include an "Account Opening Privacy Notice" checkbox.** That item is US-Consumer-specific. If you see one in an International Consumer flow, flag it for clarification with Rain Legal rather than treating it as standard.

3. [ ] **Accuracy certification** — must include: *"I certify that the information I have provided is accurate and that I will abide by all the rules and requirements related to my [Partner] Spend Card."*

4. [ ] **Non-solicitation acknowledgment** — must include: *"I acknowledge that applying for the [Partner] Spend Card does not constitute unauthorized solicitation."*

**Partner brand name check**: Every checkbox referencing a product name must use the partner's actual product/brand name consistently — not the name of a parent company, technology provider, or underlying infrastructure vendor. If the app is branded "Lambi" but checkboxes say "Yunlen Spend Card", that's a fail.

**Pre-checked = FAIL**: Every checkbox must be unchecked by default and require active user selection. Pre-checked boxes do not satisfy affirmative consent requirements.

**Extra checkboxes**: A partner may add additional checkboxes (e.g., the partner's own privacy policy) only if they appear **after** the four required items above and have been pre-approved by Rain Legal. The official Rain International Consumer spec does not require, prohibit, or position any partner-owned privacy policy — flag it as a question for Rain Legal rather than as a pass/fail.

## Consent Link Destinations & Click-Through Demonstration (required as of Aug 2026)

The video must show every hyperlinked agreement being **opened, scrolled through, and returned from** before its checkbox is checked — checking the boxes without opening the links is a FAIL (Rain Legal will bounce the submission).

| # | Link | Host | Required destination (verify domain in the visible address bar) |
|---|---|---|---|
| 1 | E-Sign Disclosure | Rain | `legal.raincards.xyz/legal/electronic-communications-notice` — "E-Sign & Electronic Communications Notice" |
| 2a | [Partner] Card Terms | Partner | Partner domain (e.g., `dionapp.com/card-terms-int`) |
| 2b | Issuer Privacy Policy | Rain | `legal.raincards.xyz/legal/privacy-policy` — "Rain Privacy Policy" |

**Nested links inside the partner-hosted Card Terms** (the video must show at least the Prohibited Activities click-through; the canonical video shows both):
- [ ] **Prohibited Activities** → `legal.raincards.xyz/legal/prohibitions` ("Rain Prohibitions List") — tapped from within the Card Terms and scrolled.
- [ ] **E-Sign & Electronic Communications Notice** → `legal.raincards.xyz/legal/electronic-communications-notice` — the Card Terms must reference and link the Rain-hosted notice.

Checkboxes 3 (Accuracy) and 4 (Non-solicitation) have **no links** — no click-through applies.

Notes for the reviewer:
- Phone browsers usually show only the domain in the URL pill (`legal.raincards.xyz` vs the partner's domain) — that is sufficient evidence; full paths are rarely visible.
- The canonical pattern (Dion `Int_conditions_agreement.mov`, Aug 19 2026): E-Sign notice opened and scrolled end-to-end → return → check #1; Card Terms on the partner domain scrolled to the very end, with the nested Prohibitions link clicked (resolving to `legal.raincards.xyz`) and the nested E-Sign link clicked → Issuer Privacy Policy opened at `legal.raincards.xyz` and scrolled fully → check #2; then #3 and #4; "Confirm & issue card" enables only once all 4 are checked.
- Partial scrolling of a long document is acceptable as ⚠️ Partial with a note, but never opening a link at all is a ❌ Fail for that link.

## Card Creation
- [ ] Flow ends with an international virtual or physical card explicitly displayed — a visible card face, masked card number, card network logo, and/or "Active" status. A generic home or dashboard screen without a visible card object does not satisfy this.
