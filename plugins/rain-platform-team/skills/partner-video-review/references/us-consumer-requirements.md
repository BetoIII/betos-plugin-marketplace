# US Consumer Onboarding Requirements

> Source: Rain — *US Consumer User Onboarding Requirements* (2026 release). Always re-confirm against the version of the PDF shared by Rain Legal for the specific program under review — the list and order of consent checkboxes can change per program.

---

## KYC Flow
The video must show the full individual consumer onboarding from start to finish:

- [ ] User sign-up / account creation screen(s)
- [ ] Personal information collection (name, DOB, address, SSN or national ID)
- [ ] **Identity document upload** — user photographs a valid government-issued ID
- [ ] **Selfie capture** — user takes a selfie
- [ ] **Liveness check** — active liveness verification (camera prompt, circular overlay, "look straight into the camera", etc.). This is distinct from a static selfie photo.
- [ ] KYC reaches an **approved** or **verified** state — must be shown explicitly on screen. "Under review", "submitted", or "processing" alone are a FAIL.

## Consent Flow — User Agreements Page

The User Agreements page must contain **these five checkboxes, in this exact order**, each requiring **active user selection** (no pre-checked boxes):

1. [ ] **E-Sign Consent** — standalone checkbox, first. Uses the linked E-Sign Consent template with "Rain" replaced by the partner's company name. Cannot be bundled with other items.

2. [ ] **Account Opening Privacy Notice** — standalone checkbox. Text: *"I accept the Account Opening Privacy Notice."* The Account Opening Privacy Notice text is provided to the partner by Rain's account representative.
   > **This item is required for US Consumer flows specifically — it does not appear in International Consumer or Business flows.** A US Consumer flow that goes E-Sign → Card Terms directly (skipping the Account Opening Privacy Notice) is non-compliant. Conversely, seeing the Account Opening Privacy Notice in this position is correct, **not** an "extra" checkbox.

3. [ ] **[Partner] Card Terms + Issuer Privacy Policy** — *"I accept the [Partner] Card Terms, and the Issuer Privacy Policy."* Per Rain's spec the Issuer Privacy Policy can be linked as-is and **can** be combined with the Card Terms into one checkbox (recommended), or appear as two separate checkboxes — both are acceptable. The Issuer Privacy Policy must be Rain's linked policy (not the partner's own). `[Partner]` must be the partner's actual product brand name. Card Terms are templated and provided by the Rain account representative.

4. [ ] **Accuracy certification** — must include: *"I certify that the information I have provided is accurate and that I will abide by all the rules and requirements related to my [Partner] Spend Card."*

5. [ ] **Non-solicitation acknowledgment** — must include: *"I acknowledge that applying for the [Partner] Spend Card does not constitute unauthorized solicitation."* (US spelling — "unauthorized" not "unauthorised".)

**Partner brand name check**: Every checkbox referencing a product name (e.g., "[X] Spend Card", "[X] Card Terms") must use the partner's actual product/brand name — not the name of a parent company, technology provider, or infrastructure vendor.

**Pre-checked = FAIL**: Every checkbox must be unchecked by default. The user must actively check each one. Any checkbox already ticked when the screen loads is non-compliant.

**Extra checkboxes**: A partner may add additional checkboxes (e.g., the partner's own privacy policy) only if they appear **after** the five required items above and have been pre-approved by Rain Legal. The official Rain US Consumer spec does not require, prohibit, or position any partner-owned privacy policy — flag it as a question for Rain Legal rather than as a pass/fail.

## Card Creation
- [ ] Flow ends with a US virtual or physical card explicitly displayed — card face, masked number, and/or "Active" status visible. A generic home screen without a visible card object does not satisfy this.
