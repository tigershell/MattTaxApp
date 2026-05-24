---
name: branding
description: "Use this skill whenever the user needs to define the visual identity of an app, website, or product. This is stage 2 of the development pipeline, sitting between Product Design and Architect. Trigger when the user says 'branding', 'design the look', 'colour scheme', 'colour palette', 'logo', 'visual identity', 'design system', 'what should it look like', 'fonts', 'UI style', 'make it look good', or when handing off from a completed Product Design Brief. Always run this before the Architect stage so visual decisions are locked before technical decisions are made."
---

# Branding Skill

You are running the **Branding** stage — stage 2 of the development pipeline. You have a product idea from the Product Design Brief. Your job now is to define how it looks and feels — the visual identity that users will experience. This stage produces four outputs: generated logo prompts to take to ChatGPT/DALL-E, a written design brief, a code-ready Python design system, and an HTML design preview that visualises the entire brand in context.

Good visual design isn't decoration. For consumer-facing apps it directly affects whether people trust, enjoy, and keep using the product. Get this right before the Architect starts making technical decisions, so the Coding stage has real values to build with.

---

## The Design Conversation

Work through these areas conversationally — don't fire all questions at once. Listen to the answers and let them inform each other. A well-chosen word from the user about personality often unlocks the entire colour direction.

### 1. Personality & Tone

Start here. Everything else flows from this.

- If this app were a person, how would you describe them? (e.g. friendly and casual, authoritative and professional, playful and energetic, calm and trustworthy)
- What three words should a user feel when they first open it?
- What's the opposite of how you want it to feel? (Knowing what you *don't* want is just as useful)

### 2. Target Audience

Visual language that works for a 22-year-old fitness enthusiast is completely different from what works for a 45-year-old accountant.

- Who is using this? Age range, lifestyle, context?
- Where will they typically use it — phone on the go, desktop at work, tablet at home?
- Are they expecting something that feels consumer-polished, or professional/enterprise?

### 3. References & Inspiration

- Are there any apps, websites, or brands whose visual style you admire — even outside your space? (This is the fastest way to align on direction)
- Any colours, styles, or aesthetics you definitely want to avoid?
- Any competitors in this space whose design you want to deliberately differentiate from?

### 4. Practical Constraints

- Is this primarily a mobile app, desktop app, or web app? (Affects typography scale, touch targets, layout)
- Will there be a logo mark (icon/symbol), a wordmark (just the name styled), or both?
- Are there any existing brand elements to work with, or is this a clean slate?

---

## Visual Direction

Based on the conversation, make concrete recommendations across these areas. Be decisive — give a clear recommendation with reasoning, then offer an alternative if there's a genuine close call.

### Colour Palette

Define a 7-colour palette covering primary brand colours and the supporting greyscale needed for real UI work:

- **Primary** — the dominant brand colour, used for key UI elements, buttons, headers
- **Secondary** — supports the primary, used for accents, highlights, secondary actions
- **Background** — the main surface colour (not necessarily white)
- **Text** — primary text colour (ensure 4.5:1 contrast ratio against background minimum)
- **Muted** — secondary text, captions, placeholders, subtle labels
- **White / Cards** — surface colour for cards, modals, raised elements
- **Border** — subtle dividers, input borders, card outlines

For each colour provide the hex code, a short evocative name (e.g. "Career Blue", "Achievement Gold", "Clean Slate"), and the reasoning — why this colour fits the personality and audience.

The greyscale colours (Muted, White/Cards, Border) often look like an afterthought but they're 80% of what users actually see. Choose them deliberately — a slightly warm grey vs cool grey changes the entire feel of the app.

**Colour psychology quick reference:**
- Blues → trust, calm, professionalism
- Greens → health, growth, nature, money
- Oranges/Reds → energy, urgency, appetite, excitement
- Purples → creativity, luxury, wisdom
- Neutrals (charcoal, slate) → sophistication, seriousness
- Bright/saturated → youth, energy, fun
- Muted/desaturated → maturity, premium, calm

### Typography

Recommend a heading font and body font pairing. Both must be available on Google Fonts (free, easy to use in any Python GUI or web project).

For each font: name, where to get it, and why it fits the brand personality.

| Pairing Style | Heading | Body |
|--------------|---------|------|
| Friendly & modern | Nunito | Open Sans |
| Professional & clean | Inter | Inter |
| Authoritative | Playfair Display | Source Sans 3 |
| Warm & approachable | Lato | Lato |
| Bold & energetic | Oswald | Roboto |
| Elegant & premium | Cormorant Garamond | Raleway |

### Shape & Style Language

- **Border radius** — sharp corners (0px) feel corporate/serious; rounded (8-16px) feel friendly; very rounded (24px+) feel playful
- **Spacing** — tight spacing feels dense/professional; generous spacing feels premium/airy
- **Illustration style** — flat icons, line art, filled icons, photographic, illustrated characters?
- **Overall style** — minimal, rich/detailed, bold, subtle?

---

## Output 1: Logo Generation Prompts (for ChatGPT / DALL-E)

Produce 3 distinct logo direction prompts the user can paste directly into ChatGPT with DALL-E enabled. Each should explore a different creative angle while staying true to the brand personality.

Format each prompt ready to paste — no extra explanation needed inside the prompt itself:

```
LOGO PROMPT 1 — [Direction Name e.g. "Minimal Wordmark"]

Create a professional logo for an app called "[APP NAME]". [APP NAME] is [one line description].

Style: [specific style description]
Colour palette: [primary hex] and [secondary hex] on a white background
Typography feel: [font personality, e.g. "clean sans-serif, modern, slightly rounded"]
Mood: [3 mood words]
Format: Simple, scalable, works at small sizes. White background. No gradients. No drop shadows.
Do not include explanatory text — just the logo.
```

Make all 3 prompts specific and visually distinct from each other so the user gets genuinely different directions to react to.

---

## Output 2: Written Design Brief

Save as `docs/design-brief.md` in the project folder.

```markdown
# Design Brief — [App Name]

## Brand Personality
[3-5 sentences describing the brand voice and visual personality]

## Target Audience
[Who this is designed for and what they expect visually]

## Colour Palette
| Role | Name | Hex | Usage |
|------|------|-----|-------|
| Primary | [name] | #XXXXXX | Buttons, headers, key actions |
| Secondary | [name] | #XXXXXX | Accents, highlights |
| Background | [name] | #XXXXXX | Main surface |
| Text | [name] | #XXXXXX | Body copy, labels |
| Muted | [name] | #XXXXXX | Captions, placeholders, secondary text |
| White / Cards | [name] | #XXXXXX | Cards, modals, raised surfaces |
| Border | [name] | #XXXXXX | Dividers, input borders |

## Typography
- **Heading font:** [Name] — [where to get it] — [why it fits]
- **Body font:** [Name] — [where to get it] — [why it fits]
- **Heading size:** [px]
- **Body size:** [px]
- **Line height:** [value]

## Shape & Spacing
- Border radius: [value]px
- Base spacing unit: [value]px
- Overall style: [description]

## Logo Direction
[Summary of the 3 logo directions explored and which the user preferred]

## Do / Don't
| Do | Don't |
|----|-------|
| [e.g. Use generous whitespace] | [e.g. Use more than 3 colours in one screen] |

## Inspiration References
[Any apps or brands referenced during the conversation]
```

---

## Output 3: Python Design System

Save as `src/design_system.py` in the project folder. This file gets imported by any UI code in the project so colours, fonts, and spacing are never hardcoded.

```python
"""
Design System — [App Name]
Generated from the Branding stage. Import this wherever UI values are needed.
Update here to change the look across the entire app.
"""

# ── Colours ──────────────────────────────────────────────────────────────────
PRIMARY        = "#XXXXXX"   # [colour name] — buttons, headers, key actions
SECONDARY      = "#XXXXXX"   # [colour name] — accents, highlights
BACKGROUND     = "#XXXXXX"   # [colour name] — main surface
TEXT           = "#XXXXXX"   # [colour name] — body copy and labels
TEXT_MUTED     = "#XXXXXX"   # [colour name] — secondary text, placeholders, captions
SURFACE        = "#XXXXXX"   # [colour name] — cards, modals, raised surfaces (often white)
BORDER         = "#XXXXXX"   # [colour name] — dividers, input borders, card outlines

# ── Typography ────────────────────────────────────────────────────────────────
FONT_HEADING   = "[Font Name]"
FONT_BODY      = "[Font Name]"

FONT_SIZE_H1   = 32          # px — main page titles
FONT_SIZE_H2   = 24          # px — section headers
FONT_SIZE_H3   = 18          # px — card titles, sub-headers
FONT_SIZE_BODY = 14          # px — standard body text
FONT_SIZE_SMALL = 12         # px — captions, labels, hints

# ── Spacing ───────────────────────────────────────────────────────────────────
SPACING_XS     = 4           # px — tight gaps between related elements
SPACING_SM     = 8           # px — padding inside small components
SPACING_MD     = 16          # px — standard component padding
SPACING_LG     = 24          # px — section gaps
SPACING_XL     = 40          # px — major layout gaps

# ── Shape ─────────────────────────────────────────────────────────────────────
BORDER_RADIUS  = 8           # px — corners on cards, buttons, inputs
BORDER_WIDTH   = 1           # px — borders on inputs, cards

# ── Shadows (for Tkinter/web — adapt as needed) ───────────────────────────────
SHADOW_COLOUR  = "#00000020" # subtle drop shadow colour (20% black)
```

---

## Output 4: HTML Design Preview

Once the colour palette, typography, and shape decisions have been made, generate a self-contained HTML file that previews all of them together using sample text drawn from the project being built. Save as `docs/design-preview.html`.

The purpose is simple: the user opens it in a browser and can see every visual decision made during this stage, applied in context. Seeing the choices together on a real page reveals issues (poor contrast, fonts that don't pair well, a primary colour that's too aggressive at scale) that aren't obvious from a list of hex codes.

**Requirements:**

- **Single self-contained file** — all CSS inline in a `<style>` block, fonts loaded from Google Fonts via CDN, no external files, no build step. The user should be able to double-click it and have it open in any browser.
- **Show every decision made in the skill** — colour palette (with names and hex codes), heading and body fonts, the type scale, and any shape/spacing decisions (border radius, spacing units). If it was decided in this stage, it appears in the preview.
- **Use sample text drawn from the project, not Lorem Ipsum.** Headings, body copy, button labels, card titles, and any other text in the preview should use phrases that fit the actual product — drawn from the user journey, MVP features, and value proposition in the Product Design Brief. This makes the preview feel like a real product mockup rather than a generic style guide, and reveals whether the chosen styling actually suits the content the app will show.
- **Show the choices in real UI context** — not just isolated swatches and font samples, but applied to the kinds of elements the app will actually have (buttons, cards, sections, whatever fits the product).

The exact layout, sections, and which UI components to include are a judgement call based on what the project is. Use the Product Design Brief to inform what makes sense.

Once the file is generated, tell the user it's ready and suggest they open it in a browser to review. If anything looks off in context, iterate now — adjust the values across all four outputs together so the brief, the Python design system, and the HTML preview stay in sync.

---

## Handing Off

Once all four outputs are complete, tell the user:

> "The brand identity is defined. You now have four artifacts: the logo prompts (take these into ChatGPT with DALL-E), the design brief, the Python design system the code will import, and a self-contained HTML preview at `docs/design-preview.html` — open it in a browser to see the whole brand in context. Once you're happy with how it looks, we can move to the **Architect** stage."

If the user wants to iterate on colours, fonts, or direction after seeing the preview, do it now — adjust the values across all four outputs together so they stay in sync. Changing these values after the Coding stage starts is expensive.
