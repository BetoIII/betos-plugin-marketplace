---
name: slack-channel-identifier
description: >
  Identify which customer Slack channel belongs to a Rocketlane project (or any customer/company
  name), by correlating the project's creation time with channels the Rocketlane Slack bot
  auto-created, cross-checked against current channel names. Use whenever someone asks "which
  channel is [customer]?", "what's the Slack channel for this project/account?", "find the
  customer channel", "where do I post this for [client]?", "is #ext-foo-rain the right channel
  for [customer]?", or needs the destination channel verified before sending anything
  customer-facing into Slack. Also use to audit an ext-*-rain channel's provenance, to tell two
  similarly-named channels apart, or when a report/update must reach a client's shared channel
  and picking the wrong one would leak it to a different client. Read-only — identifies, never posts.
---

# Slack Channel Identifier

Resolve which Slack channel belongs to a customer project, with a confidence
level that is safe to gate an automated post on.

**Posting a client's report into a different client's channel is the worst
possible outcome.** Every rule below trades recall for precision on purpose.
When in doubt, report lower confidence and hand the decision back.

## How the correlation works

When a project is created in Rocketlane, its Slack integration bot
(`U07DS8F9STS`) automatically creates a channel shortly afterward — usually
within seconds, occasionally up to ~48 hours. Two independent signals:

1. **Creation-time proximity** (primary). The channel's `created` falls just
   after the project's `createdAt`. Times cannot be edited, so this proves
   which channel was *provisioned for* this project. The window reaches back an
   hour only to absorb clock skew — the bot provisions *after* the project, so
   a **negative delta is weak evidence** and rarely the answer.
2. **Current name** (secondary). Channels are named `ext-{squashed-name}-rain`.
   Both channels and projects get renamed after creation, so names drift — but
   the *current* name is where the customer's team lives **now**, which is
   where a report must actually land.

Neither signal alone is sufficient. The whole job is adjudicating them.

## Step 0 — Slack token (first run only)

```bash
test -s ~/.config/rain-claude/slack.env && echo "token configured" || echo "MISSING"
```

If configured, continue to Step 1 — do not read the file or display the token.

If MISSING, run first-time setup:

1. Tell the user a Slack bot token is needed once, stored at
   `~/.config/rain-claude/slack.env` (outside any repo, `chmod 600`). It needs
   `channels:read`, plus `groups:read` to see private channels. A workspace
   admin creates it under **Slack API → Your Apps → OAuth & Permissions**.
2. Ask them to paste the `xoxb-…` token.
3. Save it without echoing it anywhere:

```bash
mkdir -p ~/.config/rain-claude && chmod 700 ~/.config/rain-claude
printf 'SLACK_BOT_TOKEN=%s\n' '<pasted-token>' > ~/.config/rain-claude/slack.env
chmod 600 ~/.config/rain-claude/slack.env
```

4. Validate immediately with `--all`. On `invalid_auth`, delete the file, tell
   the user, and re-ask — never persist a token that fails validation.

**Never** print the token, put it on a command line, or write it into a repo.

`--project` additionally needs `ROCKETLANE_API_KEY`; the script reads the same
`~/.config/rain-claude/rocketlane.env` the **rocketlane-api** skill writes, so
if that skill is set up there is nothing more to do. Without it, anchor
manually with `--name` / `--created-at`.

## Step 1 — Gather the evidence (one command)

```bash
node "<this-skill-dir>/scripts/fetch-candidates.mjs" --project <projectId>
```

No Rocketlane project? Anchor manually:

```bash
node "<this-skill-dir>/scripts/fetch-candidates.mjs" \
  --name "Acme Corp" --created-at 2026-03-04T18:22:00Z
```

One run prints everything needed: the project anchor, the time-window
candidates with signed deltas, the all-time name cross-check, and an explicit
`!! REVIEW` section when a name match sits outside the time window. Add
`--json` for structured output, `--all` to dump every bot-created channel.

Useful flags: `--window <hours>` (default 48) to widen the upper bound,
`--name-contains <frag>` to override the auto-derived needle, `--bot <id>` if
the integration bot ever changes.

## Step 2 — Apply the confidence rules

Do **not** skip the name cross-check because the time match looks obvious. The
cross-check exists precisely to catch the cases where time is misleading.

**high** — safe to post automatically:
- Time and current name point at the **same** channel; or
- Exactly one channel in the time window, its name is plausible for this
  customer, and the cross-check surfaces no competing live channel elsewhere.

**low** — surface candidates, let a human choose:
- Time match and name match point at **different** channels (see Conflicts);
- Several window candidates the name can't disambiguate;
- A name-only match with no time support;
- A time-only match whose current name plausibly belongs to a *different*
  customer.

**none** — no candidates, or nothing plausible.

**An archived channel is never high.** Report it as a candidate at low/none and
say it's archived. Archived means the customer's team is no longer there.

## Adjudicating conflicts

The script flags every name match outside the time window. Not all are real
conflicts — judge each by asking: *could this channel plausibly be where THIS
customer's team lives now?*

- **Yes → real conflict, cap at low.** A *live* channel whose current name
  matches this customer as well as or better than the window candidate does.
  Renames genuinely swap names across customers. Real case: two projects'
  channels had names swapped, so the channel created 1 second after the
  *Omniwire* project is now `#ext-elvidia-rain`. Time proves provenance; the
  current name is where the team lives. A conflict must gate delivery, not post.
- **No → substring artifact, dismiss it.** An archived channel from a clearly
  different customer that merely shares a substring. Real case: searching
  `blinka` surfaces both `#ext-blinka-rain` (created 6.6 min after the project,
  live) and `#ext-blinkai-rain` (BlinkAI — a different customer, archived seven
  months earlier). Keep your confidence and say why you dismissed it.

## Gotchas

- **Private channels may be invisible.** If the token lacks `groups:read` the
  script warns and lists public channels only. A "no candidates" result under
  that warning is **not conclusive** — say so rather than reporting `none`.
- **Empty window?** Widen stepwise (`--window 168`, then `--window 336`) up to
  ~14 days. Do not widen indefinitely; past ~2 weeks time proximity stops
  proving anything and a match there is name-only (low at best).
- **Same-minute pairs.** Two channels created seconds apart both fall in the
  window; the name cross-check is what separates them. This is the common case
  for batch-created projects.
- **Old projects.** Projects from before the Slack integration existed have no
  channel at all. `none` is the correct, expected answer — don't stretch.
- **Rate limits.** `conversations.list` is Tier 2. The script paginates once
  per run and retries 429s honoring `Retry-After`; a full scan of ~1,600
  channels takes a few seconds. Don't loop it per-candidate.

## Reporting

State the conclusion as: **confidence**, the channel (`#name` + ID), one or two
sentences of reasoning naming which signals agreed, and every candidate
considered — including ones you dismissed, with the reason. At `low` or `none`,
list candidates with their deltas and archived status so a human can decide in
one glance.

## Out of scope by design

This skill **identifies only — it never posts.** Delivery belongs to whatever
system owns the message, so the gate (high confidence + not archived) and the
send stay in one place. If asked to post, identify first, show the result, and
let the caller confirm the destination.

## Provenance

Mirrors the `slack-identify` sub-agent in the `card-art-checker` service
(`lib/slack-identify.js`), which gates automated card-art report delivery.
That version runs unattended in a Vercel function, so it wraps this logic in
its own Claude tool-use loop; here the agent reading this file plays that role,
so the script only fetches evidence. Its production counterpart also validates
the answer against the creator-filtered channel list as a hallucination guard —
the equivalent here is that every channel the script prints came from that same
filtered list, so **never report a channel that does not appear in its output.**
Keep the confidence rules in the two copies in sync.
