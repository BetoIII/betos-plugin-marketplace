---
name: send-messages
description: This skill should be used when the user asks to "send messages to my contacts", "send bulk SMS", "message multiple people", "send personalized messages", "text everyone", or wants to send SMS messages to multiple recipients using templates.
---

# Send Messages

Send personalized SMS messages to multiple contacts using templates with variable placeholders.

## Overview

This skill guides users through creating a bulk message campaign by collecting two critical pieces of data and then confirming the  campaign with the user: 1) Submit the list of contact recipients - with 'phone_number' being the only required field, 2) Submit the message to send (with customized variables), and 3) Give a preview of the campaign. After the user has confirmed, the skill will send the message individually to every recipient.

For interactive composition, this skill uses the **playground skill** to generate self-contained HTML artifacts that the user interacts with. The user then copies the output and pastes it back to Claude for parsing.

## Prerequisites

- macOS with Messages.app installed
- Messages.app configured with Apple ID and SMS capability
- Claude Desktop (this plugin is designed for the VM environment)

## Workflow

### Step 1: Gather Recipients

Ask the user provide their contact list. They can paste text in the chat, attach files with contacts, or connect to any data source.

Tell the user they can provide contacts in any format as long as each record includes a phone number:

> "Please provide your contact list. You can use:
>
> **CSV format:**
> ```
> phone_number,name,company
> +15551234567,John,Acme Corp
> +15559876543,Sarah,Tech Inc
> ```
>
> **JSON format:**
> ```json
> [
>   {"phone_number": "+15551234567", "name": "John", "company": "Acme Corp"},
>   {"phone_number": "+15559876543", "name": "Sarah", "company": "Tech Inc"}
> ]
> ```
>
> **Or simple list:**
> ```
> +15551234567 John Acme
> +15559876543 Sarah Tech
> ```
>
> Only `phone_number` is required. Any additional fields can be used as template variables."

Wait for the user to provide their contact data, then parse it.


**Parse and Store** the contact list to use in the messaging workflow.

### Step 2: Get the Message Template

Ask the user how they want to provide their message template:

```json
{
  "questions": [
    {
      "id": "template-method",
      "prompt": "How would you like to compose your message template?",
      "options": [
        {
          "id": "Quick",
          "label": "Quick - Type it in chat"
        },
        {
          "id": "Interactive",
          "label": "Interactive - Use visual composer"
        }
      ]
    }
  ]
}
```

#### If the user selects "Quick"

Tell the user how to submit their message:

> "Please provide your message template. Use double curly braces for variables: `{{variable_name}}`
>
> Example:
> ```
> Hi {{name}}, just checking in about {{topic}}. Let me know if you need anything!
> ```
>
> Common variables:
> - `{{name}}` - Recipient's name
> - `{{first_name}}` - First name only
> - `{{company}}` - Company name
> - `{{date}}` - Date
> - Any custom variable you need"

Wait for the user to provide their template text.

#### If the user selects "Interactive"

Use the **playground skill** to build an interactive SMS composer:

1. Invoke the playground skill and tell it to build an SMS template composer using the `templates/sms-composer.md` template
2. The playground skill will generate a self-contained HTML file and open it
3. Tell the user: "I've opened the SMS Template Composer. Compose your message, then click **Copy Prompt** and paste the result back here."
4. Wait for the user to paste the output

When the user pastes the output, it will be natural language like:

> "I've composed an SMS message. The message is: 'Hi {{name}}, happy holidays from {{company}}! Enjoy {{discount}}% off.'"

Parse this output to extract:
- Template text (between "The message is: '" and "'. It uses" or end of string)
- Variables (after "uses N variable(s): " as comma-separated list)

**Store the template message** Store the message to use in the messaging workflow

### Step 3: Preview Bulk Message Campaign

After collecting both the message and contact list, show a preview of the bulk message campaign you have prepared:

For the first 3 recipients:
1. Start with the template
2. Replace each `{{variable}}` with the recipient's value
3. If a variable is missing for a recipient, flag it

**Example:**
Template: `Hi {{name}}, checking in about {{topic}}`
Recipient: `{"name": "John", "topic": "project"}`
Result to show the user: `Hi John, checking in about project`

Then offer the user a visual preview:

```json
{
  "questions": [
    {
      "id": "preview-method",
      "prompt": "Would you like to preview your message and recipients before sending?",
      "options": [
        {
          "id": "interactive",
          "label": "Yes - Open visual preview"
        },
        {
          "id": "skip",
          "label": "No - Proceed to send"
        }
      ]
    }
  ]
}
```

#### If the user selects "Yes"

Use the **playground skill** to build a message preview:

1. Invoke the playground skill and tell it to build a message preview using the `templates/preview.md` template
2. **Pre-populate** the playground with the user's template and contacts from the current session
3. The playground will show each personalized message in iMessage-blue phone mockups with stats
4. Tell the user: "I've opened the Message Preview. Make any edits in the browser, then click **Copy Prompt** and paste the result back here to confirm sending."
5. Wait for the user to paste the output

When the user pastes the output, it will include edits to the bulk messaging campaign, or direction to proceed. Edit campaign (if necessary).

This flow confirms the user has reviewed and approved all messages. Proceed to sending.

#### If the user selects "No"

Skip to Step 4 (Validate Phone Numbers).

### Step 4: Validate Phone Numbers

For each phone number:
- Remove formatting characters (spaces, dashes, parentheses)
- Verify it's numeric
- Check length (10 digits for US, or international format with +)

**Valid formats:**
- `5551234567` (10 digits, US)
- `+15551234567` (international format)
- `555-123-4567` (will be cleaned to 5551234567)

**If invalid:** Report which phone numbers are invalid and ask user to correct.

### Step 5: Generate Personalized Messages

For each recipient:
1. Start with the template
2. Replace each `{{variable}}` with the recipient's value
3. If a variable is missing for a recipient, flag it

**Example:**
Template: `Hi {{name}}, checking in about {{topic}}`
Recipient: `{"name": "John", "topic": "project"}`
Result: `Hi John, checking in about project`

**Variable replacement algorithm:**

```python
import re

def personalize_message(template, recipient_data):
    message = template
    variables = re.findall(r'\{\{([^}]+)\}\}', template)
    
    for var in variables:
        var_clean = var.strip()
        if var_clean in recipient_data:
            message = message.replace(f'{{{{{var}}}}}', str(recipient_data[var_clean]))
        else:
            message = message.replace(f'{{{{{var}}}}}', f'[MISSING: {var_clean}]')
    
    return message
```

### Step 6: Preview Messages

Display all personalized messages for user review:

```
Preview (3 messages):

1. To: John (+15551234567)
   Message: Hi John, checking in about project

2. To: Sarah (+15559876543)
   Message: Hi Sarah, checking in about meeting

3. To: Mike (+15555551234)
   Message: [full message shown]
```

Ask for confirmation: "Ready to send these messages?"

### Step 7: Send Messages via Messages.app

For each recipient, use AppleScript to send via Messages.app:

**AppleScript command:**

```applescript
osascript -e 'tell application "Messages"
    set targetService to 1st account whose service type = iMessage
    set targetBuddy to participant "[PHONE]" of targetService
    send "[MESSAGE]" to targetBuddy
end tell'
```

**Implementation steps:**
1. Escape quotes in message text
2. Replace [PHONE] with recipient's phone number
3. Replace [MESSAGE] with personalized message
4. Execute via Shell tool with timeout (10 seconds per message)
5. Report progress: "Sent 1/3...", "Sent 2/3...", etc.

**Error handling:**
- If Messages.app is not running, attempt to launch it
- If send fails, report which message failed
- Continue with remaining messages

**Note for Claude Desktop VM:** If running in Claude Desktop's VM environment and Messages.app is not accessible, offer an alternative output format:

```
Messages.app is not accessible in this environment. Here are your personalized messages ready to send manually:

1. +15551234567 (John)
   Hi John, checking in about project

2. +15559876543 (Sarah)
   Hi Sarah, checking in about meeting

[Copy and send these manually through Messages.app]
```

### Step 8: Summary

After sending all messages (or providing the manual list), display a summary:

**If sent successfully:**

```
SMS Campaign Complete!

Sent: 3 messages
Failed: 0

All messages sent via Messages.app.
```

**If any failures:**

```
SMS Campaign Complete!

Sent: 2 messages
Failed: 1 (Mike - Messages.app error)

Review failed messages and retry if needed.
```

**If manual output provided:**

```
SMS Campaign Prepared!

Generated: 3 personalized messages

Messages are ready to send manually via Messages.app.
```

### Step 9: Save Work & Cleanup
Ask the user if they would like save any records:
```json
{
  "questions": [
    {
      "id": "Save Rercords?",
      "prompt": "Would you like to save any data from this campaign?",
      "options": [
        {
          "id": "Message Template",
          "label": "Markdown file of the message template"
        },
        {
          "id": "Activity Log",
          "label": "JSON file of the message template & contact recipients"
        },
        {
          "id": "skip",
          "label": "Nope - End the workflow"
        }
      ]
    }
  ]
}
```

**If the user selects Message Template**
Create a markdown file of the message template used in the bulk message campaign and put it in the /output folder, including a simple timestamp in the filename. 

**IF the user selects Activity Log**
Create a json file with two objects: 1) the message template used, and 2) the contacts, including any metadata or additional fields in the contact record. Put this json file in the ouput folder, including a simple timestamp in the filename.

## Important last step
BEFORE YOU END THIS SKILL & regardless of whether the user completed the workflow, always delete any *.html files that were created during this session. Check both the plugin root `output/` folder and the session's `/sessions/[session-id]/mnt/outputs/` folder. Do not delete any other files besides html pages.

## Important Notes

**Professional Demeanor**
- You are a professional assistant helping someone accomplish important work
- Be helpful and succinct
- Do not use emojis in your conversation or when rendering web pages

**Messages.app requirements:**
- Messages.app must be signed in with Apple ID
- Phone number must be configured for SMS sending
- First send may prompt for permissions

**Privacy:**
- Messages are sent immediately, no logging
- User confirmation required before sending
- Preview shown before sending

**Rate limiting:**
- No artificial rate limiting applied
- Be mindful of carrier limits (typically 100-200 SMS per day)
- Consider spacing messages if sending to many recipients

**Error scenarios:**
- Messages.app not configured: Prompt user to configure
- AppleScript permission denied: Instruct user to grant permissions
- Network unavailable: Report error and suggest retry

**Claude Desktop VM Limitations:**
- This plugin is designed for Claude Desktop's VM environment
- No persistent storage - each session is independent
- If Messages.app is not accessible, manual sending instructions are provided

## Troubleshooting

**Messages don't send:**
- Verify Messages.app is signed in
- Check System Settings > Privacy > Automation > Claude Desktop > Messages
- Ensure phone number is configured for SMS

**Variables not replacing:**
- Check variable names match exactly (case-sensitive)
- Verify recipient data includes all variables from template
- Look for typos in variable names

**Playground artifacts not opening:**
- Ensure the playground skill is properly installed
- Check that template files exist in `skills/playground/templates/`
- Try the "Quick" method as an alternative
