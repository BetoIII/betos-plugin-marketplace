# SMS Composer Template

Use this template when the web builder is about composing SMS message templates with variable placeholders for bulk messaging campaigns.

## Styling

Reference the global stylesheet and component reference in the templates folder to guide your styling:

```html
<link rel="stylesheet" href="global-styles.css">
<link rel="stylesheet" href="component-reference.md">
```

All component styles (phone preview, buttons, forms, etc.) are defined in the global stylesheet.

## Layout

```
+-------------------+----------------------+
|                   |                      |
|  Compose Message  |  Phone Preview       |
|  • Preset buttons |  (dark mockup with   |
|  • Insert Variable|   iMessage-blue      |
|  • Message text   |   message bubble     |
|                   |   showing rendered   |
|                   |   template           |
|                   +----------------------+
|                   |  Prompt output       |
|                   |  [ Copy Prompt ]     |
+-------------------+----------------------+
```

## Header
Title: SMS Template Composer
Subtitle: Compose your message. Then copy the resulting prompt output and paste back into Claude

## Compose Message Section
Title: Compose Message
Subtitle: Use double curly braces for each personalization: {{variable}}

Use this definition table to render the components in this section:

| Decision | Control | Example |
|---|---|---|
| Quick start | Clickable preset buttons | Meeting, Invite, Open House |
| Insert Variable | Clickaable preset buttons | `{{name}}`, `{{first_name}}`, `{{company}}`, `{{date}}` |
| Message body | Textarea with {{variable}} syntax | "Hi {{name}}, reminder about {{event}}" |

## Phone Preview
Use this section to render the message inside a dark phone-frame mockup with message bubble styling:

```javascript
function renderPreview() {
  const preview = document.getElementById('preview-message');
  
  if (!state.template.trim()) {
    preview.innerHTML = '<span class="preview-empty">Your message preview will appear here...</span>';
    return;
  }
  
  // Render template with {{variable}} highlighting
  const rendered = state.template.replace(
    /\{\{(\w+)\}\}/g,
    '<span class="variable-highlight">{{$1}}</span>'
  );
  
  preview.innerHTML = rendered;
}
```

## Prompt output
Use this section to display the resulting ouput prompt, framing the output as a natural description of the composed template, not a key-value dump:

> "I've composed an SMS template. The message is: 'Hi {{name}}, happy holidays from {{company}}! Enjoy {{discount}}% off.' It uses 2 variables: name, company."

Place a button that says "Copy Prompt" at the bottom of the section that copies the prompt to the user's clipboard.

Implementation pattern:

```javascript
function extractVariables(template) {
  const regex = /\{\{(\w+)\}\}/g;
  const vars = new Set();
  let match;
  while ((match = regex.exec(template)) !== null) {
    vars.add(match[1]);
  }
  return Array.from(vars);
}

function updatePrompt() {
  const promptEl = document.getElementById('prompt-output');

  if (!state.template.trim()) {
    promptEl.textContent = 'Compose a message above to generate output.';
    return;
  }

  const vars = extractVariables(state.template);

  let prompt = `I've composed an SMS template.`;
  prompt += ` The message is: '${state.template}'.`;

  if (vars.length > 0) {
    prompt += ` It uses ${vars.length} variable${vars.length > 1 ? 's' : ''}: ${vars.join(', ')}.`;
  }

  promptEl.textContent = prompt;
}

// IMPORTANT: Use this exact copyPrompt implementation.
// navigator.clipboard requires a secure context (HTTPS/localhost).
// Claude Desktop opens files via file:// URLs (Electron WebView), which
// blocks the Clipboard API. The execCommand fallback works in file:// contexts.
function copyPrompt() {
  const text = document.getElementById('prompt-output').textContent;
  if (text === 'Compose a message above to generate output.') return;

  const onSuccess = () => {
    const btn = document.getElementById('copy-btn');
    btn.textContent = '✓ Copied!';
    btn.classList.add('copied');
    setTimeout(() => {
      btn.textContent = 'Copy Prompt';
      btn.classList.remove('copied');
    }, 2000);
  };

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(onSuccess).catch(() => fallbackCopy(text, onSuccess));
  } else {
    fallbackCopy(text, onSuccess);
  }
}

function fallbackCopy(text, callback) {
  const ta = document.createElement('textarea');
  ta.value = text;
  ta.style.cssText = 'position:fixed;opacity:0;pointer-events:none;';
  document.body.appendChild(ta);
  ta.focus();
  ta.select();
  try {
    document.execCommand('copy');
    if (callback) callback();
  } catch (e) {
    console.error('Copy failed', e);
  }
  document.body.removeChild(ta);
}
```

## State structure

```javascript
const state = {
  template: ''
};
```

## Quick Start Presets (EXACT VALUES — do not invent or modify)

The quick start preset buttons must load these exact template strings. Do not create your own presets or alter the wording, variables, or formatting.

```javascript
const PRESETS = {
  'Meeting Reminder': 'Hey {{name}}, reminder about our {{event}} on {{date}} at {{time}}. See you there!',
  'Invite': "You're invited to {{event}} on {{date}}! RSVP by {{rsvp_date}}. Hope to see you there!",
  'Open House': `Hey {{name}}, it was a pleasure meeting you at the open house today. Curious what you thought of {{address}}. Here's a link to Zenlist:

{{zenlist_link}}

Let me know if you'd be interested in collaborating on Zenlist and seeing some places together!`
};
```

## No persistence

This web builder has NO saved templates sidebar and NO persistent storage. Each session starts fresh. The user composes a template, copies the prompt output, and pastes it back to Claude.
