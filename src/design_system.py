"""
Design System — Taxidermatt
Terminal / phosphor-green aesthetic. Import this wherever UI values are needed.
For Flask: register these as template globals in create_app() so Jinja templates
can reference them directly, or use them to generate a CSS :root block.
Update here to change the look across the entire app.
"""

# ── Colours ──────────────────────────────────────────────────────────────────
PRIMARY        = "#00FF41"   # Phosphor     — buttons, active states, key amounts, headings
SECONDARY      = "#00B32A"   # Dim Green    — accents, secondary actions, hover states
BACKGROUND     = "#0A0F0A"   # Void         — main app surface
TEXT           = "#C8ECC8"   # Screen Glow  — body copy, table data, labels
TEXT_MUTED     = "#4A7A52"   # Faded Signal — captions, placeholders, secondary text
SURFACE        = "#121912"   # Dark Panel   — cards, panels, raised surfaces
BORDER         = "#1E3D22"   # Grid Line    — dividers, input borders, table lines

# ── Typography ────────────────────────────────────────────────────────────────
FONT_HEADING   = "VT323"           # Google Fonts — authentic CRT terminal display font
FONT_BODY      = "Share Tech Mono" # Google Fonts — clean readable monospace

FONT_SIZE_H1   = 32          # px — page titles
FONT_SIZE_H2   = 24          # px — section headers
FONT_SIZE_H3   = 18          # px — card titles, vendor names
FONT_SIZE_BODY = 14          # px — table data, body copy
FONT_SIZE_SMALL = 12         # px — captions, status labels, hints

# ── Spacing ───────────────────────────────────────────────────────────────────
SPACING_XS     = 4           # px — tight gaps between related elements
SPACING_SM     = 8           # px — padding inside small components
SPACING_MD     = 16          # px — standard component padding
SPACING_LG     = 24          # px — section gaps
SPACING_XL     = 40          # px — major layout gaps

# ── Shape ─────────────────────────────────────────────────────────────────────
BORDER_RADIUS  = 2           # px — nearly square corners, old-software feel
BORDER_WIDTH   = 1           # px — borders on inputs, cards, table lines

# ── CSS :root block (paste into base.html <style> or a .css file) ─────────────
CSS_VARIABLES = f"""
:root {{
  --primary:    {PRIMARY};
  --secondary:  {SECONDARY};
  --bg:         {BACKGROUND};
  --text:       {TEXT};
  --muted:      {TEXT_MUTED};
  --surface:    {SURFACE};
  --border:     {BORDER};
  --radius:     {BORDER_RADIUS}px;
  --font-heading: '{FONT_HEADING}', monospace;
  --font-body:    '{FONT_BODY}', monospace;
}}
"""
