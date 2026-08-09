---
name: rocketlane-api
description: >
  Full read/write access to the Rocketlane API for natural-language requests. Use this skill
  whenever the user asks anything involving Rocketlane — look up a project or client, check
  project status/stage/launch date, list or create tasks, update task status or assignees,
  move tasks between phases, log or review time entries, look up users or team members,
  download task attachments, manage spaces and space documents, review invoices, or update
  custom fields. Trigger on any mention of Rocketlane or phrases like "check the project",
  "find [company] in Rocketlane", "what's the status of", "who's on the team for",
  "create a task", "log time", "update the stage", "download the attachment", or
  "look up [client name]". Handles first-time API key setup, pagination, and both API versions
  automatically.
---

# Rocketlane API

Drive any Rocketlane API function from natural language. All requests go through
`scripts/rl.py` in this skill's directory, which reads the API key from a local config file —
**never put the key on a command line, in a repo file, or in your output.**

## Step 0 — API key (first run only)

Check for a stored key:

```bash
test -s ~/.config/rain-claude/rocketlane.env && echo "key configured" || echo "MISSING"
```

If configured, continue to Step 1 — do not read the file's contents or display the key.

If MISSING, run first-time setup:

1. Tell the user: a Rocketlane API key is needed once; it will be stored at
   `~/.config/rain-claude/rocketlane.env` (outside any repo, chmod 600) and never asked for again.
   They can generate one in Rocketlane under **Settings → API**.
2. Ask the user to paste their API key (use AskUserQuestion with "Other"/free-text, or just ask).
3. Save it without echoing it anywhere else:

```bash
mkdir -p ~/.config/rain-claude && chmod 700 ~/.config/rain-claude
printf 'ROCKETLANE_API_KEY=%s\n' '<pasted-key>' > ~/.config/rain-claude/rocketlane.env
chmod 600 ~/.config/rain-claude/rocketlane.env
```

4. Validate immediately:

```bash
python3 "<this-skill-dir>/scripts/rl.py" GET /users -q pageSize=1
```

   On HTTP 401, the key is wrong — delete the file, tell the user, and re-ask. Never persist a
   key that fails validation.

**Key hygiene rules (always):** never print the key value, never write it into any file inside
a git repository, never pass it as a curl header argument. `rl.py` reads it from the env file
itself. An exported `ROCKETLANE_API_KEY` env var overrides the file if present.

## Step 1 — Map the request to an endpoint

Common intents:

| User intent | Call |
|---|---|
| Find a project / client by name | `GET /projects -q projectName.cn=<name>` (case-sensitive contains; if no hit, fall back to `GET /projects --all` and match client-side) |
| Project status / stage / team | `GET /projects/{projectId}` then read `status.label`, `fields[]`, `teamMembers` |
| List tasks on a project | `GET /tasks -q projectId.eq=<id> -q pageSize=100` |
| Create a task | `POST /tasks -d '{"taskName":"...","project":{"projectId":<id>}}'` |
| Update task / project | `PUT /tasks/{id}` / `PUT /projects/{id}` |
| Assign someone to a task | `POST /tasks/{id}/add-assignees` |
| Move task to a phase | `POST /tasks/{id}/move-phase -d '{"phase":{"phaseId":<id>}}'` |
| Log time | `POST /time-entries -d '{"date":"YYYY-MM-DD","minutes":<n>,"task":{"taskId":<id>}}'` (exactly one source: activityName, task, projectPhase, or project) |
| Review time | `GET /time-entries -q date.ge=<date>` |
| Task attachments | `--v1 GET /tasks/{taskId}` (only v1 returns `attachments[]`) |
| Download attachment | `--v1 GET /attachments/{id}/download --download <dir>` |
| Who is a user | `GET /users` / `GET /users/{id}` |
| Resolve custom-field IDs | `GET /fields` |

Full catalog with filters and body shapes: read `references/endpoints.md`. If a request/body
schema isn't covered there, fetch `https://developer.rocketlane.com/reference/<slug>.md`
(index at `https://developer.rocketlane.com/llms.txt`) before calling — don't guess payloads.

## Step 2 — Call the API

```bash
python3 "<this-skill-dir>/scripts/rl.py" METHOD PATH [-q key=value ...] [-d '<json>'] [--v1] [--all] [--download DIR]
```

Examples:

```bash
# Search projects by name fragment
python3 "<this-skill-dir>/scripts/rl.py" GET /projects -q projectName.cn=Acme

# Every project (auto-paginates, ~300 records across 3+ pages)
python3 "<this-skill-dir>/scripts/rl.py" GET /projects --all

# Tasks on a project
python3 "<this-skill-dir>/scripts/rl.py" GET /tasks -q projectId.eq=123 -q pageSize=100

# Task with attachments (v1 quirk)
python3 "<this-skill-dir>/scripts/rl.py" --v1 GET /tasks/4567

# Download an attachment
python3 "<this-skill-dir>/scripts/rl.py" --v1 GET /attachments/99/download --download ./rocketlane-downloads

# Create a time entry
python3 "<this-skill-dir>/scripts/rl.py" POST /time-entries -d '{"date":"2026-07-28","minutes":120,"task":{"taskId":4567},"notes":"API integration"}'
```

## Step 3 — Pagination and filters

- List endpoints return `pagination: {hasMore, nextPageToken, nextPage, totalRecordCount}`.
  Prefer `--all` to auto-follow; it merges every `data[]` page and reports `totalFetched`.
- `pageSize` caps at 100. `nextPageToken` expires in ~15 minutes.
- Filter syntax is `field.operator=value` (`eq`, `gt`, `lt`, `ge`, `le`, `cn`, `nc`, `oneOf`,
  `noneOf`); combine with `match=all|any`. Custom-field filters:
  `project.field.{fieldId}.value=<v>`. Details in `references/endpoints.md`.
- The API's `nextPage` URL sometimes says `http://` — `rl.py` always rebuilds HTTPS URLs, so
  never follow `nextPage` by hand.

## Step 4 — Write-operation safety

Before ANY `POST`, `PUT`, or `DELETE`:

1. Show the user the exact method, path, and JSON body you intend to send.
2. Get their explicit confirmation first. The only exception is the read-only-in-effect
   `GET`-like probes above; anything that mutates Rocketlane waits for a yes.
3. `DELETE` requires the user to have named the specific record; prefer
   `POST /projects/{id}/archive` over deleting projects. Never bulk-delete, and never loop a
   write over many records without listing every affected record first.

## Step 5 — Interpret responses (Rain conventions)

- Custom fields arrive as `fields[]` of `{fieldLabel, fieldValueLabel}` — flatten by label.
  Rain's key labels: **Stage, Client Priority, Target Launch Date, Tier, Region, Notes (HTML —
  strip tags), Compliance, Authorization Flow, Card Type**.
- `teamMembers.members[]` = Rain staff; `teamMembers.customers[]` = client contacts (with
  `emailId`). Timestamps (`createdAt`, `updatedAt`) are epoch milliseconds.
- Writing custom fields needs `fieldId` + typed `fieldValue` — resolve via `GET /fields`.
  Full mapping guide: `references/fields.md`.

## Known limitations

- **Form responses cannot be enumerated via the API** (verified live, July 2026). Files that a
  form uploaded ARE downloadable — they are ordinary attachments — but there is no API route
  that lists a response's attachment IDs:
  - `GET /projects/{projectId}/forms` exists and returns a correct `totalRecordCount`, but every
    object in `data[]` comes back **empty** (`{}`) regardless of `includeAllFields` /
    `includeFields` — the tenant's forms are counted but not described.
  - `/form-responses/{id}`, `/projects/{id}/forms/{formId}`, `/projects/{id}/forms/responses/{id}`
    → 404 on both `/api/1.0` and `/api/v1`. `/forms/{id}` is a real route but only accepts a
    form ID, which nothing exposes.
  - Web-UI URLs (`https://<tenant>.rocketlane.com/projects/{id}/forms/responses/{responseId}`)
    are session-authenticated pages, not API endpoints.

  **Practical routes to a form response's files, in order:**
  1. If the upload attached to a task, use `--v1 GET /tasks/{taskId}` → `attachments[]`, then
     `--v1 GET /attachments/{id}/download`. (Many Rocketlane forms do NOT attach to a task.)
  2. Get the attachment ID from outside the API — the response page in a browser (file links
     carry `data-attachment-id` or `/attachments/<id>/`), or a webhook consumer's logs — then
     download it with route 1's download call. Rocketlane's "form completed" webhook payload
     itself omits file-upload answers.
  3. Never brute-force or scan attachment IDs to find a submission; IDs are tenant-global and
     you would be pulling unrelated customers' files.

## Presenting results

- Lead with the direct answer (status, owner, date), then supporting detail.
- Use a table for lists of projects/tasks/time entries; prose for a single record.
- Strip HTML from `Notes`/`taskDescription` before showing.
- If a lookup by name returns multiple candidate projects, list them and ask which one.
