# Business Onboarding Requirements
> Source: Rain — *Business Onboarding Requirements* (2026 release). Applies to both US Business and International Business flows.
> Business submissions often span two separate apps: a consumer-facing app (where individuals go through KYC) and a business admin platform (where company/UBO info is submitted). Both portions must be evaluated. Always re-confirm against the version of the PDF shared by Rain Legal for the specific program.

---

## KYB Flow — Company Level
The video must show the full business entity registration:

- [ ] Business/company information collected (company name, registration number, address, business type, website, etc.)
- [ ] Beneficial Owner (UBO) and/or Director information collected (name, DOB, ownership %, address, TIN)
- [ ] **Company/KYB reaches an approved or verified state** — showing "Company details submitted" or "Verification required for UBOs" alone is a **FAIL**. The company entity itself must reach a confirmed approved/verified status on screen.

## KYC Flow — Individual Representatives
Each UBO, director, or authorized representative must go through individual identity verification:

- [ ] Identity document upload (passport, national ID, etc.)
- [ ] Selfie capture
- [ ] Liveness check (camera-facing prompt — distinct from a static photo)
- [ ] KYC reaches **approved** or **verified** state for each representative — "under review" or "pending" is a FAIL

## Required Video Content
Business submissions must demonstrate **both** consent pages — typically captured as one combined video or two separate videos:

- [ ] **Business Agreements page** — accepted by the company account owner/admin
- [ ] **Authorized User Agreements page** — accepted by an individual card user (authorized user)

## Consent Flow — Business Agreements Page

The Business Agreements page must contain **these four checkboxes, in this exact order**, each requiring **active user selection** (no pre-checked boxes):

1. [ ] **E-Sign Consent** — standalone checkbox, first. Uses the linked E-Sign Consent template with "Rain" replaced by the partner's company name. Cannot be bundled with other items.

2. [ ] **[Partner] Card Terms + Issuer Privacy Policy** — *"I accept the [Partner] Card Terms, and the Issuer Privacy Policy."* Per Rain's spec the Issuer Privacy Policy can be linked as-is and **can** be combined with the Card Terms into one checkbox (recommended), or appear as two separate checkboxes — both are acceptable. The Issuer Privacy Policy must be Rain's linked policy (not the partner's own). `[Partner]` must be the partner's actual product brand name. Card Terms are templated and provided by the Rain account representative.
   > **Business flows do NOT include an "Account Opening Privacy Notice" checkbox.** That item is US-Consumer-specific.

3. [ ] **Accuracy certification** — must include: *"I certify that the information I have provided is accurate and that I will abide by all the rules and requirements related to my [Partner] Spend Card."*

4. [ ] **Non-solicitation acknowledgment** — must include: *"I acknowledge that applying for the [Partner] Spend Card does not constitute unauthorized solicitation."*

## Consent Flow — Authorized User Agreements Page

The Authorized User Agreements page must contain **this single checkbox**, requiring active user selection:

1. [ ] **Authorized User Agreement** — *"I accept the Authorized User Agreement."* The Authorized User Agreement text is provided by the Rain account representative.

---

**Pre-checked = FAIL**: All checkboxes on both pages must be unchecked by default and require affirmative user selection. Pre-checked boxes are a hard fail regardless of text.

**Partner brand name check**: Every checkbox referencing a product name must use the partner's actual product/brand name consistently — not a parent company, technology provider, or underlying infrastructure vendor.

**Extra checkboxes**: A partner may add additional checkboxes (e.g., the partner's own privacy policy) only if they appear **after** the required items on either page and have been pre-approved by Rain Legal. The official Rain Business spec does not require, prohibit, or position any partner-owned privacy policy — flag it as a question for Rain Legal rather than as a pass/fail.

## Card Creation
- [ ] The flow ends with a card being explicitly shown — a visible card face, masked card number, and/or "Active" status. A generic home dashboard alone is not sufficient.
