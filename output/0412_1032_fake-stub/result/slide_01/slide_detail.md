# Layout Specification for Slide 1: "Attention Is All You Need"

## 1. Page Meta

- **Page role**: `cover`
- **Style tier inferred**: `A. Versatile` — The design spec emphasizes "academic, institutional, structured" with decorative elements (book icon, calligraphic motto, geometric parallelograms). It uses a creative, imagery-heavy approach with full-width decorative shapes and a strong visual anchor, fitting the versatile tier.
- **Content density**: `Relaxed 3-5 items` → 24px body font baseline.
- **Layout mode**: `cover_centered`
- **Rationale**: This is the opening slide of an academic paper presentation. The cover role requires a centered, authoritative layout that establishes the formal tone. The design specification explicitly describes a cover page treatment with a large institutional blue geometric shape as a visual anchor, left-aligned or centered title, and decorative elements. The content (title, authors, affiliations, conference, core contribution) is best presented in a single-column, centered format for maximum impact and readability.

## 2. Narrative & Argument Plan

*(Skipped for cover page)*

## 3. Data Contextualization Plan

*(No numbers/charts/KPIs on this slide)*

## 4. Image Plan

*(No figure on this slide)*

## 5. Background & Decorations

- **Background**: Solid `#F8F9FA`
- **Top decorative bar**: A 3px solid `#0A3D8F` horizontal line spanning the full width (x=0, y=100, width=1280, height=3).
- **Decorative geometric shape**: A large blue parallelogram (shear 15°) serving as a visual anchor on the left side of the content area.
  - Shape: Parallelogram with 15° slant (skewX=-15°).
  - Position: x=60, y=140, width=400, height=440.
  - Fill: `#0A3D8F`.
  - Outline/Shadow: A white parallelogram layered behind at offset (+8px, +8px) to create depth.
    - White shape: x=68, y=148, width=400, height=440, fill=`#FFFFFF`, skewX=-15°.
- **Book icon**: Positioned within the title area as per design spec.
  - Position: x=60, y=30, width=50, height=50.
  - Fill: `#0A3D8F`.
- **Institutional logo**: Positioned in the upper right corner.
  - Position: x=1100, y=20, width=120, height=80.
  - (Assumed to be a circular seal with bilingual text).

## 6. Title Area & Takeaway Box

*(Cover page does not use a Takeaway Box)*

- **Title text**: "Attention Is All You Need"
- **Position and alignment**: Left-aligned at x=120 (to the right of the book icon), y=40.
- **Font**: 56px Bold, color `#0A3D8F`.
- **Subtitle**: None.
- **Separator line below title**: A 3px solid `#0A3D8D` line positioned below the title.
  - Position: x=120, y=100, width=1040, height=3.

## 7. Content Elements

All content will be placed in a centered, single-column layout within the safe content zone (x: 40–1240, y: 100–620). The large blue parallelogram on the left acts as a decorative anchor; text flows in the remaining space to its right.

#### Element 1: Authors

**Component type**: Content Card (Text Block)

**Bounding box**: x=500, y=180, width=720, height=80. (This is not a blue parallelogram card, but a text block on the light background).

**Body content**:
- Line 1: "Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit,"
- Line 2: "Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin"
- Font: size=24px, weight=normal, color=`#1A1A1A`
- Line height: 1.4em (Latin names)
- Text start position: x_offset=0px, y_offset=0px (within the text block's bounding box).

**Wrapping calculation**:
- Container inner width: 720px.
- Chars per line at 24px: 720 / (24 * 0.55) ≈ 54 characters.
- Total chars (Line 1+2): ~100 characters.
- Lines needed: 2 lines (manually split at the natural break after "Uszkoreit,").
- Text block height: 2 * 24px * 1.4 = 67.2px → fits within 80px height.

#### Element 2: Affiliations

**Component type**: Content Card (Text Block)

**Bounding box**: x=500, y=280, width=720, height=60.

**Body content**:
- Line 1: "Google Brain; Google Research; University of Toronto;"
- Line 2: "Independent (work performed while at Google Research)"
- Font: size=20px, weight=normal, color=`#4A5568`
- Line height: 1.4em
- Text start position: x_offset=0, y_offset=0.

**Wrapping calculation**:
- Container width: 720px.
- Chars per line at 20px: 720 / (20 * 0.55) ≈ 65 characters.
- Total chars: ~85 chars.
- Lines needed: 2 lines.
- Text block height: 2 * 20px * 1.4 = 56px → fits within 60px.

#### Element 3: Conference

**Component type**: Content Card (Text Block)

**Bounding box**: x=500, y=360, width=720, height=40.

**Body content**:
- Line 1: "31st Conference on Neural Information Processing Systems (NeurIPS 2017)"
- Font: size=18px, weight=normal, color=`#4A5568`
- Line height: 1.4em
- Text start position: x_offset=0, y_offset=0.

**Wrapping calculation**:
- Container width: 720px.
- Chars per line at 18px: 720 / (18 * 0.55) ≈ 72 characters.
- Total chars: ~75 chars.
- Lines needed: 1 line (fits).
- Text block height: 1 * 18px * 1.4 = 25.2px → fits within 40px.

#### Element 4: Core Contribution

**Component type**: Info Box (Blue Card - for emphasis)

**Bounding box**: x=500, y=440, width=720, height=140.
**Card styling**:
- Fill: `#0A3D8D`, border: none, border-radius: 0px.
- Header strip: Not used. This is a full-card emphasis.
- Header text: N/A.

**Body content**:
- Line 1: "A new simple network architecture, the Transformer,"
- Line 2: "based solely on attention mechanisms, dispensing with"
- Line 3: "recurrence and convolutions entirely."
- Font: size=24px, weight=bold, color=`#FFFFFF`
- Line height: 1.4em
- Text start position: x_offset=30px (accounting for card padding), y_offset=40px.

**Wrapping calculation**:
- Container inner width: 720px - 60px (30px left + 30px right padding) = 660px.
- Chars per line at 24px: 660 / (24 * 0.55) ≈ 50 characters.
- Total chars: ~115 chars.
- Lines needed: 3 lines (split as shown).
- Text block height: 3 * 24px * 1.4 = 100.8px → fits within 140px height (with 40px top padding).

## 8. Visual Emphasis

- **The core contribution statement** (Element 4) deserves the most visual weight as it is the thesis of the paper.
- **Emphasis method**: It is placed inside a full-width, solid blue (`#0A3D8D`) card with bold white text, making it the most prominent text block on the slide after the title. This follows the design spec's principle of using blue cards for key sections.

## 9. Footer

- **Page number**: text="1", position (x=1240, y=700, right-aligned), font size=14px, color=`#718096`.
- **Institutional motto**: Calligraphic script at bottom left.
  - Position: x=60, y=660.
  - Text: "自强不息 知行合一" (Dalian University of Technology motto).
  - Font: Brush-style script, size=20px, color=`#1A1A1A`.
- **Date/Context**: Positioned at bottom right.
  - Position: x=1100, y=660.
  - Text: "Academic Presentation".
  - Font: size=16px, weight=normal, color=`#718096`.

## 10. Final Spacing & Narrative Check

- [x] **Title**: Copied verbatim ("Attention Is All You Need"). 4 words, 25 characters. Fits on one line.
- [x] **Takeaway Box**: Not present (cover page).
- [x] **Metrics**: No metrics on this slide.
- [x] **Chart highlight**: Not applicable.
- [x] **Image aspect ratio**: Not applicable.
- [x] **Color restraint**: Primary color (`#0A3D8D`) used for title, decorative bar, book icon, parallelogram, and core contribution card. Secondary text colors (`#1A1A1A`, `#4A5568`, `#718096`) used for body text and footer. White used for text on blue. ≤ 3 primary colors.
- [x] **Body font size**: Relaxed density (4 content items) → 24px for main author list and core contribution, 20px and 18px for secondary info. Compliant.
- [x] **Safe zone**: All elements within x: 40–1240, y: 40–680.
  - Title: x=120, y=40.
  - Authors: x=500, y=180.
  - Affiliations: x=500, y=280.
  - Conference: x=500, y=360.
  - Core Contribution: x=500, y=440.
  - Footer elements: y=660.
- [x] **No overlap**: Minimum 20px vertical gaps maintained.
  - Gap between title bar (y=100) and authors (y=180): 80px.
  - Gap between authors and affiliations: 20px (180+80=260 vs 280).
  - Gap between affiliations and conference: 20px (280+60=340 vs 360).
  - Gap between conference and core contribution: 20px (360+40=400 vs 440).
  - Gap between core contribution and footer: 80px (440+140=580 vs 660).
- [x] **Text pre-split**: All multi-line text blocks have been manually split to fit calculated container widths.
- [x] **Image zones**: Not applicable.
- [x] **Data source footer**: Not applicable (no data).

**Narrative Check**: As a cover page, this layout successfully establishes the formal, academic tone. The large title and decorative blue parallelogram anchor the viewer's attention. The author list and affiliations are clearly presented, leading to the highlighted core contribution—the Transformer architecture—which is given prominence through the blue info box, immediately communicating the paper's central claim. The footer adds institutional gravitas. The layout is clean, structured, and authoritative, matching the design specification's intent.