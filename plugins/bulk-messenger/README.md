# Bulk Messenger

Send personalized bulk SMS messages to multiple contacts via Apple Messages.app — directly from Claude.

## Skills

### `/send-messages`
Guides you through a full bulk messaging campaign:
1. **Collect recipients** — paste a CSV, JSON, or plain list; only `phone_number` is required
2. **Compose a template** — type it in chat or use the visual SMS composer
3. **Preview messages** — see each personalized message before sending
4. **Send** — messages are dispatched one-by-one via AppleScript to Messages.app

Template variables use `{{double_curly_braces}}` and map to any field in your contact list.

### `/playground`
Builds interactive HTML artifacts used internally by `send-messages`:
- **SMS Composer** — visual template editor with phone preview
- **Message Preview** — renders all personalized messages in iMessage-style mockups before sending

You can also invoke this skill directly to create custom interactive playgrounds on any topic.

## Prerequisites

- macOS with **Messages.app** configured (signed in with Apple ID, SMS enabled)
- **Claude Desktop** with plugin support

## Installation

Install via the plugin marketplace or copy this directory into your Claude plugins folder.

## Usage

Start a conversation with Claude and say something like:

> "Send a message to my contacts"
> "I want to text everyone on my list"
> "Send bulk SMS using a template"

Claude will walk you through the rest.

## Notes

- Messages are sent individually, not as a group thread
- Carrier SMS limits typically apply (~100–200/day)
- AppleScript automation permission must be granted to Claude Desktop in **System Settings > Privacy & Security > Automation**
- If Messages.app is inaccessible, the skill outputs ready-to-send messages for manual copying

## Author

betojuareziii
