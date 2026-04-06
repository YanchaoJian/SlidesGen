# Design Specification: Dalian University of Technology Academic Blue

---

## I. Theme Overview

| Item | Value |
| ---- | ----- |
| **Theme Name** | Dalian University Academic Blue |
| **Design Tone Family** | corporate-traditional |
| **Atmosphere** | Formal academic presentation with institutional branding. Clean, structured layout suitable for university lectures, research presentations, and educational conferences. |
| **Tone Keywords** | academic, institutional, structured, professional, traditional |
| **Theme Mode** | Light |
| **Suitable Scenarios** | University lectures, academic conferences, research presentations, educational seminars, institutional reports |

---

## II. Color Scheme

| Role | HEX | Purpose |
| ---- | --- | ------- |
| **Background** | `#F5F5F5` | Page background (light gray) |
| **Secondary bg** | `#FFFFFF` | Card / section background |
| **Primary** | `#004B87` | Deep blue - title decorations, header elements, card fills |
| **Accent** | `#0066B3` | Medium blue - secondary emphasis, borders |
| **Secondary accent** | `#E8F0F7` | Light blue tint - subtle backgrounds |
| **Body text** | `#333333` | Main body text (dark gray) |
| **Secondary text** | `#666666` | Captions, annotations |
| **Tertiary text** | `#999999` | Supplementary info, footers, page numbers |
| **Border / divider** | `#D0D0D0` | Card borders, divider lines |
| **Success** | `#4CAF50` | Positive indicators (not visible but inferred) |
| **Warning** | `#F44336` | Issue markers (not visible but inferred) |

### Semantic Color Convention

| Semantic role | Assigned color | Where it appears |
| ------------- | ------------- | ---------------- |
| Brand emphasis | `#004B87` | Title bar, card headers, institutional branding, primary decorative elements |
| Recommended / success | `#4CAF50` | Positive data points, success indicators, recommended options |
| Process / informational | `#0066B3` | Secondary emphasis, borders, informational callouts |
| Risk / warning | `#F44336` | Negative indicators, warnings, critical information |
| Baseline / neutral | `#D0D0D0` | Gridlines, dividers, non-emphasized borders |

### Gradient Definitions (if applicable)

Primarily solid color fills, no gradients.

---

## III. Typography System

| Role | Ratio | Size (px) | Weight | Color Role |
| ---- | ----- | --------- | ------ | ---------- |
| Cover title | 3x | 66px | Bold | Primary |
| Section title | 2.2x | 48px | Bold | Primary |
| Subtitle | 1.5x | 33px | SemiBold | Body text |
| **Body** | **1x** | **22px** | Normal | Body text |
| Annotation | 0.8x | 18px | Normal | Secondary text |
| Page number | 0.6x | 13px | Normal | Tertiary text |

**Font stack**: `"Microsoft YaHei", "SimHei", "STHeiti", Arial, sans-serif`

---

## IV. Layout Principles

### Page Structure (1280×720 canvas)

| Zone | Y-range (px) | Height (px) | Description |
| ---- | ------------ | ----------- | ----------- |
| Header area | 0 – 100 | 100px | White background with blue decorative element and title, university logo top-right |
| Content area | 100 – 660 | 560px | Main content zone on light gray background |
| Footer area | 660 – 720 | 60px | Page number, date, institutional values text |

### Margins & Spacing

| Element | Value (px) |
| ------- | ---------- |
| Left / right margin | 60px |
| Top / bottom margin | 40px |
| **Grid base unit** | 20px |
| Card gap | 40px |
| Content block gap | 60px |
| Card padding | 40px |
| Card border radius | 0px (sharp corners with parallelogram shape) |

### Common Layout Modes

| Mode | Suitable Scenarios |
| ---- | ----------------- |
| Single column centered | Covers, conclusions, key statements |
| Three column cards | Feature lists, parallel concepts, structured content |
| Left-right split (5:5) | Comparisons, image+text |
| Top-bottom split | Timelines, processes |

---

## V. Page-Type Treatments

### 1. Cover Page

- Background: Light gradient `#F5F5F5` → `#FFFFFF`
- Decorative elements: Large blue parallelogram (skewed rectangle) on left side, university logo on top-right
- Title treatment: 66px bold, `#004B87`, left-aligned within blue parallelogram area
- Subtitle / date / source info: 22px normal weight, `#666666`, bottom-left area
- Accent decorative line: 3px horizontal line below title area, `#004B87`, full width

### 2. Chapter / Section Page

- Background: `#F5F5F5` solid
- Chapter number style: Large 120px bold numeric in `#004B87`, positioned top-left with 30% opacity
- Chapter title style: 48px bold, `#004B87`, centered vertically and horizontally
- Decorative line or divider: 3px horizontal line above and below title, `#0066B3`, 400px width centered

### 3. Content Page (the workhorse)

- Background: `#F5F5F5` solid
- Top decorative bar: Blue parallelogram element (40px height) with title text, `#004B87` fill
- Page-type label (if any): None visible
- Title position: y=30px within header parallelogram, 33px bold, `#FFFFFF`, left-aligned at x=60px
- Key-message / takeaway strip (if consulting-style): Not present in this design
- Default card layout for the content zone: Three-column parallelogram cards with `#004B87` to `#0066B3` gradient fills, white text, 40px horizontal gaps, centered in content area
- Footer: Page number right-aligned at x=1220px, y=690px, 13px `#999999`; institutional values left-aligned at x=60px, y=690px, 13px `#666666`

### 4. Ending / Closing Page

- Background: Mirrors cover with `#F5F5F5` → `#FFFFFF` gradient
- Thank-you message style: 48px bold, `#004B87`, centered
- Contact / CTA info: 22px normal, `#666666`, centered below thank-you message
- Decorative carryover from cover: Blue parallelogram element on right side (mirrored from cover), university logo maintained top-right

### 5. TOC / Agenda Page (optional — only if visible or strongly implied)

- Background: `#F5F5F5` solid
- Numbering style: Blue circles (30px diameter) with white numbers, `#004B87` fill
- Item layout: Left-aligned list with 40px vertical spacing, 22px body text, numbers at x=80px, text at x=140px

---

## VI. Visual Features

### Decorative Elements
- **Parallelogram cards**: Skewed rectangles (15-degree right slant) used for content containers, positioned throughout content area
- **Header parallelogram**: Left-aligned decorative shape in header area, `#004B87` fill, extends from left edge approximately 400px width
- **University logo**: Circular institutional seal, positioned top-right corner at approximately (1180, 30), 60px diameter
- **Horizontal divider**: 2px line below header area, `#D0D0D0`, full width

### Shadow Effects
- Parallelogram cards: `rgba(0, 0, 0, 0.1)`, offset-x: 4px, offset-y: 4px, blur: 12px
- No other shadow effects

### Border & Line Style
- Line thickness: 2-3px for dividers
- Color: `#D0D0D0` for neutral dividers, `#004B87` for emphasis lines
- Style: solid lines throughout
- Usage context: Header separation, card outlines (white stroke on parallelograms)

### Shape Style
- Geometric feel: Sharp parallelograms (skewed rectangles) with 15-degree right slant
- Overall roundedness: 0px radius - completely angular design
- Parallelogram dimensions: Approximately 360px width × 420px height for content cards

---

## VII. Component Patterns

### Content Cards
- Background: `#004B87` to `#0066B3` vertical gradient (darker at top)
- Border: 3px white stroke, 0px radius (parallelogram shape with 15-degree slant)
- Shadow: Yes - `rgba(0, 0, 0, 0.1)`, 4px offset-x, 4px offset-y, 12px blur
- **Card header strip**: Integrated into card top area, 60px height, same gradient as card body
- **Card header text**: 33px bold, `#FFFFFF`, centered horizontally within card
- **Card body padding**: 40px from all edges (accounting for parallelogram slant)

### Numbered Badges
- 30px diameter circle, `#004B87` fill, white bold text (18px), centered number
- Used for ordered lists and step indicators

### Info / Warning / Success Boxes
- **Info box**: `#E8F0F7` background, `#0066B3` text, 0px radius (rectangular)
- **Warning box**: `#FFEBEE` background, `#F44336` text, 0px radius
- **Success box**: `#E8F5E9` background, `#4CAF50` text, 0px radius
- Box height: Auto-fit content with 20px vertical padding
- Padding: 20px all sides
- Typical placement: Standalone below main content or within card body

### Title Treatment
- Page titles: Positioned within blue parallelogram header element, white text on blue background
- Subtitle style: 22px normal weight, `#666666`, positioned 20px below main title

### Data Emphasis
- Key numbers: 48px bold, `#004B87`, optionally within light blue `#E8F0F7` background badge with 10px padding
- Enlarged font with bold weight for emphasis
- No border on emphasis badges

### Icon Style (if visible)
- No icons visible - design uses geometric shapes (parallelograms) and text-based emphasis instead
- Decorative book/document icon in header (stylized parallelogram stack) in `#004B87`

---

## VIII. Design Quality Rules

- Content fill ratio: ~55%, moderate whitespace with structured layout
- Alignment: Strict grid-aligned, 20px base unit, left-aligned text within cards, centered card arrangement
- Color contrast: High contrast between white text on dark blue cards (WCAG AAA compliant), moderate contrast for body text on light background
- Data visualization rule: Monochromatic blue family for consistency, use depth through gradient rather than multiple hues
- Whitespace rhythm: Consistent 40-60px gaps between major elements, 20px internal padding
- Color restraint: Primary blue dominates (≤2 blue shades per page), accent colors used sparingly for semantic meaning only