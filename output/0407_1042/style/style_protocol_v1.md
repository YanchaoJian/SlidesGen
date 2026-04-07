## I. Theme Overview

| Item | Value |
| ---- | ----- |
| **Theme Name** | Dalian University Academic Blue (Refined) |
| **Design Tone Family** | corporate-traditional |
| **Atmosphere** | Formal, institutional, and highly structured. Emulates an academic "paper" feel with technical geometric precision. |
| **Tone Keywords** | academic, geometric, institutional, structured |
| **Theme Mode** | Light (Off-white background with heavy navy accents) |
| **Suitable Scenarios** | Academic defenses, university department meetings, formal research presentations. |

---

## II. Color Scheme

| Role | HEX | Purpose |
| ---- | --- | ------- |
| **Background** | `#F8F9FA` | Main page background (Institutional off-white) |
| **Secondary bg** | `#F4F7FA` | Subtle section backgrounds or alternating rows |
| **Primary** | `#003D7C` | DUT Brand Blue: Header icons, card fills, main titles |
| **Accent** | `#0056A6` | Lighter blue for interactive elements or secondary cards |
| **Secondary accent** | `#E6EEF7` | Very light blue for background shapes or highlights |
| **Body text** | `#1A1A1A` | Main titles and high-contrast body text |
| **Secondary text** | `#FFFFFF` | Text inside primary-colored cards |
| **Tertiary text** | `#808080` | Footers, dates, and page numbers |
| **Border / divider** | `#003D7C` | Card outlines and header separators |
| **Grid Line** | `#E9ECEF` | Subtle background grid pattern |

### Semantic Color Convention

| Semantic role | Assigned color | Where it appears |
| ------------- | ------------- | ---------------- |
| Brand emphasis | `#003D7C` | Page titles, primary content cards, university logo |
| Recommended / success | `#28A745` | Success badges or positive data trends |
| Process / informational | `#0056A6` | Secondary cards, flow arrows, or links |
| Risk / warning | `#DC3545` | Error states or critical warnings |
| Baseline / neutral | `#D1D1D1` | Decorative offset outlines |

### Gradient Definitions
Primarily solid color fills. Depth is achieved through geometric layering and hard-edge offsets.

---

## III. Typography System

| Role | Ratio | Size (px) | Weight | Color Role |
| ---- | ----- | --------- | ------ | ---------- |
| Cover title | 3.0x | 60px | Bold | Primary |
| Section title | 2.0x | 40px | Bold | Primary |
| Subtitle | 1.4x | 28px | SemiBold | Body text |
| **Body** | **1x** | **20px** | Normal | Secondary text (on blue) / Body text |
| Annotation | 0.8x | 16px | Normal | Tertiary text |
| Page number | 0.7x | 14px | Normal | Tertiary text |

**Font stack**: `"Microsoft YaHei", "SimHei", Arial, sans-serif`

---

## IV. Layout Principles

### Page Structure (1280×720 canvas)

| Zone | Y-range (px) | Height (px) | Description |
| ---- | ------------ | ----------- | ----------- |
| Header area | 0 – 100 | 100px | Contains skewed icon, title (left), and logo (right) |
| Content area | 100 – 640 | 540px | Main content zone for cards or text |
| Footer area | 640 – 720 | 80px | Motto (left), Date (right), and thin divider |

### Margins & Spacing

| Element | Value (px) |
| ------- | ---------- |
| Left / right margin | 60px |
| Top / bottom margin | 40px |
| **Grid base unit** | 20px |
| Card gap | 40px |
| Content block gap | 20px |
| Card padding | 30px |
| Card border radius | 0px (Sharp geometric angles) |

### Common Layout Modes

| Mode | Suitable Scenarios |
| ---- | ----------------- |
| Three-column skewed cards | Feature lists, core concepts, or process steps |
| Left-right split (4:6) | Image on left, detailed text on right |
| Single column centered | Cover page or major transition statements |

---

## V. Page-Type Treatments

### 1. Cover Page
- **Background**: `#F8F9FA` with a large navy blue parallelogram occupying the right 40% of the screen (skewed -20°).
- **Decorative elements**: A thin blue outline parallelogram offset 20px from the main shape.
- **Title treatment**: 60px, Bold, Navy Blue, Left-aligned at x=80, y=300.
- **Subtitle**: 28px, Gray, below the title.

### 2. Chapter / Section Page
- **Background**: Solid Navy Blue (#003D7C).
- **Chapter number**: Large "01" in white, 120px, 10% opacity in the background.
- **Chapter title**: 48px, Bold, White, Centered.
- **Decorative line**: A horizontal white line (2px) below the title, 200px wide.

### 3. Content Page (The Workhorse)
- **Background**: `#F8F9FA` with a subtle 40px dot or line grid pattern in `#E9ECEF`.
- **Top decorative bar**: A thin navy blue line (2px) at y=95, spanning the full width.
- **Title position**: y=60, 40px, Bold, Navy Blue, Left-aligned.
- **Header Icon**: A navy blue parallelogram icon (40x40px, skew -20°) containing three horizontal white lines representing a document.
- **Default card layout**: Three parallelograms (skewed -20 degrees). Each card has a solid navy fill and a secondary "ghost" outline shifted 10px down and right.

### 4. Ending / Closing Page
- **Background**: `#F8F9FA`.
- **Thank-you message**: "Thank You", 60px, Bold, Navy Blue, Centered.
- **Contact info**: Centered below the message in 20px Gray.
- **Decorative carryover**: A large navy blue parallelogram in the bottom right corner (skewed -20°).

---

## VI. Visual Features

### Decorative Elements
- **Skewed Icon**: A parallelogram icon (width 30px, height 50px, skew -20deg) precedes every main title. It features a simplified "document" graphic (white horizontal lines).
- **Offset Outlines**: Content cards are paired with a "shadow" outline (1px stroke, Primary color) shifted 8-12px to the bottom-right.
- **Background Grid**: A subtle, low-contrast grid pattern (40px spacing) covers the background to enhance the technical/academic feel.

### Shadow Effects
- No soft blurs. Depth is achieved through **hard-edge geometric offsets** (the "ghost" outline effect).

### Border & Line Style
- **Divider**: 1px solid navy line in the footer.
- **Card Stroke**: 1px solid navy for the offset "ghost" shapes.

### Shape Style
- **Geometric feel**: Sharp, non-rounded corners.
- **Skew**: Consistent **-20 degree** horizontal skew on all major container shapes and icons.

---

## VII. Component Patterns

### Content Cards (Parallelogram)
- **Background**: Solid `#003D7C`.
- **Shape**: Rectangle with `transform: skewX(-20deg)`.
- **Shadow**: A secondary parallelogram with no fill and a 1px `#003D7C` stroke, positioned behind and offset.
- **Card Body Text**: White, **strictly centered**, 20px.
- **Card Header**: Bold white text, 28px, positioned in the top third of the card, **strictly centered**.

### Numbered Badges
- Small white circles with navy text, or bold white numbers at the top of the parallelogram cards.

### Title Treatment
- **Page Title**: Left-aligned, preceded by the "document" parallelogram icon.
- **Subtitle**: 24px, Gray, directly below the main title.

---

## VIII. Design Quality Rules

- **Content fill ratio**: ~65% content, 35% whitespace.
- **Alignment**: Strict left-alignment for page titles; **strict center-alignment** for all text and content within cards.
- **Color restraint**: Max 2 primary colors (Navy and White) plus 1 neutral gray and the off-white background.
- **Geometric Consistency**: Every decorative shape and container must use the same **-20 degree** skew angle.
- **Institutional Branding**: The university logo must always appear in the top right corner of content pages at a fixed scale.