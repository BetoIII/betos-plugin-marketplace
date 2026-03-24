# US Consumer Onboarding Requirements

---

## KYC Flow
The video must show the full individual consumer onboarding from start to finish:

- [ ] User sign-up / account creation screen(s)
- [ ] Personal information collection (name, DOB, address, SSN or national ID)
- [ ] **Identity document upload** — user photographs a valid government-issued ID
- [ ] **Selfie capture** — user takes a selfie
- [ ] **Liveness check** — active liveness verification (camera prompt, circular overlay, "look straight into the camera", etc.). This is distinct from a static selfie photo.
- [ ] KYC reaches an **approved** or **verified** state — must be shown explicitly on screen. "Under review", "submitted", or "processing" alone are a FAIL.

## Consent Flow

All checkboxes must appear **in this exact order** and require **active user selection** (no pre-checked boxes):

1. [ ] **E-Sign Consent** — standalone checkbox, **first** in the card program section. Cannot be bundled with other items.

2. [ ] **US Card Terms + Issuer Privacy Policy** — single combined checkbox (e.g., "I accept the [Partner] Card Terms and Issuer Privacy Policy"). Privacy Policy must link to **Third National's policy** — not the partner's own.

3. [ ] **Accuracy certification** — must include: *"I certify that the information I have provided is accurate and that I will abide by all the rules and requirements related to my [Partner] Spend Card."*

4. [ ] **Non-solicitation acknowledgment** — must include: *"I acknowledge that applying for the [Partner] Spend Card does not constitute unauthorized solicitation."*

5. [ ] **Partner Privacy Policy** *(if included)* — must be the **last** checkbox. A partner privacy policy appearing in a separate section before the card program checkboxes is a fail.

**Partner name check**: Every checkbox that references a product name (e.g., "[X] Spend Card", "[X] Card Terms") must use the partner's actual product/brand name — not the name of a parent company, technology provider, or infrastructure vendor.

**Pre-checked = FAIL**: Every checkbox must be unchecked by default. The user must actively check each one. Any checkbox already ticked when the screen loads is non-compliant.

## Card Creation
- [ ] Flow ends with a US virtual or physical card explicitly displayed — card face, masked number, and/or "Active" status visible. A generic home screen without a visible card object does not satisfy this.
