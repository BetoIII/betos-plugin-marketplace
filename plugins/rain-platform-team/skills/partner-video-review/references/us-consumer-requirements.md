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

1. [ ] **E-Sign Consent / E-Sign Disclosure** — standalone checkbox, first (canonical text: *"I consent to the E-Sign Disclosure."*). Must link **directly to Rain's hosted notice** at `legal.raincards.xyz/legal/electronic-communications-notice` (document title: "E-Sign & Electronic Communications Notice"). Partners were previously asked to fork this template and rebrand "Rain" as their own name — as of Aug 2026 Rain Legal requires linking to the Rain-hosted document as-is, with no forked/rebranded copies. Cannot be bundled with other items.

2. [ ] **Account Opening Privacy Notice** — standalone checkbox. Text: *"I accept the Account Opening Privacy Notice."* Links to a **partner-hosted** page on the partner's own domain (e.g., `dionapp.com/glba`); the content is the GLBA "FACTS — What does Third National ('Issuer') do with your personal information?" table, provided to the partner by Rain's account representative.
   > **This item is required for US Consumer flows specifically — it does not appear in International Consumer or Business flows.** A US Consumer flow that goes E-Sign → Card Terms directly (skipping the Account Opening Privacy Notice) is non-compliant. Conversely, seeing the Account Opening Privacy Notice in this position is correct, **not** an "extra" checkbox.

3. [ ] **[Partner] Card Terms + Issuer Privacy Policy** — *"I accept the [Partner] Card Terms, and the Issuer Privacy Policy."* Per Rain's spec the Issuer Privacy Policy can be linked as-is and **can** be combined with the Card Terms into one checkbox (recommended), or appear as two separate checkboxes — both are acceptable. The Card Terms link goes to a **partner-hosted** page on the partner's own domain (e.g., `dionapp.com/card-terms-us`) — the document itself is Rain's template redlined by the partner and approved by Rain Legal. The Issuer Privacy Policy link must go **directly to Rain's hosted policy** at `legal.raincards.xyz/legal/privacy-policy` (document title: "Rain Privacy Policy") — not the partner's own policy, and not a partner URL that redirects there (redirects like `third-national.com/privacypolicy` should be flagged; ask the partner to link directly). `[Partner]` must be the partner's actual product brand name.

4. [ ] **Accuracy certification** — must include: *"I certify that the information I have provided is accurate and that I will abide by all the rules and requirements related to my [Partner] Spend Card."*

5. [ ] **Non-solicitation acknowledgment** — must include: *"I acknowledge that applying for the [Partner] Spend Card does not constitute unauthorized solicitation."* (US spelling — "unauthorized" not "unauthorised".)

**Partner brand name check**: Every checkbox referencing a product name (e.g., "[X] Spend Card", "[X] Card Terms") must use the partner's actual product/brand name — not the name of a parent company, technology provider, or infrastructure vendor.

**Pre-checked = FAIL**: Every checkbox must be unchecked by default. The user must actively check each one. Any checkbox already ticked when the screen loads is non-compliant.

**Extra checkboxes**: A partner may add additional checkboxes (e.g., the partner's own privacy policy) only if they appear **after** the five required items above and have been pre-approved by Rain Legal. The official Rain US Consumer spec does not require, prohibit, or position any partner-owned privacy policy — flag it as a question for Rain Legal rather than as a pass/fail.

## Consent Link Destinations & Click-Through Demonstration (required as of Aug 2026)

The video must show every hyperlinked agreement being **opened, scrolled through, and returned from** before its checkbox is checked — checking the boxes without opening the links is a FAIL (Rain Legal will bounce the submission).

| # | Link | Host | Required destination (verify domain in the visible address bar) |
|---|---|---|---|
| 1 | E-Sign Disclosure | Rain | `legal.raincards.xyz/legal/electronic-communications-notice` — "E-Sign & Electronic Communications Notice" |
| 2 | Account Opening Privacy Notice | Partner | Partner domain (e.g., `dionapp.com/glba`) — GLBA FACTS table |
| 3a | [Partner] Card Terms | Partner | Partner domain (e.g., `dionapp.com/card-terms-us`) |
| 3b | Issuer Privacy Policy | Rain | `legal.raincards.xyz/legal/privacy-policy` — "Rain Privacy Policy" |

**Nested links inside the partner-hosted Card Terms** (the video must show at least the Prohibited Activities click-through; the canonical video shows both):
- [ ] **Prohibited Activities** → `legal.raincards.xyz/legal/prohibitions` ("Rain Prohibitions List") — tapped from within the Card Terms and scrolled.
- [ ] **E-Sign & Electronic Communications Notice** → `legal.raincards.xyz/legal/electronic-communications-notice` — the Card Terms must reference and link the Rain-hosted notice.

Checkboxes 4 (Accuracy) and 5 (Non-solicitation) have **no links** — no click-through applies.

Notes for the reviewer:
- Phone browsers usually show only the domain in the URL pill (`legal.raincards.xyz` vs the partner's domain) — that is sufficient evidence; full paths are rarely visible.
- The canonical pattern (Dion `US_conditions_agreement.MP4`, Aug 19 2026): E-Sign notice opened and scrolled end-to-end → return → check #1; GLBA notice on partner domain scrolled fully → check #2; Card Terms scrolled with nested Prohibitions and E-Sign links clicked (both resolving to `legal.raincards.xyz`) → Issuer Privacy Policy opened at `legal.raincards.xyz` and scrolled fully → check #3; then #4 and #5; "Confirm & issue card" enables only once all 5 are checked.
- Partial scrolling of a long document is acceptable as ⚠️ Partial with a note, but never opening a link at all is a ❌ Fail for that link.

## Card Creation
- [ ] Flow ends with a US virtual or physical card explicitly displayed — card face, masked number, and/or "Active" status visible. A generic home screen without a visible card object does not satisfy this.
