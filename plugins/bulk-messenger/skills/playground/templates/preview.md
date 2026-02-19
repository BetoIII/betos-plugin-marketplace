# Message Preview Template

Use this template when the playground is about previewing personalized messages — the user has already composed a message template and contact list, and wants to review, edit, and approve the final messages before sending.

## Styling

Reference the global stylesheet and component reference in the templates folder to guide your styling:

```html
<link rel="stylesheet" href="global-styles.css">
<link rel="stylesheet" href="component-reference.md">
```

All component styles (tables, phone preview, buttons, etc.) are defined in the global stylesheet.

## Layout

```
+----------------------------------------------+
|  Contact Table (full width)                  |
|  [clickable rows with trash icon]            |
+---------------------+------------------------+
|  Message Template   | Phone Preview          |
|  (textarea)         | (full phone frame      |
|                     |  with iMessage bubble  |
|                     |  for selected contact) |
+---------------------+------------------------+
|  Send Edits to Claude (inactive until edits) |
|  [greyed out until delete or template edit]  |
+----------------------------------------------+
```

## Interaction model

This preview is a **review & edit** screen, not a create screen. The user arrives with a pre-populated template and contact list from earlier in their session.

### Key interactions:
1. **Click a contact row** → phone preview updates to show that contact's personalized message
2. **Click trash icon** → removes contact, activates "Send Edits to Claude" section
3. **Edit template textarea** → updates phone preview live, activates "Send Edits to Claude"
4. **Fill in missing variables** → updates the variables to be used in the message template
4. **Copy Edits** → only available when edits have been made

## State structure

```javascript
const state = {
  template: '',
  originalTemplate: '',     // snapshot at load time
  contacts: [],
  originalContacts: [],     // snapshot at load time
  fieldNames: [],
  selectedIdx: 0,           // which contact is previewed
  deletedContacts: [],      // removed contacts (for edit summary)
  templateChanged: false
};
```

## Contact Table Section

Full-width table matching the contact-list-manager style:
- Dynamic columns from `fieldNames`
- Phone validation indicator (checkmark/X)
- Green left-border for valid rows, terracotta for invalid
- **Clickable rows** — clicking selects for phone preview (highlighted with blue tint)
- **Trash icon** pinned to right side of each row (SVG trash can, no text) with red 'alert' style coloring
- Trash click removes contact and logs it in `deletedContacts`

## Phone Preview Section

Full-size phone mockup matching the sms-composer style:
- 320px phone frame with notch, dark gradient screen
- iMessage-blue bubble with personalized message for selected contact
- Updates live when template changes or different contact selected
=
## Message Preview Section
This section should include the following:
1. Message Template (Editable)
2. Fill in Missing Variable(s) (if message template has one or variables not available for all contacts)

The fill in missing variable section should display one row for each missing variable, with a text field in each row allowing the user to define the variable. If the user defines a variable, this update should be included in the send edits to claude section.

## Send Edits to Claude section

This is an **edit-aware** component:

### Inactive state (no edits):
- 45% opacity, pointer-events disabled
- Copy button greyed out
- Message: "No edits yet — delete a contact or change the template to activate."

### Active state (edits made):
- Full opacity, blue border highlight
- Summarizes all edits in natural language:
  - Template changes (shows new template text)
  - Deleted contacts (lists each removed contact)
- Copy button enabled

### Edit summary format:
```
I've made edits to the campaign in the preview:

📝 TEMPLATE CHANGED
   Updated message: 'Hi {{name}}, new message here'

🗑 CONTACTS REMOVED (2)
   - phone_number: +15551234567, name: John
   - phone_number: +15559876543, name: Sarah

Remaining: 3 contacts.
Variables: name.

Please proceed with sending the updated campaign.
```

## Component Classes

Use these classes from the global stylesheet:

**Layout:**
- `.container` - Main container
- Use CSS Grid for custom layouts

**Tables:**
- `table`, `th`, `td` - Table elements
- `tr.valid` - Valid row (green border)
- `tr.invalid` - Invalid row (terracotta border)
- `.delete-btn` - Trash icon button

**Phone Preview:**
- `.phone-preview`, `.phone-frame`, `.phone-screen`, `.message-bubble`
- `.variable-highlight` - Highlighted variables

**Prompt Section:**
- `.prompt-section` - Output container
- `.prompt-header` - Header area
- `.prompt-output` - Edit summary text
- `.copy-btn` - Copy button

**Forms:**
- `textarea`, `input[type="text"]`
- `.form-group`, `.form-label`


## Data flow

The playground can receive pre-populated data via URL query parameters:
- `?template=...` — URL-encoded message template
- `?contacts=...` — URL-encoded CSV string

Or the user can manually paste into the textarea. The playground skill should pre-populate when possible.

## No persistence

Each session is independent. The user reviews, optionally edits, copies the edit summary, and pastes it back to Claude to confirm or update the campaign.
