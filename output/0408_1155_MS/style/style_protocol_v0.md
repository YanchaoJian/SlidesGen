## I. Theme Overview

| Item | Value |
| ---- | ----- |
| **Theme Name** | Dalian University of Technology Academic Blue |
| **Design Tone Family** | corporate-traditional |
| **Atmosphere** | Formal academic presentation with institutional gravitas. Clean, structured, and authoritative with subtle Chinese calligraphic elements conveying tradition and scholarly heritage. |
| **Tone Keywords** | academic, institutional, structured, authoritative, traditional |
| **Theme Mode** | Light |
| **Suitable Scenarios** | University lectures, academic conferences, research presentations, thesis defenses, institutional reports, educational training materials |

---

## II. Color Scheme

| Role | HEX | Purpose |
| ---- | --- | ------- |
| **Background** | `#F8F9FA` | Page background (very light warm gray, almost white) |
| **Secondary bg** | `#0A3D8F` | Card backgrounds, header elements (deep institutional blue) |
| **Primary** | `#0A3D8F` | Title decorations, header bar, institutional branding |
| **Accent** | `#0A3D8F` | Data highlights, key sections (same as primary — monochromatic) |
| **Secondary accent** | `#1E5AA8` | Lighter blue for hover states or secondary emphasis |
| **Body text** | `#1A1A1A` | Main body text on light backgrounds |
| **Secondary text** | `#4A5568` | Captions, annotations, muted text |
| **Tertiary text** | `#718096` | Supplementary info, footers, page numbers |
| **Border / divider** | `#0A3D8F` | Card borders, divider lines (blue) |
| **Success** | `#2E7D32` | Positive indicators (green family — inferred) |
| **Warning** | `#C62828` | Issue markers (red family — inferred) |

### Semantic Color Convention

| Semantic role | Assigned color | Where it appears |
| ------------- | ------------- | ---------------- |
| Brand emphasis | `#0A3D8F` | Page titles, card headers, institutional branding, top decorative line |
| Recommended / success | `#2E7D32` | Positive indicators, "best practice" callouts (inferred, not visible) |
| Process / informational | `#1E5AA8` | Secondary blue for layered information, links |
| Risk / warning | `#C62828` | Issue markers, critical notes (inferred, not visible) |
| Baseline / neutral | `#718096` | Footer text, page numbers, supplementary information |

### Gradient Definitions

Primarily solid color fills, no gradients. The design uses flat, authoritative color blocks with sharp edges.

---

## III. Typography System

| Role | Ratio | Size (px) | Weight | Color Role |
| ---- | ----- | --------- | ------ | ---------- |
| Cover title | 2.5x | 56px | Bold | Primary |
| Section title | 2.0x | 44px | Bold | Primary |
| Subtitle | 1.4x | 32px | Bold | Light text on dark bg |
| **Body** | **1x** | **22px** | Normal | Body text |
| Annotation | 0.75x | 16px | Normal | Secondary text |
| Page number | 0.6x | 14px | Normal | Tertiary text |

**Font stack**: `"Microsoft YaHei", "PingFang SC", "Hiragino Sans GB", "Noto Sans CJK SC", sans-serif`

**Special typography**: Calligraphic Chinese characters for institutional motto in footer — brush-style script, black ink color `#1A1A1A`

---

## IV. Layout Principles

### Page Structure (1280×720 canvas)

| Zone | Y-range (px) | Height (px) | Description |
| ---- | ------------ | ----------- | ----------- |
| Header area | 0 – 100 | 100px | Title bar with book icon, main title, institutional logo, bottom blue divider line |
| Content area | 100 – 620 | 520px | Three-column card layout with angled parallelogram cards |
| Footer area | 620 – 720 | 100px | Institutional motto (calligraphic left), date (right), generous whitespace |

### Margins & Spacing

| Element | Value (px) |
| ------- | ---------- |
| Left / right margin | 60px |
| Top / bottom margin | 40px |
| **Grid base unit** | 20px |
| Card gap | 40px |
| Content block gap | 40px |
| Card padding | 30px (internal text padding from card edges) |
| Card border radius | 0px (sharp corners, parallelogram geometry) |

### Common Layout Modes

| Mode | Suitable Scenarios |
| ---- | ----------------- |
| Single column centered | Covers, conclusions, key statements |
| Three-column angled cards | Feature lists, comparison points, parallel concepts (primary pattern in reference) |
| Left-right split | Image+text, comparisons |
| Top-bottom split | Timelines, processes |

---

## V. Page-Type Treatments

### 1. Cover Page

- Background: Solid `#F8F9FA` with subtle texture possible
- Decorative elements: Large institutional blue `#0A3D8F` geometric shape (parallelogram or rectangle) on left or right as visual anchor; book icon motif
- Title treatment: 56px Bold, `#0A3D8F`, left-aligned or centered with institutional logo
- Subtitle / date / source info: 22px Normal, `#4A5568`, positioned below title with 20px gap
- Accent decorative line: 3px solid `#0A3D8F` horizontal line, full width or partial, positioned below header content

### 2. Chapter / Section Page

- Background: Solid `#0A3D8F` (full bleed institutional blue) or `#F8F9FA` with large blue geometric block
- Chapter number style: 72px Bold, white or `#0A3D8F` depending on background, positioned upper left or centered
- Chapter title style: 44px Bold, white on blue background or `#0A3D8F` on light background, left-aligned
- Decorative line or divider: 3px white or blue horizontal line, 60% width, centered or left-aligned below title

### 3. Content Page (the workhorse)

- Background: `#F8F9FA`
- Top decorative bar: 3px solid `#0A3D8F` horizontal line at y=100px, spanning full width minus margins
- Page-type label: None visible — clean title-only approach
- Title position: y=40px, 44px Bold, `#0A3D8F`, left-aligned with book icon prefix (40×40px icon at left)
- Key-message / takeaway strip: Not present in this design — information delivered through structured cards
- Default card layout: Three parallelogram cards with 15° slant angle, equal width, 40px gaps, blue `#0A3D8F` fill, white text
- Footer: Institutional motto in calligraphic script at bottom left (y=660px), date at bottom right, both 16px

### 4. Ending / Closing Page

- Background: Mirrors cover — `#F8F9FA` with large `#0A3D8F` geometric element
- Thank-you message style: 56px Bold, `#0A3D8F`, centered
- Contact / CTA info: 22px Normal, `#4A5568`, below thank-you with 30px gap
- Decorative carryover from cover: Book icon, blue accent line, institutional logo

### 5. TOC / Agenda Page

- Background: `#F8F9FA`
- Numbering style: Large `#0A3D8F` numerals (36px Bold) in left margin, content titles to the right
- Item layout: Horizontal blue divider lines between items, 20px vertical spacing, alternating subtle background tints possible

---

## VI. Visual Features

### Decorative Elements
- **Book icon**: 50×50px stylized open book in `#0A3D8F`, positioned at title left, consistent header element
- **Parallelogram cards**: Three main content cards with 15° slant (shear transformation), creating dynamic but controlled geometry
- **Card shadow/outline**: Each blue card has a subtle offset white/light outline or shadow shape behind it, creating depth through layered geometry
- **Top divider line**: 3px solid `#0A3D8F`, full width, positioned at y=100px
- **Institutional logo**: Circular seal + bilingual text in upper right corner, 80px height

### Shadow Effects
No shadow effects. Depth created through:
- Layered geometric shapes (white parallelogram behind blue parallelogram, offset 8px right and down)
- Solid color contrast, not transparency

### Border & Line Style
- Line thickness: 3px for major dividers, 2px for card outlines
- Color: `#0A3D8F` for all lines
- Style: Solid only

### Shape Style
- **Geometric feel**: Sharp angles, parallelograms, rectangles
- **Roundedness**: 0px — completely sharp corners throughout
- **Overall aesthetic**: Precise, technical, architectural

---

## VII. Component Patterns

### Content Cards
- Background: `#0A3D8F`
- Border: 2px solid `#0A3D8F` (self-border, or white outline variant)
- Shadow: No blur shadow — instead, white/light parallelogram shape layered behind at +8px x-offset, +8px y-offset
- **Card header strip**: Integrated into card — top 80px of card contains centered title
- **Card header text**: 32px Bold, white, centered
- **Card body padding**: 30px from left edge (accounting for slant), 40px from right

### Numbered Badges
Not visible in reference. If needed: 24px diameter circle, `#0A3D8F` fill, white Bold text, positioned at list item left.

### Info / Warning / Success Boxes
- **Info box**: Background `#E3F2FD`, border 2px `#1E5AA8`, text `#0A3D8F`, sharp corners
- **Warning box**: Background `#FFEBEE`, border 2px `#C62828`, text `#C62828`, sharp corners
- **Success box**: Background `#E8F5E9`, border 2px `#2E7D32`, text `#2E7D32`, sharp corners
- Box padding: 20px, full width or inset within content area

### Title Treatment
- Book icon (50×50px) + main title (44px Bold) combination
- 3px blue underline spanning content width
- Left-aligned, authoritative positioning

### Data Emphasis
- Key numbers: 32px Bold white on blue card background
- Section headers: 32px Bold white, centered in card top
- No additional highlighting needed — card structure provides emphasis

### Icon Style
- **Primary icon**: Stylized open book, geometric line art, `#0A3D8F`
- **Institutional logo**: Circular seal with internal detail, blue and white
- **No other icons** — use geometric shapes and colored cards for visual interest

---

## VIII. Design Quality Rules

- **Content fill ratio**: ~55%, generous whitespace with structured content zones
- **Alignment**: Strict grid-aligned, 20px base unit, all elements on grid
- **Color contrast**: High contrast between `#0A3D8F` cards and white text; sufficient contrast for accessibility
- **Data visualization rule**: Monochromatic blue family for institutional consistency; use value/tint variation for data series, not hue variation
- **Whitespace rhythm**: Consistent 40px gaps between major elements, 20px internal spacing
- **Color restraint**: ≤2 colors per page (institutional blue + neutrals), accent used consistently for all emphasis
- **Typography restraint**: Maximum 3 sizes per page, Bold for all headings, Normal for body
- **Geometric discipline**: All angles at 0° or 15° (parallelogram slant), no arbitrary rotations