## I. Theme Overview

| Item | Value |
| ---- | ----- |
| **Theme Name** | Dalian University Tech Blue |
| **Design Tone Family** | corporate-traditional |
| **Atmosphere** | Professional, academic, and institutional with restrained elegance; suitable for university presentations, research summaries, or formal departmental reports. |
| **Tone Keywords** | academic, structured, institutional, clean, authoritative |
| **Theme Mode** | Light (white background) |
| **Suitable Scenarios** | University lectures, academic research presentations, departmental reports, student project defenses |

---

## II. Color Scheme

> Extract ALL visually distinct colors. Group by role.

| Role | HEX | Purpose |
| ---- | --- | ------- |
| **Background** | `#FFFFFF` | Page background |
| **Secondary bg** | `#F8FAFC` | Card / section background (light gray overlay) |
| **Primary** | `#1E3A8A` | Title decorations, header bar, key sections |
| **Accent** | `#1E3A8A` | Data highlights, key numbers, links — same as primary due to institutional branding |
| **Secondary accent** | `#E2E8F0` | Secondary emphasis, gradient end color |
| **Body text** | `#1E3A8A` | Main body text — matches primary for consistency |
| **Secondary text** | `#64748B` | Captions, annotations |
| **Tertiary text** | `#94A3B8` | Supplementary info, footers, page numbers |
| **Border / divider** | `#1E3A8A` | Card borders, divider lines — same as primary |
| **Success** | `#10B981` | Positive indicators (green family) — not used in reference |
| **Warning** | `#EF4444` | Issue markers (red family) — not used in reference |

### Semantic Color Convention

| Semantic role | Assigned color | Where it appears |
| ------------- | ------------- | ---------------- |
| Brand emphasis | `#1E3A8A` | Title bars, card headers, chapter numbers |
| Recommended / success | `#10B981` | Not used in reference — reserved for future positive indicators |
| Process / informational | `#3B82F6` | Not used in reference — reserved for flow lines or neutral cards |
| Risk / warning | `#EF4444` | Not used in reference — reserved for negative callouts |
| Baseline / neutral | `#E2E8F0` | Card borders, gridlines, non-target data series |

### Gradient Definitions (if applicable)

Primarily solid color fills, no gradients.

---

## III. Typography System

| Role | Ratio | Size (px) | Weight | Color Role |
| ---- | ----- | --------- | ------ | ---------- |
| Cover title | 2.5-3x | 60px | Bold | Primary / Light text |
| Section title | 1.8-2.2x | 36px | Bold | Primary / Body text |
| Subtitle | 1.2-1.5x | 24px | SemiBold | Body text |
| **Body** | **1x** | **18px** | Normal | Body text |
| Annotation | 0.7-0.85x | 14px | Normal | Secondary text |
| Page number | 0.55-0.65x | 12px | Normal | Tertiary text |

**Font stack**: `"Microsoft YaHei, 'SimSun', sans-serif"`

---

## IV. Layout Principles

### Page Structure (1280×720 canvas)

| Zone | Y-range (px) | Height (px) | Description |
| ---- | ------------ | ----------- | ----------- |
| Header area | 0 – 100 | 100px | White background with blue title bar and university logo |
| Content area | 100 – 580 | 480px | Main content zone with three-column cards |
| Footer area | 580 – 720 | 140px | Contains slogan and date in bottom corners |

### Margins & Spacing

| Element | Value (px) |
| ------- | ---------- |
| Left / right margin | 40px |
| Top / bottom margin | 40px |
| **Grid base unit** | 20px |
| Card gap | 40px |
| Content block gap | 20px |
| Card padding | 20px |
| Card border radius | 12px |

> All other spacing values should be whole multiples of the grid base unit.

### Common Layout Modes

| Mode | Suitable Scenarios |
| ---- | ----------------- |
| Single column centered | Covers, conclusions, key statements |
| Left-right split (5:5 or 4:6) | Image+text, comparisons |
| Three/four column cards | Feature lists, team intros |
| Top-bottom split | Timelines, processes |

---

## V. Page-Type Treatments

### 1. Cover Page

- Background: `#FFFFFF`
- Decorative elements: None visible — minimalistic design
- Title treatment: Font size 60px, bold, centered, color `#1E3A8A`, aligned at y=60px
- Subtitle / date / source info: Positioned at bottom left, font size 18px, color `#64748B`
- Accent decorative line: Thin horizontal line under title, color `#1E3A8A`, thickness 2px

### 2. Chapter / Section Page

- Background: `#FFFFFF`
- Chapter number style: Large numeric, color `#1E3A8A`, font size 36px, centered
- Chapter title style: Font size 36px, bold, centered below chapter number
- Decorative line or divider: Thin horizontal line under title, color `#1E3A8A`, thickness 2px

### 3. Content Page (the workhorse)

- Background: `#FFFFFF`
- Top decorative bar: 6px height, color `#1E3A8A`
- Page-type label (if any): Not present
- Title position: y=100px, font size 36px, bold, centered
- Key-message / takeaway strip (if consulting-style): Not present
- Default card layout for the content zone: Three-column cards with white borders and blue headers
- Footer: Page number positioned at bottom right, font size 12px, color `#94A3B8`

### 4. Ending / Closing Page

- Background: `#FFFFFF`
- Thank-you message style: Centered, font size 36px, color `#1E3A8A`
- Contact / CTA info: Not present
- Decorative carryover from cover: None — minimalist design

### 5. TOC / Agenda Page (optional — only if visible or strongly implied)

- Background: `#FFFFFF`
- Numbering style: Large numeric, color `#1E3A8A`, font size 36px
- Item layout: Left-aligned, each item separated by 40px vertical spacing

---

## VI. Visual Features

### Decorative Elements
- None visible — minimalistic design

### Shadow Effects
- No shadow effects

### Border & Line Style
- Line thickness: 1px
- Line color: `#1E3A8A`
- Line style: Solid
- Usage context: Card borders, divider lines

### Shape Style
- Geometric feel: Sharp rectangles with rounded corners (radius 12px)

---

## VII. Component Patterns

### Content Cards
- Background: `#FFFFFF`
- Border: `#1E3A8A`, width 1px, radius 12px
- Shadow: No
- **Card header strip**: Height 55px, color `#1E3A8A`, corner radius 12px
- **Card header text**: Font size 24px, bold, color `#FFFFFF`
- **Card body padding**: 20px internal padding from card edges

### Numbered Badges
- Not used — no numbered badges visible

### Info / Warning / Success Boxes
- **Info box**: Not used — no info boxes visible
- **Warning box**: Not used — no warning boxes visible
- **Success box**: Not used — no success boxes visible
- Box height, padding, typical placement: Not applicable

### Title Treatment
- How page titles are styled: Centered title with top accent bar (`#1E3A8A`)
- Subtitle style: Smaller text below title, secondary text color (`#64748B`)

### Data Emphasis
- How key numbers / data points are highlighted: Not applicable — no data points visible

### Icon Style (if visible)
- Not used — no icons visible

---

## VIII. Design Quality Rules

- Content fill ratio: ~60%, generous whitespace
- Alignment: Grid-aligned, alignment base unit 20px
- Color contrast: High contrast between blue headers and white background
- Data visualization rule: Not applicable — no data visualization visible
- Whitespace rhythm: Consistent spacing between cards (40px gap)
- Color restraint: ≤3 colors per page, accent used ≤3 times globally