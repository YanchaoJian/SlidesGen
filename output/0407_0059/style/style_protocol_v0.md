## I. Theme Overview

| Item | Value |
| ---- | ----- |
| **Theme Name** | DUT Academic Blue (Dalian University of Technology) |
| **Design Tone Family** | corporate-traditional |
| **Atmosphere** | Formal, institutional, and structured. Suitable for academic reports, university briefings, and official administrative presentations. |
| **Tone Keywords** | academic, geometric, slanted, professional |
| **Theme Mode** | Light (White background with heavy primary blue accents) |
| **Suitable Scenarios** | University lectures, research defenses, institutional annual reports, academic conferences. |

---

## II. Color Scheme

| Role | HEX | Purpose |
| ---- | --- | ------- |
| **Background** | `#FFFFFF` | Main page background |
| **Secondary bg** | `#F4F7FA` | Subtle section backgrounds or card hover states |
| **Primary** | `#003D7C` | DUT Brand Blue: Header icons, card fills, main titles |
| **Accent** | `#1D4E89` | Lighter blue for gradients or secondary emphasis |
| **Secondary accent** | `#A0B4CC` | Light blue-gray used for the "shadow" decorative parallelograms |
| **Body text** | `#333333` | Main content text |
| **Secondary text** | `#666666` | Subtitles and labels |
| **Tertiary text** | `#999999` | Footer motto, date, and page numbers |
| **Border / divider** | `#003D7C` | Thin decorative lines in header/footer |
| **Success** | `#28A745` | Positive indicators (inferred) |
| **Warning** | `#DC3545` | Risk/Warning markers (inferred) |

### Semantic Color Convention

| Semantic role | Assigned color | Where it appears |
| ------------- | ------------- | ---------------- |
| Brand emphasis | `#003D7C` | Page titles, primary card fills, university logo |
| Recommended / success | `#28A745` | Positive data points, "Approved" status |
| Process / informational | `#A0B4CC` | Decorative background shapes, secondary steps |
| Risk / warning | `#DC3545` | Negative data points, "Alert" callouts |
| Baseline / neutral | `#E5E5E5` | Grid lines, inactive card borders |

### Gradient Definitions

```xml
<!-- Primary Slanted Card Gradient -->
<linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" stop-color="#003D7C"/>
  <stop offset="100%" stop-color="#1D4E89"/>
</linearGradient>
```

---

## III. Typography System

| Role | Ratio | Size (px) | Weight | Color Role |
| ---- | ----- | --------- | ------ | ---------- |
| Cover title | 3.0x | 60px | Bold | Primary |
| Section title | 2.0x | 40px | Bold | Primary |
| Subtitle | 1.4x | 28px | SemiBold | Body text |
| **Body** | **1x** | **20px** | Normal | Body text |
| Annotation | 0.8x | 16px | Normal | Secondary text |
| Page number | 0.6x | 12px | Normal | Tertiary text |

**Font stack**: `"Microsoft YaHei", "SimHei", "Arial", sans-serif`

---

## IV. Layout Principles

### Page Structure (1280×720 canvas)

| Zone | Y-range (px) | Height (px) | Description |
| ---- | ------------ | ----------- | ----------- |
| Header area | 0 – 100 | 100px | Contains slanted logo icon (left), Title (left), and University Logo (right) |
| Content area | 100 – 640 | 540px | Main content zone for cards, charts, or text |
| Footer area | 640 – 720 | 80px | Motto (left), Date (right), separated by a thin blue line |

### Margins & Spacing

| Element | Value (px) |
| ------- | ---------- |
| Left / right margin | 60px |
| Top / bottom margin | 40px |
| **Grid base unit** | 20px |
| Card gap | 40px |
| Content block gap | 20px |
| Card padding | 30px |
| Card border radius | 0px (Uses sharp geometric angles/parallelograms) |

---

## V. Page-Type Treatments

### 1. Cover Page
- **Background**: White with a large `#003D7C` slanted block on the right half.
- **Decorative elements**: A secondary `#A0B4CC` slanted line echoing the main block.
- **Title treatment**: 60px, Bold, Left-aligned in the white area.
- **Subtitle**: 28px, Regular, below the title.

### 2. Chapter / Section Page
- **Background**: Solid `#003D7C`.
- **Chapter number**: 80px, Bold, White, centered.
- **Chapter title**: 40px, Bold, White, centered below the number.
- **Decorative line**: A horizontal white line (2px) spanning 200px below the title.

### 3. Content Page (The Workhorse)
- **Background**: White.
- **Top decorative bar**: A thin `#003D7C` horizontal line at y=95.
- **Title position**: y=50, 40px, Bold, `#003D7C`, Left-aligned.
- **Header Icon**: A slanted blue parallelogram icon to the left of the title.
- **Default card layout**: Three-column slanted cards. Each card consists of a `#003D7C` parallelogram with a `#A0B4CC` outline/shadow offset 8px to the right and bottom.
- **Footer**: Motto "团结、进取、求实、创新" at bottom-left; Date at bottom-right.

### 4. Ending / Closing Page
- **Background**: White.
- **Thank-you message**: "感谢您的聆听" (Thank you for listening), 48px, Bold, `#003D7C`, Centered.
- **Contact info**: University URL and Department name centered at y=500.
- **Decorative carryover**: Slanted blue bars at the top-left and bottom-right corners.

---

## VI. Visual Features

### Decorative Elements
- **Slanted Motif**: All primary containers are parallelograms with a ~15-degree slant.
- **Double-Layering**: Primary shapes often have a "ghost" or "shadow" shape in `#A0B4CC` behind them, offset by 8-10px.

### Shadow Effects
- **No soft shadows**: The design uses "hard shadows" created by secondary geometric shapes in a lighter color (`#A0B4CC`).

### Border & Line Style
- **Header/Footer Lines**: 1.5px solid `#003D7C`.
- **Card Outlines**: 1px solid `#A0B4CC` for the background decorative shape.

---

## VII. Component Patterns

### Content Cards (Slanted)
- **Background**: `#003D7C` (Primary Blue).
- **Shape**: Parallelogram (skewX: -15deg).
- **Shadow Shape**: A larger, unfilled parallelogram border in `#A0B4CC` positioned behind the main card.
- **Card Title**: 28px, Bold, White, centered in the top third of the card.
- **Card Body**: 20px, Normal, White, centered in the bottom two-thirds.

### Numbered Badges
- **Style**: Small slanted parallelograms in `#A0B4CC` with white bold text.

### Title Treatment
- **Page Title**: Accompanied by a 40x40px slanted blue icon on the far left.
- **University Branding**: Official logo placed at the top right (y=30, x=1100).

---

## VIII. Design Quality Rules

- **Geometric Consistency**: Every rectangular element (cards, icons, decorative bars) must be skewed by the same angle (approx -15 degrees).
- **Content Fill Ratio**: ~65% content, 35% whitespace.
- **Alignment**: Strict left-alignment for text within the header and footer; center-alignment for text within slanted cards.
- **Color Restraint**: Maximum of 2 shades of blue + white + dark gray text. No gradients unless used subtly on large card surfaces.
- **Institutional Branding**: The DUT logo and motto are mandatory on every content page.