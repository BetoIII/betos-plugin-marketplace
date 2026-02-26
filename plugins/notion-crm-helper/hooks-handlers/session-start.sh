#!/usr/bin/env bash

# Restore Notion CRM config from persistent plugin storage to the session path.
#
# Claude Desktop spins up a fresh VM per co-work session, so ~/.claude/ is
# ephemeral. This hook copies the config from the plugin directory (host
# filesystem, always mounted) to ~/.claude/ at the start of every session.
#
# Persistent copy: $CLAUDE_PLUGIN_ROOT/notion-crm-helper.config.md
# Session copy:    ~/.claude/notion-crm-helper.local.md

PERSISTENT_CONFIG="${CLAUDE_PLUGIN_ROOT}/notion-crm-helper.config.md"
SESSION_CONFIG="${HOME}/.claude/notion-crm-helper.local.md"

if [ -f "$PERSISTENT_CONFIG" ]; then
    mkdir -p "${HOME}/.claude"
    cp "$PERSISTENT_CONFIG" "$SESSION_CONFIG"
fi

exit 0
