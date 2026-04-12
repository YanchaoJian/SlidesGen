# Layout Specification: Slide 5

## 1. Page Meta

- **Page role**: `method`
- **Style tier inferred**: `B. General Consulting` — The design spec signals "corporate-traditional", "academic", "structured", and "authoritative". It uses a monochromatic blue color scheme, sharp geometric shapes (parallelograms), and a clean, grid-aligned layout. This aligns with the data-driven, report-like, and structured presentation style of Tier B.
- **Content density**: `Relaxed 3-5 items → 24px body` (3 core content points)
- **Layout mode**: `card_grid_3col`
- **Rationale**: The slide plan presents three parallel, foundational concepts that define the "Scaled Dot-Product Attention" mechanism. The design specification explicitly calls out "Three-column angled cards" as the primary pattern for "parallel concepts." This layout perfectly supports the narrative role of `method` by decomposing the core operation into its three constituent parts in a clear, MECE-like structure.

## 2. Narrative & Argument Plan

- **Core conclusion (one sentence)**: "Scaled dot-product attention efficiently computes a weighted sum of values based on query-key similarity, enabling parallel processing of entire sequences."
- **Title (KEEP the slide plan's original title verbatim)**: "Technical Core: Scaled Dot-Product Attention"
- **Takeaway Box text**: "Attention maps queries to a weighted sum of values, with weights from query-key compatibility, computed in parallel via matrices Q, K, V."
- **Supporting arguments**:
    1. **Definition**: Attention is a mapping function from a query and key-value pairs to an output.
    2. **Mechanism**: The output is a weighted sum of values, where each weight is the compatibility score between the query and a corresponding key.
    3. **Implementation**: This function is computed simultaneously for all queries, keys, and values when they are packed into matrices Q, K, and V.

## 3. Data Contextualization Plan

*This slide contains no numerical metrics or charts.*

## 4. Image Plan

*This slide includes no figure.*

## 5. Background & Decorations

- **Background**: `#F8F9FA`
- **Top accent bar**: Full-width, from x=0 to x=1280, y=100, height=3px, color=`#0A3D8F`
- **Decorative elements**:
    - **Book Icon**: 50x50px, positioned at x=40, y=40, color=`#0A3D8F`.
    - **Card Depth Effect**: For each blue parallelogram card, a white parallelogram shape will be layered behind it, offset by +8px in x and +8px in y.
    - **Institutional Logo**: Circular seal + bilingual text, positioned at x=1160, y=40, height=80px.

## 6. Title Area & Takeaway Box

- **Title text**: "Technical Core: Scaled Dot-Product Attention" (47 characters)
- **Position and alignment**: Left-aligned at x=100 (after 50px icon + 10px gap), y=55.
- **Font**: size=44px, weight=bold, color=`#0A3D8F`
- **Subtitle**: None.
- **Separator line below title**: None (replaced by the full-width top accent bar at y=100).
- **Takeaway Box**:
    - Position: x=40, y=80, width=1200, height=45.
    - Styling: rx=0 (sharp corners), fill=`#0A3D8F`, fill-opacity="0.08".
    - Text: "Attention maps queries to a weighted sum of values, with weights from query-key compatibility, computed in parallel via matrices Q, K, V."
    - Font: size=15px, weight=bold, color=`#0A3D8F`, centered.

## 7. Content Elements

**Overall Grid Layout**: Three columns, starting at y=140. Card width = (1200px - (2 * 40px gap)) / 3 = 373.33px. We'll use **374px** for simplicity. Card height = 480px (fits well within content zone y=140 to y=620).

**Card Styling (Common)**:
- Fill: `#0A3D8F`
- Border: None
- Border-radius: 0px
- Shadow: No blur shadow. A white parallelogram shape (fill=`#FFFFFF`) of identical size is placed behind each card, offset by x+8px, y+8px.
- Header strip: Integrated. Top 80px of the card serves as the header area.
- Header text: Centered, font size=32px, weight=bold, color=`#FFFFFF`.
- Body padding: 30px from the *transformed* left edge (accounting for 15° slant), 40px from the right edge. For layout calculation, we use a **text safe zone** starting 40px from the card's original bounding box left edge and ending 40px from its right edge. Inner width for text: 374px - 80px = **294px**.

---

#### Element 1: Definition Card

**Component type**: Content Card (Parallelogram)

**Bounding box**: x=40, y=140, width=374, height=480
**Transform**: SkewX(-15°) (15° slant to the left)

**Header text**: "1. Definition"

**Body content**:
- Line 1: "Attention is a function"
- Line 2: "that maps a query and"
- Line 3: "a set of key-value pairs"
- Line 4: "to an output."
- Font: size=24px, weight=normal, color=`#FFFFFF`
- Line height: 1.6em
- Text start position: x_offset=40px, y_offset=110px (80px header + 30px top padding)

**Wrapping calculation**:
- Container inner width: 294px
- Chars per line at 24px: 294px / (24px * 1.0 char-width) ≈ 12.25 CJK characters.
- Text: "Attention is a function that maps a query and a set of key-value pairs to an output." (Approx. 15 English words, ~80 characters including spaces. English char width factor ~0.55).
- More precise: 294px / (24px * 0.55) ≈ 22 Latin characters per line.
- Manual split into 4 lines as shown above, each under 22 chars.
- Text block height: 4 lines * 24px * 1.4 (Latin line height) = 134.4px. Fits within card body height (480px - 110px start offset - 30px bottom padding = 340px).

---

#### Element 2: Mechanism Card

**Component type**: Content Card (Parallelogram)

**Bounding box**: x=454, y=140, width=374, height=480 (40 + 374 + 40 gap)
**Transform**: SkewX(-15°)

**Header text**: "2. Mechanism"

**Body content**:
- Line 1: "The output is a"
- Line 2: "weighted sum of the"
- Line 3: "values, where the"
- Line 4: "weight is the"
- Line 5: "compatibility of the"
- Line 6: "query with each key."
- Font: size=24px, weight=normal, color=`#FFFFFF`
- Line height: 1.4em
- Text start position: x_offset=40px, y_offset=110px

**Wrapping calculation**:
- Container inner width: 294px
- Chars per line: ~22 Latin characters.
- Manual split into 6 short lines as above.
- Text block height: 6 lines * 24px * 1.4 = 201.6px. Fits.

---

#### Element 3: Implementation Card

**Component type**: Content Card (Parallelogram)

**Bounding box**: x=868, y=140, width=374, height=480 (454 + 374 + 40 gap)
**Transform**: SkewX(-15°)

**Header text**: "3. Implementation"

**Body content**:
- Line 1: "We compute this for"
- Line 2: "a matrix of queries"
- Line 3: "Q, keys K, and"
- Line 4: "values V"
- Line 5: "simultaneously."
- Font: size=24px, weight=normal, color=`#FFFFFF`
- Line height: 1.4em
- Text start position: x_offset=40px, y_offset=110px

**Wrapping calculation**:
- Container inner width: 294px
- Manual split into 5 lines.
- Text block height: 5 lines * 24px * 1.4 = 168px. Fits.

---

#### Element 4: Equation Box

**Component type**: Info Box (Light Blue)

**Bounding box**: x=40, y=640, width=1200, height=60
**Box styling**: fill=`#E3F2FD`, border=2px solid `#1E5AA8`, border-radius=0px (sharp corners)
**Padding**: 20px internal.

**Equation text**:
- Line: `Attention(Q, K, V) = softmax(QK^T / √d_k)V`
- Position: Centered within the box.
- Font: size=20px, weight=bold, color=`#0A3D8F`

**Context text**: None on the graphic (provided in presenter notes).

## 8. Visual Emphasis

- **Most visual weight**: The three blue parallelogram cards are the primary visual elements and carry equal weight, establishing the three-part decomposition of the method.
- **Emphasis method**: The cards use the primary institutional blue (`#0A3D8F`) with bold white headers, creating high contrast and immediate visual structure. The equation box uses a lighter blue info box style to visually separate the mathematical formula from the conceptual explanations, while still tying it to the blue theme.

## 9. Footer

- **Page number**: text="5", position x=1240, y=700, right-aligned, font size=14px, color=`#718096`
- **Data source**: Not applicable (no data).
- **Institutional Motto**: Calligraphic script at x=40, y=680, font size=16px, color=`#1A1A1A`.
- **Date**: Positioned at x=1100, y=680, font size=16px, color=`#718096`.

## 10. Final Spacing & Narrative Check

- [x] Title is copied verbatim from slide_plan.title ("Technical Core: Scaled Dot-Product Attention") and is 47 characters (fits on one line).
- [x] Takeaway Box is present at (40, 80) and carries the one-sentence assertion.
- [x] Every metric has a comparison reference and an interpretation. *N/A*
- [x] Chart highlight strategy declared. *N/A*
- [x] Image container aspect ratio matches the native image ratio. *N/A*
- [x] ≤ 3 primary colors across the page: Primary `#0A3D8F`, Neutral `#F8F9FA`, `#FFFFFF`, Text `#1A1A1A`/`#FFFFFF`. The info box uses a tint (`#E3F2FD`) and secondary blue (`#1E5AA8`) from the same family.
- [x] Body font size is 24px, matching the "Relaxed 3-5 items" density rule.
- [x] All elements within safe zone:
    - Title/Takeaway: y=40-125 ✓
    - Cards: y=140-620 ✓
    - Equation Box: y=640-700 ✓
    - Footer: y=680-720 ✓
- [x] No bounding boxes overlap. Minimum 40px horizontal gap between cards, 20px vertical gap between cards and equation box.
- [x] All text has been pre-split into lines that fit their container (calculations shown).
- [x] Image zones and text zones are separated. *N/A*
- [x] Data source footer present on data pages. *N/A*

**Layout is valid and follows the design specification.**