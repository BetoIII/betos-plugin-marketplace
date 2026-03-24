# International Consumer Onboarding Requirements

---

## KYC Flow
The video must show the full individual consumer onboarding from start to finish:

- [ ] User sign-up / account creation screen(s)
- [ ] Personal information collection (name, DOB, address, national ID number)
- [ ] **Identity document upload** — user photographs a valid government-issued ID (national ID, passport, residence permit, or driver's license from any supported country)
- [ ] **Selfie capture** — user takes a selfie
- [ ] **Liveness check** — active liveness verification (camera-facing prompt with circular overlay, head movement, or "look straight into the camera" instruction). Distinct from a static selfie.
- [ ] KYC reaches an **approved** or **verified** state — must be shown explicitly on screen (e.g., "Your profile has been verified", "You are approved", green checkmark with confirmation). Screens showing only "under review", "submitted", or "processing" are a FAIL.

## Consent Flow

All checkboxes must appear **in this exact order** and require **active user selection** (no pre-checked boxes):

1. [ ] **E-Sign Consent** — standalone checkbox, **first** in the card program/agreement section. Must not be merged with other items. Must be unchecked by default.

2. [ ] **International Card Terms + Issuer Privacy Policy** — single combined checkbox (e.g., "I accept the [Partner] Card Terms and Issuer Privacy Policy"). The Privacy Policy must link to **Third National's policy** (https://www.third-national.com/privacypolicy) — not the partner's own policy.

3. [ ] **Accuracy certification** — must include: *"I certify that the information I have provided is accurate and that I will abide by all the rules and requirements related to my [Partner] Spend Card."*

4. [ ] **Non-solicitation acknowledgment** — must include: *"I acknowledge that applying for the [Partner] Spend Card does not constitute unauthorized solicitation."*

5. [ ] **Partner Privacy Policy** *(if included)* — must be the **last** checkbox, after all Rain/issuer-required items. A partner privacy policy appearing before the card program checkboxes (e.g., in a top-level "Core Agreements" section) is a fail.

**Partner name check**: Every checkbox referencing a product name must use the partner's actual product/brand name consistently — not the name of a parent company, technology provider, or underlying infrastructure vendor. If the app is branded "Lambi" but checkboxes say "Yunlen Spend Card", that's a fail.

**Pre-checked = FAIL**: Every checkbox must be unchecked by default and require active user selection. Pre-checked boxes do not satisfy affirmative consent requirements.

## Card Creation
- [ ] Flow ends with an international virtual or physical card explicitly displayed — a visible card face, masked card number, card network logo, and/or "Active" status. A generic home or dashboard screen without a visible card object does not satisfy this.
