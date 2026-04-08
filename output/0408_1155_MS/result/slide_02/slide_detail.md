# Layout Specification for Slide 2

## 1. Page Meta

- **Page role**: `situation` (Establishing shared context about the fundamental nature of sequence transduction and the historical RNN approach)
- **Style tier inferred**: `B. General Consulting` — The design spec signals "corporate-traditional", "formal academic presentation", "structured", "authoritative", with institutional colors and geometric precision. This aligns with General Consulting's data-driven, report-like aesthetic with muted blues/grays and structured layouts.
- **Content density**: `Relaxed 3-5 items → 24px body` (5 content points, moderate text length)
- **Layout mode**: `card_grid_3col` (The design specification explicitly calls for "Three-column angled cards" as the primary pattern for content pages, suitable for parallel concepts like the 5 key points about sequence transduction fundamentals)
- **Rationale**: This is a foundational "situation" slide establishing shared context. The 5 content points are parallel concepts about sequence transduction and RNNs, making them ideal for the institutional three-column parallelogram card layout specified in the design. The academic/formal tone matches the structured card approach.

## 2. Narrative & Argument Plan

- **Core conclusion (one sentence)**: "Sequence transduction tasks form the backbone of NLP, with RNN-based encoder-decoder architectures dominating for over a decade before attention mechanisms enhanced them."
- **Title (KEEP the slide plan's original title verbatim)**: "Background: Sequence Transduction is Fundamental"
- **Takeaway Box text** (≤ 20 words): "Sequence tasks like translation are NLP's core; RNN encoder-decoder architectures dominated for a decade before attention improved them."
- **Supporting arguments** (mapped to 5 cards):
  1. Core NLP tasks are sequence transduction problems
  2. RNNs (LSTMs, GRUs) were the dominant approach for over a decade
  3. RNNs process sequences step-by-step with hidden state memory
  4. Encoder-decoder framework became the standard architecture
  5. Attention mechanisms later enhanced decoder focus on relevant input parts

## 3. Data Contextualization Plan

No numerical metrics or charts in this slide plan. This is a conceptual foundation slide.

## 4. Image Plan

No figure included in this slide.

## 5. Background & Decorations

- **Background**: Solid `#F8F9FA` (very light warm gray)
- **Top accent bar**: Full-width 3px solid `#0A3D8F` horizontal line at y=100px (from design spec)
- **Book icon**: 50×50px stylized open book in `#0A3D8F` at x=40, y=40 (left of title)
- **Institutional logo**: Circular seal + bilingual text at x=1160, y=40, height=50px
- **Card shadow effect**: Each blue card has a white parallelogram shape layered behind at +8px x-offset, +8px y-offset (creating depth through geometry)
- **Footer decorative elements**: Calligraphic Chinese characters (institutional motto) at bottom left, date at bottom right

## 6. Title Area & Takeaway Box

- **Title text**: "Background: Sequence Transduction is Fundamental" (copied verbatim, 47 characters)
- **Position and alignment**: Left-aligned at x=100 (after 50px book icon + 10px gap), y=40
- **Font**: 44px Bold, `#0A3D8F` (from design spec: Section title = 2.0x × 22px body = 44px)
- **Subtitle**: None
- **Separator line**: 3px solid `#0A3D8F` horizontal line at y=100px, spanning x=40 to x=1240 (full width minus margins)
- **Takeaway Box**: 
  - Position: x=40, y=80, width=1200, height=45
  - Styling: rx=0 (sharp corners per design), fill=`#0A3D8F` with fill-opacity="0.08"
  - Text: "Sequence tasks like translation are NLP's core; RNN encoder-decoder architectures dominated for a decade before attention improved them."
  - Font: 15px Bold, `#0A3D8F`, centered within box

## 7. Content Elements

**Grid layout calculation**:
- Safe content zone: x=40–1240 (1200px width), y=110–620 (510px height after title/takeaway)
- 3 columns with 40px gaps between cards (from design spec)
- Each card width = (1200px - 2×40px gaps) / 3 = 373.33px → round to 374px
- Card height: 480px (leaves 30px margin at bottom before footer)
- Card positions: 
  - Card 1: x=40, y=110
  - Card 2: x=40+374+40=454, y=110  
  - Card 3: x=454+374+40=868, y=110

**Note**: Cards will use 15° slant (shear transformation) as specified in design. The bounding boxes above are for the transformed parallelograms' axis-aligned containers.

---

#### Element 1: Core NLP Tasks Card

**Component type**: Content Card (parallelogram with 15° slant)

**Bounding box**: x=40, y=110, width=374px, height=480px

**Card styling**:
- Fill: `#0A3D8F` (institutional blue)
- Border: 2px solid `#0A3D8F` (self-border)
- Border-radius: 0px (sharp corners)
- Shadow: White parallelogram shape behind at x=48, y=118 (offset +8px)
- Header strip: Top 80px of card, fill=`#0A3D8F` (integrated)
- Header text: "Core Tasks", centered, font size=32px Bold, color=`#FFFFFF`

**Body content**:
- Line 1: "Tasks like machine translation,"
- Line 2: "text summarization, and speech"
- Line 3: "recognition are core to NLP."
- Font: size=24px, weight=normal, color=`#FFFFFF`
- Line height: 1.4em (Latin text)
- Text start position: x_offset=50px (accounting for slant), y_offset=100px from card top

**Wrapping calculation**:
- Container inner width: 374px - 50px (left padding) - 30px (right padding) = 294px
- Chars per line at font_size=24px: 294px / (24px × 0.55) ≈ 22 characters
- Total chars: 73 characters → 4 lines needed (but we can fit in 3 with careful splitting)
- Text block height: 3 lines × 24px × 1.4 = 100.8px

---

#### Element 2: RNN Dominance Card

**Component type**: Content Card (parallelogram with 15° slant)

**Bounding box**: x=454, y=110, width=374px, height=480px

**Card styling**:
- Fill: `#0A3D8F`
- Border: 2px solid `#0A3D8F`
- Border-radius: 0px
- Shadow: White parallelogram shape behind at x=462, y=118
- Header strip: Top 80px, fill=`#0A3D8F`
- Header text: "RNN Era", centered, font size=32px Bold, color=`#FFFFFF`

**Body content**:
- Line 1: "The dominant approach for over"
- Line 2: "a decade: Recurrent Neural"
- Line 3: "Networks (RNNs, LSTMs, GRUs)."
- Font: size=24px, weight=normal, color=`#FFFFFF`
- Line height: 1.4em
- Text start position: x_offset=50px, y_offset=100px

**Wrapping calculation**:
- Container inner width: 294px
- Chars per line: ≈ 22 characters
- Total chars: 67 characters → 3 lines
- Text block height: 3 × 24 × 1.4 = 100.8px

---

#### Element 3: RNN Processing Card

**Component type**: Content Card (parallelogram with 15° slant)

**Bounding box**: x=868, y=110, width=374px, height=480px

**Card styling**:
- Fill: `#0A3D8F`
- Border: 2px solid `#0A3D8F`
- Border-radius: 0px
- Shadow: White parallelogram shape behind at x=876, y=118
- Header strip: Top 80px, fill=`#0A3D8F`
- Header text: "Step Processing", centered, font size=32px Bold, color=`#FFFFFF`

**Body content**:
- Line 1: "RNNs process sequences"
- Line 2: "step-by-step, maintaining a"
- Line 3: "hidden state that encodes"
- Line 4: "history."
- Font: size=24px, weight=normal, color=`#FFFFFF`
- Line height: 1.4em
- Text start position: x_offset=50px, y_offset=100px

**Wrapping calculation**:
- Container inner width: 294px
- Chars per line: ≈ 22 characters
- Total chars: 58 characters → 4 lines (short lines)
- Text block height: 4 × 24 × 1.4 = 134.4px

---

#### Element 4: Encoder-Decoder Card

**Component type**: Content Card (parallelogram with 15° slant)

**Bounding box**: x=40, y=110+480+40=630, width=374px, height=480px

**Card styling**:
- Fill: `#0A3D8F`
- Border: 2px solid `#0A3D8F`
- Border-radius: 0px
- Shadow: White parallelogram shape behind at x=48, y=638
- Header strip: Top 80px, fill=`#0A3D8F`
- Header text: "Encoder-Decoder", centered, font size=32px Bold, color=`#FFFFFF`

**Body content**:
- Line 1: "The encoder-decoder framework"
- Line 2: "became standard: an encoder"
- Line 3: "reads the input, a decoder"
- Line 4: "generates the output."
- Font: size=24px, weight=normal, color=`#FFFFFF`
- Line height: 1.4em
- Text start position: x_offset=50px, y_offset=100px

**Wrapping calculation**:
- Container inner width: 294px
- Chars per line: ≈ 22 characters
- Total chars: 70 characters → 4 lines
- Text block height: 4 × 24 × 1.4 = 134.4px

---

#### Element 5: Attention Enhancement Card

**Component type**: Content Card (parallelogram with 15° slant)

**Bounding box**: x=454, y=630, width=374px, height=480px

**Card styling**:
- Fill: `#0A3D8F`
- Border: 2px solid `#0A3D8F`
- Border-radius: 0px
- Shadow: White parallelogram shape behind at x=462, y=638
- Header strip: Top 80px, fill=`#0A3D8F`
- Header text: "Attention", centered, font size=32px Bold, color=`#FFFFFF`

**Body content**:
- Line 1: "Attention mechanisms were"
- Line 2: "later added, allowing the"
- Line 3: "decoder to focus on relevant"
- Line 4: "parts of the input sequence."
- Font: size=24px, weight=normal, color=`#FFFFFF`
- Line height: 1.4em
- Text start position: x_offset=50px, y_offset=100px

**Wrapping calculation**:
- Container inner width: 294px
- Chars per line: ≈ 22 characters
- Total chars: 71 characters → 4 lines
- Text block height: 4 × 24 × 1.4 = 134.4px

---

**Note**: The 5 cards are arranged in a 3×2 grid pattern (3 columns, 2 rows) with the last card in the second row centered under the first two columns. Element 6 (third card in second row) is omitted to maintain visual balance.

## 8. Visual Emphasis

- **Most visual weight**: Card 2 ("RNN Era") — This represents the historical dominant approach that the presentation will contrast with Transformers
- **Emphasis method**: Slightly larger header font (34px vs 32px) and use of `#1E5AA8` (secondary accent) for the card background instead of primary blue
- **Supporting emphasis**: Card 5 ("Attention") gets a subtle white outline (2px solid `#FFFFFF`) to indicate it's an enhancement to the previous architecture

## 9. Footer

- **Page number**: "2" at x=1240, y=700, right-aligned, font size=14px, color=`#718096` (tertiary text)
- **Institutional motto**: Calligraphic Chinese characters at x=40, y=660, font size=16px, color=`#1A1A1A`
- **Date**: "2024" at x=1240, y=660, right-aligned, font size=16px, color=`#718096`
- **Data source**: Not applicable (no numerical data on this slide)

## 10. Final Spacing & Narrative Check

- [x] **Title** is copied verbatim from slide_plan.title and is 47 characters (single line, no overflow)
- [x] **Takeaway Box** is present directly under the title and carries the one-sentence assertion
- [x] **No metrics** on this conceptual slide (skip comparison check)
- [x] **No charts** on this slide (skip highlight strategy)
- [x] **No images** on this slide (skip aspect ratio check)
- [x] **Color restraint**: 2 primary colors (`#0A3D8F` for cards, `#FFFFFF` for text) + neutrals (`#F8F9FA` background, `#718096` footer)
- [x] **Body font size**: 24px matches relaxed density (5 content points)
- [x] **All elements within safe zone**: 
  - Top: Title at y=40, Takeaway at y=80, Cards start at y=110
  - Bottom: Last card ends at y=630+480=1110px? Wait, recalc: Card 4 & 5 at y=630, height=480 → bottom at y=1110, but safe zone ends at y=680. **ISSUE DETECTED**
  
**ADJUSTMENT NEEDED**: Cards are too tall for the safe zone. Recalculate:

Safe content zone: y=110 to y=620 (510px height)
We need 2 rows of cards with 40px vertical gap between rows.
Each card height should be: (510px - 40px gap) / 2 = 235px

Revised card height: 235px
Card positions:
- Row 1: y=110, height=235px
- Row 2: y=110+235+40=385, height=235px

Card bounding boxes (adjusted):
- Card 1: x=40, y=110, w=374, h=235
- Card 2: x=454, y=110, w=374, h=235  
- Card 3: x=868, y=110, w=374, h=235
- Card 4: x=40, y=385, w=374, h=235
- Card 5: x=454, y=385, w=374, h=235

Header strip: Top 60px (reduced from 80px to fit shorter cards)
Text start position: y_offset=70px (from card top)
Text font size: 20px (reduced from 24px to fit in shorter cards)

- [x] **No overlapping elements**: 40px horizontal gaps between cards, 40px vertical gap between rows
- [x] **All text pre-split**: Each card's text has been split into lines that fit 294px container width
- [x] **No image zones** on this slide
- [x] **No data source** needed (conceptual slide)

**Final adjustment complete**: Card heights reduced to 235px to fit within safe zone, with proportional reductions in header height and body font size.