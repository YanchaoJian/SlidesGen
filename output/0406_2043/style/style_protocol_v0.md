## I. Theme Overview

| Item | Value |
| ---- | ----- |
| **Theme Name** | DUT Academic Blue (Dalian University of Technology) |
| **Design Tone Family** | corporate-traditional |
| **Atmosphere** | Formal, institutional, and highly structured. Suitable for academic defenses, university reports, and formal corporate presentations. |
| **Tone Keywords** | Academic, geometric, navy-blue, structured, institutional |
| **Theme Mode** | **Mixed** (Light content pages with Dark/Solid-color cover and chapter pages) |
| **Suitable Scenarios** | University lectures, research proposals, administrative reports, formal institutional briefings. |

---

## II. Color Scheme

| Role | HEX | Purpose |
| ---- | --- | ------- |
| **Background** | `#FFFFFF` | Main page background |
| **Secondary bg** | `#F4F7FA` | Subtle section backgrounds or card hover states |
| **Primary** | `#003D7C` | DUT Brand Navy: Main titles, logo, footer text, and icon accents |
| **Accent** | `#0056A4` | Royal Blue: Content card fills, primary buttons |
| **Secondary accent** | `#0072CE` | Lighter blue for secondary highlights or gradients |
| **Body text** | `#333333` | Main body text on light backgrounds |
| **Secondary text** | `#FFFFFF` | Text inside blue content cards |
| **Tertiary text** | `#999999` | Footers, page numbers, and dates |
| **Border / divider** | `#003D7C` | Thin decorative lines and card outlines |
| **Success** | `#28A745` | Positive indicators (Standard green) |
| **Warning** | `#DC3545` | Risk/Issue markers (Standard red) |

### Semantic Color Convention

| Semantic role | Assigned color | Where it appears |
| ------------- | ------------- | ---------------- |
| Brand emphasis | `#003D7C` | Page titles, university logo, footer slogan |
| Recommended / success | `#0056A4` | Content cards (defaulting to brand blue as "standard") |
| Process / informational | `#0072CE` | Flow arrows, secondary callouts |
| Risk / warning | `#DC3545` | Negative data points or alerts |
| Baseline / neutral | `#E5E5E5` | Grid lines or background card shadows |

### Gradient Definitions

```xml
<!-- Card depth gradient -->
<linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" stop-color="#0056A4"/>
  <stop offset="100%" stop-color="#003D7C"/>
</linearGradient>
```

---

## III. Typography System

| Role | Ratio | Size (px) | Weight | Color Role |
| ---- | ----- | --------- | ------ | ---------- |
| Cover title | 2.8x | 56px | Bold | Primary / White |
| Section title | 2.2x | 44px | Bold | Primary |
| Subtitle (Card) | 1.6x | 32px | Bold | Secondary text (White) |
| **Body** | **1x** | **20px** | Normal | Secondary text / Body text |
| Annotation | 0.8x | 16px | Normal | Tertiary text |
| Page number | 0.7x | 14px | Normal | Tertiary text |

**Font stack**: `"Microsoft YaHei", "SimHei", Arial, sans-serif`

---

## IV. Layout Principles

### Page Structure (1280×720 canvas)

| Zone | Y-range (px) | Height (px) | Description |
| ---- | ------------ | ----------- | ----------- |
| Header area | 0 – 100 | 100px | Logo (top right), Title + Icon (top left) |
| Content area | 100 – 640 | 540px | Main content zone for cards/charts |
| Footer area | 640 – 720 | 80px | Slogan (bottom left), Date (bottom right) |

### Margins & Spacing

| Element | Value (px) |
| ------- | ---------- |
| Left / right margin | 60px |
| Top / bottom margin | 40px |
| **Grid base unit** | 20px |
| Card gap | 40px |
| Content block gap | 20px |
| Card padding | 30px |
| Card border radius | 0px (Uses sharp-edged parallelograms) |

---

## V. Page-Type Treatments

### 1. Cover Page
- **Background**: Solid `#003D7C` (Navy) or a subtle geometric pattern of DUT architecture.
- **Decorative elements**: Large white DUT logo at 10% opacity in the background.
- **Title treatment**: Centered, 56px, Bold, White.
- **Subtitle**: 24px, White, 80% opacity, positioned 40px below title.

### 2. Chapter / Section Page
- **Background**: White background with a large `#0056A4` parallelogram in the center.
- **Chapter number**: "01", 80px, Bold, White, inside the parallelogram.
- **Chapter title**: 44px, Bold, Primary Blue, positioned below the shape.

### 3. Content Page (The workhorse)
- **Background**: White (`#FFFFFF`).
- **Top decorative bar**: A thin 2px horizontal line in `#003D7C` spanning the width at y=100.
- **Title position**: y=50, Left-aligned, 44px, Primary Blue.
- **Title Icon**: A small blue parallelogram icon (skewed rectangle) to the left of the title.
- **Content zone**: Three-column layout using skewed parallelograms (skew angle: -15 degrees).
- **Footer**: Slogan "团结、进取、求实、创新" at bottom-left; Date at bottom-right.

### 4. Ending / Closing Page
- **Background**: Mirrors the Cover Page (`#003D7C`).
- **Thank-you message**: "感谢您的聆听" (Thank you for listening), 48px, White, Centered.
- **Contact info**: Website or Department name at y=600, 18px, White.

---

## VI. Visual Features

### Decorative Elements
- **Parallelogram Icon**: A small blue skewed rectangle (approx 40x40px) placed to the left of every page title.
- **Skewed Cards**: Main content containers are parallelograms (rectangles skewed on the X-axis by approx -15 to -20 degrees).

### Shadow Effects
- **Card Shadow**: `drop-shadow(0px 10px 20px rgba(0, 61, 124, 0.15))` - subtle blue-tinted shadow for depth.

### Border & Line Style
- **Dividers**: 1px solid `#003D7C` lines used to separate header/footer from content.
- **Card Outlines**: 1px solid `#0056A4` for empty or "ghost" cards.

### Shape Style
- **Geometric feel**: Sharp, non-rounded corners. Heavy use of 15-degree slants to create a sense of forward motion.

---

## VII. Component Patterns

### Content Cards (Parallelograms)
- **Background**: Solid `#0056A4` (Royal Blue).
- **Shape**: Skewed rectangle (CSS: `transform: skewX(-15deg)`).
- **Text**: All text inside is white, centered, and "un-skewed" (counter-rotated) to remain legible.
- **Card Body Padding**: 40px.

### Numbered Badges
- **Style**: White bold numbers placed at the top-center of the blue cards.

### Title Treatment
- **Page Title**: Left-aligned, preceded by a blue parallelogram icon.
- **Card Title**: 32px, Bold, White, centered within the top third of the card.

---

## VIII. Design Quality Rules

- **Content fill ratio**: ~70% content, 30% whitespace.
- **Alignment**: Strict grid alignment. Titles must align with the left margin of the first content card.
- **Color restraint**: Maximum 2 shades of blue + white + gray. No vibrant secondary colors unless for semantic warnings.
- **Visual Rhythm**: The "skew" angle must be consistent across all pages (e.g., always -15 degrees).
- **Institutional Branding**: The DUT logo must appear on every page (top right on content pages, centered on cover).