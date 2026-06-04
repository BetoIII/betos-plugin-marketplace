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

1. [ ] **E-Sign Consent** — standalone checkbox, first. Uses the linked E-Sign Consent template with "Rain" replaced by the partner's company name. Cannot be bundled with other items.

2. [ ] **[Partner] Card Terms + Issuer Privacy Policy** — *"I accept the [Partner] Card Terms, and the Issuer Privacy Policy."* Per Rain's spec the Issuer Privacy Policy can be linked as-is and **can** be combined with the Card Terms into one checkbox (recommended), or appear as two separate checkboxes — both are acceptable. The Issuer Privacy Policy must be Rain's linked policy (not the partner's own). `[Partner]` must be the partner's actual product brand name. Card Terms are templated and provided by the Rain account representative.
   > **International Consumer does NOT include an "Account Opening Privacy Notice" checkbox.** That item is US-Consumer-specific. If you see one in an International Consumer flow, flag it for clarification with Rain Legal rather than treating it as standard.

3. [ ] **Accuracy certification** — must include: *"I certify that the information I have provided is accurate and that I will abide by all the rules and requirements related to my [Partner] Spend Card."*

4. [ ] **Non-solicitation acknowledgment** — must include: *"I acknowledge that applying for the [Partner] Spend Card does not constitute unauthorized solicitation."*

**Partner brand name check**: Every checkbox referencing a product name must use the partner's actual product/brand name consistently — not the name of a parent company, technology provider, or underlying infrastructure vendor. If the app is branded "Lambi" but checkboxes say "Yunlen Spend Card", that's a fail.

**Pre-checked = FAIL**: Every checkbox must be unchecked by default and require active user selection. Pre-checked boxes do not satisfy affirmative consent requirements.

**Extra checkboxes**: A partner may add additional checkboxes (e.g., the partner's own privacy policy) only if they appear **after** the four required items above and have been pre-approved by Rain Legal. The official Rain International Consumer spec does not require, prohibit, or position any partner-owned privacy policy — flag it as a question for Rain Legal rather than as a pass/fail.

## Card Creation
- [ ] Flow ends with an international virtual or physical card explicitly displayed — a visible card face, masked card number, card network logo, and/or "Active" status. A generic home or dashboard screen without a visible card object does not satisfy this.
