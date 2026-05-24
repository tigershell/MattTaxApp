# Design Brief — Taxidermatt

## Brand Personality
Taxidermatt looks like it was built in 1987 and has been running perfectly ever since. It draws on the aesthetic of classic phosphor-green CRT terminals — the kind used in early accounting departments and developer workstations — but applies it to a modern, fully functional web interface. The feel is serious, a little dry, and quietly confident. It doesn't try to be pretty; it tries to be exactly right. The name is self-aware and the design matches: a personal tool that takes the work seriously without taking itself too seriously.

## Target Audience
Matt — a developer in Adelaide who knows what a terminal looks like and appreciates the reference. Desktop browser, used at a desk, in focused sessions. Not a casual user. Expects the interface to be dense and information-rich, not hand-holdy. Consumer-polished is the wrong goal here — developer-elegant is the right one.

## Colour Palette

| Role | Name | Hex | Usage |
|------|------|-----|-------|
| Primary | Phosphor | #00FF41 | Buttons, active states, headings, key data |
| Secondary | Dim Green | #00B32A | Accents, secondary actions, highlights |
| Background | Void | #0A0F0A | Main app surface |
| Text | Screen Glow | #C8ECC8 | Body copy, table data, labels |
| Muted | Faded Signal | #4A7A52 | Captions, placeholders, secondary text |
| White / Cards | Dark Panel | #121912 | Cards, panels, raised surfaces |
| Border | Grid Line | #1E3D22 | Dividers, input borders, table lines |

**Contrast notes:** Phosphor (#00FF41) on Void (#0A0F0A) is extremely high contrast — use for headings and key values. Screen Glow (#C8ECC8) on Void is softer but still highly readable — use for body text and dense table data to reduce eye strain.

## Typography

- **Heading font:** VT323 — Google Fonts — The authentic old CRT terminal display font. At 32px+ it looks exactly like a phosphor screen. Used for page titles, section headers, vendor names, and any display text.
- **Body font:** Share Tech Mono — Google Fonts — A cleaner monospace that keeps the terminal character but is genuinely readable at 14px across dense tables and reports.
- **Heading size:** 32px (H1), 24px (H2), 18px (H3)
- **Body size:** 14px
- **Small size:** 12px
- **Line height:** 1.6

## Shape & Spacing

- Border radius: 2px — nearly square, like old software UI chrome
- Base spacing unit: 8px
- Overall style: Dense, information-rich, minimal decoration. Every pixel earns its place.

## Logo Direction

Three directions explored:

1. **Terminal Prompt** — "TAXIDERMATT>" with a blinking cursor block. The app name as a command being entered. Simple, instantly recognisable to anyone who's used a terminal.
2. **Mounted Receipt** — A minimalist mounted animal head silhouette with a receipt/printout coming from its mouth. Plays on the taxidermy pun literally.
3. **ASCII Badge** — The name set in a bordered terminal window frame, like a classic software splash screen. Clean, typographic, scalable.

## Do / Don't

| Do | Don't |
|----|-------|
| Use generous line spacing in tables for readability | Use more than 2 colours on a single screen |
| Phosphor green for numbers that matter (totals, amounts) | Round corners more than 4px anywhere |
| Monospace fonts everywhere — it's part of the identity | Use any font other than VT323 or Share Tech Mono |
| Dense information layout — respect the user's intelligence | Add gradients, shadows, or glow effects |
| ALL CAPS for labels and navigation items | Use icons without text labels |
| Dim Green for interactive elements on hover | Mix warm and cool tones — stay in the green spectrum |

## Inspiration References

- Classic VT100 / VT220 terminal interfaces
- Early 1980s accounting software (Lotus 1-2-3 era)
- The terminal scenes in War Games (1983)
- Fallout 3/4 Pip-Boy interface — terminal aesthetic done with restraint
