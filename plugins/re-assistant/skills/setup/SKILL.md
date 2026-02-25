---
name: setup
description: >-
  This skill should be used when the user says "set up re-assistant", "configure
  re-assistant", "run setup", "update my agent profile", "change my agent info",
  or runs /re-assistant:setup. Collects the agent's personal profile and saves it
  persistently so all re-assistant skills know who is using the plugin.
---

## Purpose

Collect and save the agent's personal profile to `~/.claude/re-assistant.local.md`. This profile is used by all re-assistant skills to personalize output — offer letters, Zenlist links, and report headers. Once saved, the profile persists across all sessions and can only be updated by running this setup skill again.

## Step 1 — Check for Existing Profile

Read the file `~/.claude/re-assistant.local.md`.

- If the file exists and contains a YAML frontmatter block with `agent_name` set, show the current profile values:

  ```
  Your current agent profile:

  - Agent Name: [agent_name]
  - Team Name: [team_name or "Not set"]
  - Brokerage: [brokerage_name]
  - Email: [agent_email]
  - Zenlist Username: [zenlist_username or "Not set"]
  ```

  Then ask: "Would you like to update your profile, or keep the current one?"

  - If the user wants to keep the current profile, end the skill: "Your profile is unchanged. All re-assistant skills will continue using your saved profile."
  - If the user wants to update, proceed to Step 2.

- If the file does not exist or is empty, proceed directly to Step 2.

## Step 2 — Collect Profile Values

Use the AskUserQuestion tool to collect the following. Ask all non-optional questions in a single interaction where possible.

Ask for:

1. **Agent Name** *(required)* — Full name as it should appear in emails and reports (e.g., "David Raygorodsky")
2. **Brokerage Name** *(required)* — The brokerage (e.g., "Vanguard Properties")
3. **Agent Email** *(required)* — Professional email address
4. **Team Name** *(optional)* — Leave blank if not on a named team (e.g., "The Nolan Group")
5. **Zenlist Username** *(optional)* — The username portion of their Zenlist share URL. Format: `https://zenlist.com/listing/mlslistings:[ID]?as=[USERNAME]`. Enter only the username (e.g., `david.ray`). Leave blank to omit Zenlist links.

Do not proceed until at minimum Agent Name, Brokerage Name, and Agent Email are provided.

## Step 3 — Confirm Before Saving

Show the collected values to the user for confirmation before writing:

```
Ready to save your agent profile:

- Agent Name: [value]
- Team Name: [value or "Not set"]
- Brokerage: [value]
- Email: [value]
- Zenlist Username: [value or "Not set"]

Save this profile?
```

If the user confirms, proceed to Step 4. If they want changes, return to Step 2 for the specific field(s) they want to change.

## Step 4 — Save the Profile

Write the following content to `~/.claude/re-assistant.local.md`, replacing any existing content:

```
---
agent_name: "[AGENT_NAME]"
team_name: "[TEAM_NAME]"
brokerage_name: "[BROKERAGE_NAME]"
agent_email: "[AGENT_EMAIL]"
zenlist_username: "[ZENLIST_USERNAME]"
---

# RE Assistant Agent Profile

This file stores the agent profile for the re-assistant plugin. To update these values, run `/re-assistant:setup`.
```

Leave `team_name` and `zenlist_username` as empty strings `""` if the user did not provide them.

Use the Write tool to create or overwrite the file at `~/.claude/re-assistant.local.md`.

## Step 5 — Confirm Success

After writing the file, confirm to the user:

```
Agent profile saved.

All re-assistant skills — comparable analysis, offer letters, and disclosure summaries — will now use your profile automatically.

To update your profile in the future, run /re-assistant:setup again.
```

## Error Handling

- If the Write tool fails, tell the user: "Unable to save the profile to `~/.claude/re-assistant.local.md`. Please check that your `~/.claude/` directory exists and is writable."
- If the user provides an email that doesn't look valid, note it but do not block — save what they provided.
- Never save a partial profile (i.e., if agent_name, brokerage_name, or agent_email are blank, ask again before writing).
