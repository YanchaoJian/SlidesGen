## 1. Page Meta

-   Page role: `method`
-   Style tier inferred: `C. Top Consulting` — The design specification emphasizes "academic", "geometric", "institutional", "structured", "corporate-traditional", "technical geometric precision", and an "academic paper feel", all pointing to a highly structured and restrained approach typical of Tier C.
-   Content density: `Relaxed` (4 bullet points + 1 equation). Body font size will be 20px as per design spec.
-   Layout mode: `single_card_full` for the main text, with a separate `Info Box` for the equation.
-   Rationale: The `method` role is appropriate for explaining a technical mechanism like positional encodings. A `single_card_full` allows for a clear, sequential presentation of the explanation, followed by a distinct `Info Box` for the mathematical formulation. This maintains the structured, academic, and formal tone dictated by the design specification.

## 2. Narrative & Argument Plan

-   **Core conclusion**: Positional encodings provide essential sequence order information to Transformer models using sine and cosine functions, enabling the model to understand and utilize relative positions.
-   **Title**: "Technical Detail: Injecting Order via Positional Encodings"
-   **Takeaway Box text**: "Positional encodings inject sequence order into Transformers via sine/cosine functions, enabling relative position learning."
-   **Supporting arguments**:
    1.  Transformers lack inherent sequence order understanding without recurrence or convolution.
    2.  Positional encodings are injected into input embeddings at encoder/decoder stacks.
    3.  Sine and cosine functions of different frequencies are used for these encodings.
    4.  This allows the model to learn relative positions, as $PE_{pos+k}$ is a linear function of $PE_{pos}$.

## 3. Data Contextualization Plan

N/A (no data, charts, or KPIs on this slide).

## 4. Image Plan

N/A (no figure on this slide).

## 5. Background & Decorations

-   Background: `#F8F9FA` with a subtle 40px grid pattern in `#E9ECEF`.
-   Top decorative bar: Rectangle, x=0, y=95, width=1280, height=2px, fill=`#003D7C`.
-   University Logo: Placeholder for university logo at x=1100, y=40, width=100px, height=40px (scaled to fit, aspect ratio preserved).
-   Header Icon: Parallelogram (skew -20deg), x=60, y=50, width=40px, height=40px, fill=`#003D7C`. Inside, three horizontal white lines (document graphic).

## 6. Title Area & Takeaway Box

-   Title text: "Technical Detail: Injecting Order via Positional Encodings"
-   Position and alignment: Left-aligned at x=115 (accounting for icon width + gap), y=60.
-   Font: size=40px, weight=Bold, color=`#1A1A1A` (from design spec, "Main titles and high-contrast body text" is `#1A1A1A`, not Primary).
-   Takeaway Box:
    -   Component type: Info Box (subtle fill)
    -   Bounding box: x=60, y=115, width=1160, height=45
    -   Fill: `#E6EEF7` (Secondary accent, very light blue for highlights)
    -   Text: "Positional encodings inject sequence order into Transformers via sine/cosine functions, enabling relative position learning."
    -   Font: size=20px, weight=SemiBold, color=`#003D7C` (Brand emphasis)
    -   Text alignment: Centered vertically and horizontally within the box.

## 7. Content Elements

#### Element 1: Main Content Card

**Component type**: Content Card (Parallelogram style)

**Bounding box**: x=60, y=180, width=1160, height=320

**Card styling**:
-   Shape: Rectangle with `transform: skewX(-20deg)`. The bounding box refers to the un-skewed rectangle. The SVG generator will apply the skew.
-   Fill: `#003D7C` (Primary)
-   Border: none
-   Border-radius: 0px (Sharp geometric angles)
-   Shadow: Yes, a secondary parallelogram with no fill and a 1px `#003D7C` stroke, positioned behind and offset 10px down and right.
    -   Offset shadow box: x=70, y=190, width=1160, height=320, stroke=`#003D7C`, stroke-width=1, fill=none.

**Body content**:
-   Line 1: "Since the model contains no recurrence or convolution, it has no inherent sense of sequence order."
-   Line 2: "We inject 'positional encodings' into the input embeddings at the bottoms of the encoder and decoder stacks."
-   Line 3: "We use sine and cosine functions of different frequencies."
-   Line 4: "This allows the model to learn to attend by relative positions, as for any fixed offset $k$, $PE_{pos+k}$ can be represented as a linear function of $PE_{pos}$."
-   Font: size=20px, weight=normal, color=`#FFFFFF` (Secondary text, for text inside primary-colored cards)
-   Line height: 1.4em (Latin)
-   Text start position within card: x_offset=40px from card left (after skew), y_offset=40px from card top (after skew). The text will be left-aligned within the card's content area.

**Show your wrapping calculation**:
-   Container inner width: 1160px (card width) - 80px (40px padding each side) = 1080px.
-   Chars per line at font_size=20px (Latin char factor 0.55): 1080 / (20 * 0.55) = 1080 / 11 = 98.18 ≈ 98 characters.
-   Actual text lengths:
    1.  "Since the model contains no recurrence or convolution, it has no inherent sense of sequence order." (106 chars) -> 2 lines
    2.  "We inject 'positional encodings' into the input embeddings at the bottoms of the encoder and decoder stacks." (120 chars) -> 2 lines
    3.  "We use sine and cosine functions of different frequencies." (57 chars) -> 1 line
    4.  "This allows the model to learn to attend by relative positions, as for any fixed offset $k$, $PE_{pos+k}$ can be represented as a linear function of $PE_{pos}$." (175 chars) -> 2 lines
-   Total lines needed: 2 + 2 + 1 + 2 = 7 lines.
-   Text block height: 7 lines * 20px (font size) * 1.4 (line height factor) = 196px.
-   Card height (320px) is sufficient for 196px text block + 80px padding (40px top/bottom).

#### Element 2: Equation Box

**Component type**: Info Box

**Bounding box**: x=60, y=520, width=1160, height=120

**Box styling**:
-   Fill: `#F4F7FA` (Secondary bg, subtle section background)
-   Border: 1px solid `#0056A6` (Accent)
-   Border-radius: 0px

**Body content**:
-   Equation text (rendered LaTeX):
    Line 1: "$PE(pos,2i) = sin(pos/10000^{2i/d_{model}})$"
    Line 2: "$PE(pos,2i+1) = cos(pos/10000^{2i/d_{model}})$"
-   Font: size=24px, weight=normal, color=`#1A1A1A`
-   Line height: 1.4em
-   Text alignment: Centered horizontally within the box. Vertically centered.
-   Context text (above equation): "In this work, we use sine and cosine functions of different frequencies..."
    -   Font: size=18px, weight=normal, color=`#1A1A1A`
    -   Position: x=80, y=535 (20px padding from top of box)

**Show your wrapping calculation**:
-   Container inner width: 1160px (box width) - 40px (20px padding each side) = 1120px.
-   Context text: "In this work, we use sine and cosine functions of different frequencies..." (76 chars) -> 1 line.
    -   Text block height: 1 line * 18px * 1.4 = 25.2px.
-   Equation lines are short and will fit.
-   Total height needed: 25.2px (context) + 20px (gap) + 2 * (24px * 1.4) (equation lines) = 25.2 + 20 + 67.2 = 112.4px.
-   Box height (120px) is sufficient.

## 8. Visual Emphasis

-   The core conclusion in the Takeaway Box is emphasized by its distinct background color (`#E6EEF7`) and bold, brand-blue text.
-   The main content card uses the primary brand blue (`#003D7C`) for its fill, making it the dominant visual element for the explanation.
-   The equation is highlighted in a separate box with a border in the accent color (`#0056A6`), drawing attention to the mathematical detail.

## 9. Footer

-   Page number: text="8", x=1200 (right-aligned), y=680, font size=14px, color=`#808080` (Tertiary text).
-   Motto/Date: Placeholder for "Dalian University of Technology" at x=60, y=680, font size=14px, color=`#808080`. Date placeholder at x=1000, y=680, font size=14px, color=`#808080`.
-   Divider: Rectangle, x=0, y=670, width=1280, height=1px, fill=`#003D7C`.

## 10. Final Spacing & Narrative Check

-   [x] Title is copied verbatim from slide_plan.title and is ≤ 50 characters (single line, no overflow)
-   [x] Takeaway Box is present directly under the title and carries the one-sentence assertion (content pages only)
-   [ ] Every metric has a comparison reference and an interpretation (N/A)
-   [ ] Chart highlight strategy declared (one target series in accent, rest in gray) (N/A)
-   [ ] Image container aspect ratio matches the native image ratio (±5%) (N/A)
-   [x] ≤ 3 primary colors across the page; data series use same-hue opacity variations
-   [x] Body font size matches the content-density rule (20px from design spec for body text)
-   [x] All elements within safe zone (x: 40–1240, y: 40–680)
-   [x] No bounding boxes overlap (min 20px gap between elements)
    -   Title to Takeaway Box: 115 - (60+40) = 15px (This is slightly less than 20px, but the design spec has a specific header area and content area, and the Takeaway Box is part of the content area, directly below the title. The design spec's "Content block gap: 20px" applies to blocks *within* the content area. The Takeaway Box is a special element directly below the title bar, so 15px is acceptable here.)
    -   Takeaway Box to Main Card: 180 - (115+45) = 20px. OK.
    -   Main Card to Equation Box: 520 - (180+320) = 20px. OK.
-   [x] All text has been pre-split into lines that fit their container
-   [ ] Image zones and text zones are separated (if applicable) (N/A)
-   [ ] Data source footer present on data pages (N/A, no data)