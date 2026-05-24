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

- **Heading font:** IBM Plex Mono SemiBold (weight 600) — Google Fonts — Clean, refined monospace with genuine terminal character. Matches the logo mark exactly. Used for page titles, section headers, nav, and all display text.
- **Body font:** IBM Plex Mono Regular (weight 400) — Google Fonts — Same typeface at regular weight. Single-font system: consistent, no visual clash between heading and body.
- **Google Fonts import:** `IBM+Plex+Mono:wght@400;500;600;700`
- **Heading size:** 32px (H1), 24px (H2), 18px (H3)
- **Body size:** 14px
- **Small size:** 12px
- **Line height:** 1.6

## Shape & Spacing

- Border radius: 2px — nearly square, like old software UI chrome
- Base spacing unit: 8px
- Overall style: Dense, information-rich, minimal decoration. Every pixel earns its place.

## Logo Direction

Three directions explored, two chosen:

1. **Terminal Prompt / Primary Mark** ✅ CHOSEN — "TAXIDERMATT" in IBM Plex Mono SemiBold with a blinking phosphor cursor block. Clean, typographic, scalable to any size. The blinking cursor is the only animation in the entire brand.
2. **Mounted Receipt / Icon Mark** ✅ CHOSEN — Minimalist ram head silhouette with a receipt/printout element. The secondary icon mark — used as a favicon, app icon, and standalone symbol where the full wordmark doesn't fit.
3. **ASCII Badge** — Terminal window frame with the name inside. Not chosen.

Both chosen marks live in `assets/`. Primary mark: `Taxidermatt Logo.html`. Icon mark: `Taxidermatt Logo - Icon.html`.

## Do / Don't

| Do | Don't |
|----|-------|
| Use generous line spacing in tables for readability | Use more than 2 colours on a single screen |
| Phosphor green for numbers that matter (totals, amounts) | Round corners more than 4px anywhere |
| Monospace fonts everywhere — it's part of the identity | Use any font other than IBM Plex Mono |
| Dense information layout — respect the user's intelligence | Add gradients, shadows, or glow effects |
| ALL CAPS for labels and navigation items | Use icons without text labels |
| Dim Green for interactive elements on hover | Mix warm and cool tones — stay in the green spectrum |

## Inspiration References

- Classic VT100 / VT220 terminal interfaces
- Early 1980s accounting software (Lotus 1-2-3 era)
- The terminal scenes in War Games (1983)
- Fallout 3/4 Pip-Boy interface — terminal aesthetic done with restraint
