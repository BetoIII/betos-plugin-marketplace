# Component Reference

HTML structure examples and class reference for `global-styles.md`.
Used by: `sms-composer`, `preview` templates.

---

## HTML Structure Examples

### Phone Preview with Contact Header

```html
<div class="phone-preview">
  <div class="phone-frame">
    <div class="phone-notch"></div>
    <div class="phone-screen">
      <div class="contact-header">
        <div class="contact-avatar" id="preview-avatar">R</div>
        <div class="contact-info">
          <div class="contact-name" id="preview-contact-name">Recipient</div>
          <div class="contact-status">SMS · delivered</div>
        </div>
      </div>
      <div class="message-bubble" id="preview-message">
        <span class="preview-empty">Your message preview will appear here...</span>
      </div>
    </div>
  </div>
</div>
```

### Card with Output

```html
<div class="card">
  <div class="card-header">
    <span class="output-label">PROMPT OUTPUT</span>
    <button class="btn btn-primary btn-full" id="copy-btn">Copy Prompt</button>
  </div>
  <div class="code-output" id="prompt-output">Output text here...</div>
</div>
```

### Edits Section (inactive → active)

```html
<div class="edits-section inactive" id="edits-section">
  <div class="card-header">
    <span class="output-label">
      <span class="dot"></span>SEND EDITS TO CLAUDE
    </span>
    <button class="btn btn-primary btn-full" id="copy-edits-btn">Copy Edits</button>
  </div>
  <div class="code-output" id="edits-output">No edits yet — delete a contact or change the template to activate.</div>
</div>
```

Activate with JS: `el.classList.replace('inactive', 'active')`

### Contact Table

```html
<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Phone</th>
      <th>Status</th>
      <th></th>
    </tr>
  </thead>
  <tbody id="contact-table-body">
    <tr class="valid">
      <td>John Doe</td>
      <td>+15551234567</td>
      <td><span class="badge valid">✓</span></td>
      <td><button class="btn btn-danger btn-small">🗑</button></td>
    </tr>
    <tr class="invalid">
      <td>Bad Entry</td>
      <td>not-a-phone</td>
      <td><span class="badge danger">✗</span></td>
      <td><button class="btn btn-danger btn-small">🗑</button></td>
    </tr>
  </tbody>
</table>
```

---

## Class Reference

### Layout
| Class | Description |
|---|---|
| `.container` | Main container (max-width: 1400px) |
| `.layout-grid` | Two-column grid, 2rem gap |
| `.header-section` | Centered header block |

### Typography
| Class | Description |
|---|---|
| `h1` | Fraunces serif, 2.5rem |
| `.subtitle` | Gray, 1.1rem |
| `.section-title` | Uppercase, spaced, 2rem |

### Buttons
| Class | Description |
|---|---|
| `.btn` | Base button — always combine with a variant |
| `.btn-primary` | Burnt orange fill |
| `.btn-accent` | Olive green fill |
| `.btn-secondary` | Card background, bordered |
| `.btn-danger` | Terracotta fill |
| `.btn-small` | Compact padding/font |
| `.btn-full` | Full-width block button |
| `.btn-primary.copied` | Switches to success green (copy confirmation) |

**Common compositions:**
- Copy button: `class="btn btn-primary btn-full"`
- Delete/trash: `class="btn btn-danger btn-small"`
- Preset buttons: `class="btn btn-accent"`

### Cards
| Class | Description |
|---|---|
| `.card` | Standard card (dark bg, 16px radius, border) |
| `.card-header` | Flex row, space-between, mb 1rem |

### Badges
| Class | Description |
|---|---|
| `.badge` | Olive pill badge |
| `.badge.valid` / `.badge.success` | Green |
| `.badge.warning` | Yellow |
| `.badge.danger` | Red |

### Phone Preview
| Class | Description |
|---|---|
| `.phone-preview` | Centered card container |
| `.phone-frame` | Black device mockup, 320px |
| `.phone-notch` | iPhone-style notch |
| `.phone-screen` | Dark gradient screen area |
| `.contact-header` | Contact name/avatar bar at screen top |
| `.contact-avatar` | Circular initial avatar |
| `.contact-info` | Name + status wrapper |
| `.contact-name` | Contact name text |
| `.contact-status` | SMS delivery status |
| `.message-bubble` | iMessage-blue bubble, right-aligned |
| `.preview-empty` | Placeholder italic text |
| `.variable-highlight` | Unfilled `{{variable}}` — white bg highlight |
| `.variable-filled` | Filled variable value |
| `.missing-var` | Missing variable — red bg highlight |

### Output Components
| Class | Description |
|---|---|
| `.code-output` | Monospace text display area |
| `.output-label` | Uppercase flex label for section headers |
| `.output-label .dot` | Status dot (animated in `.edits-section.active`) |
| `.edits-section` | Edit-aware output panel |
| `.edits-section.inactive` | 45% opacity, pointer-events off |
| `.edits-section.active` | Full opacity, primary border, dot animates |

### Tables
| Class | Description |
|---|---|
| `table` | Full-width, collapse |
| `th` | Olive header, uppercase |
| `td` | Standard cell |
| `tr.valid` | Green left border |
| `tr.invalid` | Red left border, 70% opacity |
| `tr.selected-row` | Blue tint (active selection) |

### Forms
| Class | Description |
|---|---|
| `.form-group` | Vertical flex field wrapper |
| `.form-label` / `label` | Uppercase, 500 weight |
| `textarea` | Monospace, min-height 150px |
| `.template-area` | Textarea variant, min-height 180px |
| `.presets` | Flex wrap preset button row |

### Empty States
| Class | Description |
|---|---|
| `.empty-state` | Centered empty state container |
| `.empty-state .icon` | Large icon (4rem, 50% opacity) |
