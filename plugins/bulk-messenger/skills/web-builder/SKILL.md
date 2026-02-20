---
name: web-builder
description: Creates interactive HTML web builders — self-contained single-file explorers that let users configure something visually through controls, see a live preview, and copy out a prompt. Use when the user asks to make a web builder, explorer, or interactive tool for a topic.
---

# Web Builder

A web builder is a self-contained HTML file with interactive controls on one side, a live preview on the other, and a prompt output at the bottom with a copy button. The user adjusts controls, explores visually, then copies the generated prompt back into Claude.

## When to use this skill

When the user asks for an interactive web builder, explorer, or visual tool for a topic — especially when the input space is large, visual, or structural and hard to express as plain text.

## How to use this skill

1. **Identify the web builder type** from the user's request
2. **Load the matching template** from `templates/`:
   - `templates/sms-composer.md` — SMS template composition (message text, quick start, variables, phone preview)
   - `templates/preview.md` — Message preview (shows personalized messages with template + contacts combined, iMessage-blue phone mockups)
3. **Load the global style sheet and component reference** from `templates/`:
    - `templates/global-styles.md` - Global styles reference
    - `templates/component-reference.md` - Common html components
4. **Follow the template** to build the web builder. If the topic doesn't fit any template cleanly, use the one closest and adapt.

## Core requirements (every web builder)

- **Single HTML file.** Inline all CSS and JS. No external dependencies.
- **Live preview.** Updates instantly on every control change. No "Apply" button.
- **Prompt output.** Natural language, not a value dump. Only mentions non-default choices. Includes enough context to act on without seeing the web builder. Updates live.
- **Copy button.** Clipboard copy with brief "Copied!" feedback.
- **Sensible defaults + presets.** Looks good on first load. Include 3-5 named presets that snap all controls to a cohesive combination.
- **Dark theme.** System font for UI, monospace for code/values. Minimal chrome.

## State management pattern

Keep a single state object. Every control writes to it, every render reads from it.

```javascript
const state = { /* all configurable values */ };

function updateAll() {
  renderPreview(); // update the visual
  updatePrompt();  // rebuild the prompt text
}
// Every control calls updateAll() on change
```

## Prompt output pattern

```javascript
function updatePrompt() {
  const parts = [];

  // Only mention non-default values
  if (state.borderRadius !== DEFAULTS.borderRadius) {
    parts.push(`border-radius of ${state.borderRadius}px`);
  }

  // Use qualitative language alongside numbers
  if (state.shadowBlur > 16) parts.push('a pronounced shadow');
  else if (state.shadowBlur > 0) parts.push('a subtle shadow');

  prompt.textContent = `Update the card to use ${parts.join(', ')}.`;
}
```

## Common mistakes to avoid

- Prompt output is just a value dump → write it as a natural instruction
- Too many controls at once → group by concern, hide advanced in a collapsible section
- Preview doesn't update instantly → every control change must trigger immediate re-render
- No defaults or presets → starts empty or broken on load
- External dependencies → if CDN is down, web builder is dead
- Prompt lacks context → include enough that it's actionable without the web builder
