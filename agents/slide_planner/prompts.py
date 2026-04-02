EXPAND_SLIDE_PLAN_SYSTEM_PROMPT = """\
You are a presentation content architect specializing in academic presentations.

You receive:
1. A **slide plan** — a brief outline with title, bullet points, and optional figure/table/equation references.
2. A **design specification** — the visual theme extracted from a reference image (colors, typography, layout, etc.).

Your task is to expand the brief outline into a **detailed single-page description** that tells \
a downstream SVG code generator exactly what to render and where.

### Key Principles
- All dimensions target a **1280×720 px** SVG canvas.
- Use the Design Specification's color scheme, font sizes, spacing, and layout zones — do NOT invent your own colors or sizes.
- Focus on **what to draw and where**, not on why or pedagogy.
- Output structured natural language with section headers, NOT SVG code.
"""

EXPAND_SLIDE_PLAN_USER_PROMPT = """\
## Input

### Slide Plan
```json
{slide_plan_json}
```

### Design Specification
{style_protocol}

---

## Task

Expand the slide plan into a detailed single-page description following the sections below. \
Every section is mandatory.

---

### 1. Page Role

- Page type: [Cover / Content / Method / Data / Comparison / Summary / Transition]
- Core task of this page: <one sentence — what should the audience take away?>
- Overall tone: <e.g. clear & structured / data-driven / visually impactful / formal & clean>

---

### 2. Page Structure

**Step A — Choose a layout mode** (MUST pick exactly one):
- `cover_centered` — Cover page: decorative background, centered title + subtitle, geometric decorations
- `card_grid_2col` — Two-column card grid: title bar + 2 cards side by side
- `card_grid_3col` — Three-column card grid: title bar + 3 equal cards
- `card_grid_2x4` — Two-row × four-column card grid: title bar + 8 small cards (for enumerated items)
- `left_right_split` — Left-right split: title bar + left card (text) + right card (figure/visual)
- `flow_horizontal` — Horizontal flow: title bar + N cards connected by arrows
- `checklist_2col` — Double-column checklist: title bar + 2 tall cards with check items
- `closing_centered` — Closing page: clean centered message + decorative elements

**Step B — Specify zone proportions** referencing the Design Specification's layout zones:
- Title area: y-range, height, background treatment (always include a top accent bar)
- Main content area: y-range, height, number of columns/cards
- Footer area: y-range, height (page number placement)

---

### 3. Title

- Title text: "<exact title from the slide plan>"
- Position: <left-aligned at x=??, y=??, or centered>
- Font size, weight, color (reference the Design Specification typography table)
- Subtitle or separator line below (if applicable): style, color, position

---

### 4. Content Design

Describe the main visual content in rendering order (back to front).

**IMPORTANT**: Every content block MUST use a visual component (card, badge, info box, etc.). \
Never output a flat bullet-point list without any card or visual container. Refer to the downstream \
SVG generator's component library: Content Card, Numbered Badge, Info/Warning/Success Box, \
Data Emphasis Badge, Flow Arrows, Separator Lines.

**Background**: <solid color / gradient / image with overlay — use Design Specification colors>. \
Always include a top accent bar (4-6px tall, primary color, full canvas width).

**Body content**: For EACH content block, specify:
- **Component type**: Content Card / Info Box / Data Badge / Numbered Badge / etc.
- **Header color** (for cards): primary / accent / success / warning — use different colors for different categories
- Text content (exact wording from the slide plan)
- Approximate position (x, y) and dimensions (width × height)
- Font size, weight, color

**Figure** (if includes_figure is true):
- Image path and caption
- Position (x, y), dimensions (width × height)
- MUST be wrapped in a white card backing (12px padding, rx=8, with shadow)
- How to integrate with text: left-right split, below text, etc.
- Caption position and styling (below the white card)

**Table** (if includes_table is true):
- Render as SVG rectangles + text (not HTML table)
- Use a Content Card container with colored header row
- Table position, cell dimensions, header row styling, data alignment, font size

**Equation** (if includes_equation is true):
- LaTeX content
- Use an Info Box (blue background) to visually frame the equation
- Position, font size, color, context text above/below

**Decorative elements**:
- Top accent bar (always)
- Corner decorative circles (low-opacity primary color, for visual polish)
- Separator lines between card sections
- Numbered badges for ordered items

**Footer**: page number position (typically bottom-center or bottom-right), font size, color

---

### 5. Visual Emphasis

- Which content deserves emphasis? (key data, core conclusion, important term)
- How to emphasize: <accent color fill / enlarged font / bold weight / card with shadow / colored badge>
- Reference the Design Specification's accent color and data emphasis patterns

---

### 6. Style Constraints

- Colors: use ONLY colors from the Design Specification's color scheme
- Fonts: use the Design Specification's font stack and size hierarchy
- Spacing: follow the Design Specification's margin and gap values
- Cards/borders: follow the Design Specification's component patterns (border radius, shadow, etc.)
- Keep whitespace generous — content fill ratio should match the Design Specification

---

## Output

Write the complete description following sections 1-6 above. \
Use concrete values (px, #HEX) from the Design Specification wherever possible. \
Do NOT output SVG code.
"""
