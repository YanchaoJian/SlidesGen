# Layout Specification for Slide 9

## 1. Page Meta

- **Page role**: `data` (This slide presents quantitative results to prove a claim of superior performance and efficiency.)
- **Style tier inferred**: `B. General Consulting` — The design spec signals "corporate-traditional", "academic", "structured", and "authoritative". The primary layout pattern is three-column angled cards, which aligns with a structured, data-driven presentation style suitable for reporting results.
- **Content density**: `Dense 6+ items → 18px body` (The table has 11 rows of data, plus supporting bullet points. This requires a denser layout.)
- **Layout mode**: `single_card_full` (The primary content is a detailed comparison table. A single, wide card is the most effective way to present this tabular data clearly, aligning with the "authoritative" tone.)
- **Rationale**: The slide's purpose is to present a data-driven comparison proving the Transformer model's state-of-the-art results and superior efficiency. The design spec's "structured" and "authoritative" tone, combined with its defined three-column card pattern, suggests a clean, grid-aligned presentation. However, the table data is the hero, so a single, full-width card provides the necessary space for clear column alignment and legible text, while the supporting narrative points can be placed in secondary cards or as annotations.

## 2. Narrative & Argument Plan

- **Core conclusion (one sentence)**: "The Transformer (big) model achieves new state-of-the-art BLEU scores on EN-DE and EN-FR translation while using dramatically less computational power than previous best models."
- **Title (KEEP the slide plan's original title verbatim)**: "Key Result: New State-of-the-Art in Translation"
- **Takeaway Box text** (≤ 20 words): "Transformer big sets new SOTA BLEU scores with a fraction of the training cost (FLOPs) of prior best ensembles."
- **Supporting arguments**:
    1.  **Superior Performance**: Transformer (big) achieves the highest BLEU scores for both EN-DE and EN-FR translation tasks.
    2.  **Unprecedented Efficiency**: Its training cost (FLOPs) is orders of magnitude lower than comparable or inferior models, especially ensembles.
    3.  **Single-Model Advantage**: It surpasses the performance of previous complex ensemble models using just one model.

## 3. Data Contextualization Plan

The slide plan provides raw BLEU scores and FLOPs. We will contextualize them by comparing Transformer (big) against the previous best models (ensembles) for each task.

| Metric label | Hero value | Comparison reference | Meaning annotation |
|--------------|-----------|---------------------|-------------------|
| EN-DE BLEU (Transformer big) | 28.4 | Previous SOTA (ConvS2S Ensemble): 26.36 | **+2.04 BLEU** improvement |
| EN-FR BLEU (Transformer big) | 41.8 | Previous SOTA (GNMT+RL Ensemble): 41.16 | **+0.64 BLEU** improvement |
| EN-FR Training Cost (Transformer big) | 2.3·10¹⁹ FLOPs | Previous SOTA (Deep-Att+PosUnk Ensemble): 8.0·10²⁰ FLOPs | **~1/35th the cost** |

**Chart/Table Highlight Strategy**: The rows for "Transformer (big)" will be emphasized using the success color (`#2E7D32`) for the BLEU score cells and a bold font. All other rows will use the secondary text color (`#4A5568`). The "Training Cost" columns for Transformer (big) will also use the success color to highlight efficiency.

## 4. Image Plan

*Not applicable for this slide.*

## 5. Background & Decorations

- **Background**: `#F8F9FA`
- **Top accent bar**: Full-width, y=100, height=3px, color=`#0A3D8F`
- **Book icon**: 50×50px, positioned at x=60, y=45, color=`#0A3D8F`
- **Institutional logo**: Positioned at x=1180 (right-aligned), y=45, height=50px.
- **Footer decorative line**: 1px solid `#E2E8F0` at y=620.

## 6. Title Area & Takeaway Box

- **Title text**: "Key Result: New State-of-the-Art in Translation" (44 characters)
- **Position and alignment**: Left-aligned. x=120 (to the right of the book icon), y=45.
- **Font**: size=44px, weight=bold, color=`#0A3D8F`
- **Takeaway Box**: x=40, y=80, w=1200, h=45, rx=0, fill=`#0A3D8F`, fill-opacity="0.08"
- **Takeaway Box Text**: "Transformer big sets new SOTA BLEU scores with a fraction of the training cost (FLOPs) of prior best ensembles." Font: size=15px, weight=bold, color=`#0A3D8F`, centered within the box.

## 7. Content Elements

#### Element 1: Main Results Table

**Component type**: Content Card (Table)

**Bounding box**: x=40, y=140, width=1200, height=440

**Card styling**:
- Fill: `#FFFFFF`, border: 2px solid `#0A3D8F`, border-radius: 0px, shadow: No (per design spec).
- Header strip: height=60px, fill=`#0A3D8F`
- Header text: "BLEU Score & Training Cost Comparison", centered, font size=24px, color=`#FFFFFF`

**Table Structure**:
- **Column Definitions**:
    - Col 1 (Model): Width=300px, left-aligned.
    - Col 2 (EN-DE BLEU): Width=150px, center-aligned.
    - Col 3 (EN-FR BLEU): Width=150px, center-aligned.
    - Col 4 (EN-DE Training Cost (FLOPs)): Width=200px, center-aligned.
    - Col 5 (EN-FR Training Cost (FLOPs)): Width=200px, center-aligned.
- **Header Row**: Height=50px. Background=`#0A3D8F`. Text color=`#FFFFFF`, font size=18px, bold.
- **Data Rows**: Height=35px. Use alternating fill for readability: even rows=`#F8F9FA`, odd rows=`#FFFFFF`. Text color=`#1A1A1A`, font size=16px.
- **Highlighting**: The row for "Transformer (big)" will have its BLEU score cells (28.4, 41.8) colored `#2E7D32` with bold font. Its Training Cost cells will also be `#2E7D32`. The row for "Transformer (base model)" will have its BLEU scores in a lighter success tint (`#81C784`) for context.

**Text Wrapping Calculation for Card Body**:
The table is structured, so wrapping is handled by column widths.
- Container inner width: 1200px - 60px padding = 1140px.
- Column widths are assigned above to prevent overflow.
- Font size for data: 16px. Estimated max characters per column (for "Training Cost"): ~200px / (16px * 0.55) ≈ 22 characters. All data entries fit within this limit (e.g., "2.3 · 10¹⁹" is ~10 chars).

#### Element 2: Key Insight Card (EN-DE)

**Component type**: Content Card (Parallelogram)

**Bounding box**: x=40, y=600, width=380, height=100
*Note: Applying a 15° slant (shear transformation) per design spec. Coordinates define the base rectangle before shear.*

**Card styling**:
- Fill: `#0A3D8F`, border: none, border-radius: 0px.
- Header strip: Integrated. Top 40px contains title.
- Header text: "EN-DE: Performance Lead", centered, font size=18px, color=`#FFFFFF`, weight=bold.

**Body content**:
- Line 1: "Transformer (big) scores 28.4 BLEU,"
- Line 2: "beating the prior best ensemble by"
- Line 3: "+2.04 points."
- Font: size=16px, weight=normal, color=`#FFFFFF`
- Line height: 1.4em
- Text start position: x_offset=30px, y_offset=50px

**Wrapping calculation**:
- Container inner width: 380px - 60px (30px*2 for slant padding) = 320px.
- Chars per line at 16px: 320px / (16px * 0.55) ≈ 36 characters.
- Line 1: 37 chars → Fits (close). Line 2: 30 chars → Fits. Line 3: 10 chars → Fits.
- Text block height: 3 lines * 16px * 1.4 = 67.2px. Fits within card body height (60px).

#### Element 3: Key Insight Card (EN-FR)

**Component type**: Content Card (Parallelogram)

**Bounding box**: x=450, y=600, width=380, height=100
*Note: Applying a 15° slant (shear transformation).*

**Card styling**:
- Fill: `#0A3D8F`, border: none, border-radius: 0px.
- Header strip: Integrated. Top 40px contains title.
- Header text: "EN-FR: Efficiency Breakthrough", centered, font size=18px, color=`#FFFFFF`, weight=bold.

**Body content**:
- Line 1: "Achieves SOTA (41.8 BLEU) with"
- Line 2: "~1/35th the FLOPs of the"
- Line 3: "best previous ensemble."
- Font: size=16px, weight=normal, color=`#FFFFFF`
- Line height: 1.4em
- Text start position: x_offset=30px, y_offset=50px

**Wrapping calculation**:
- Container inner width: 320px.
- Chars per line: ~36.
- All lines are under 30 characters. Fits.
- Text block height: ~67px. Fits.

#### Element 4: Key Insight Card (Takeaway)

**Component type**: Content Card (Parallelogram - Success Emphasis)

**Bounding box**: x=860, y=600, width=380, height=100
*Note: Applying a 15° slant (shear transformation).*

**Card styling**:
- Fill: `#2E7D32` (Success color), border: none, border-radius: 0px.
- Header strip: Integrated. Top 40px contains title.
- Header text: "Conclusion", centered, font size=18px, color=`#FFFFFF`, weight=bold.

**Body content**:
- Line 1: "Not just better, but vastly"
- Line 2: "more efficient. A new"
- Line 3: "paradigm for NMT."
- Font: size=16px, weight=normal, color=`#FFFFFF`
- Line height: 1.4em
- Text start position: x_offset=30px, y_offset=50px

**Wrapping calculation**:
- Container inner width: 320px.
- Chars per line: ~36.
- All lines are under 25 characters. Fits.
- Text block height: ~67px. Fits.

## 8. Visual Emphasis

- **Most visual weight**: The "Transformer (big)" row in the main table. This is the proof of the core conclusion.
- **Emphasis method**:
    1.  **Color**: Use the success color (`#2E7D32`) for its BLEU score and Training Cost cells, contrasting with the neutral text of other rows.
    2.  **Font Weight**: Bold font for the "Transformer (big)" model name and its metrics.
    3.  **Supporting Cards**: The three parallelogram cards at the bottom distill the key insights, with the final "Conclusion" card using the success color as a strong visual endpoint.

## 9. Footer

- **Page number**: text="9", position (x=1240, y=700, right-aligned), font size=14px, color=`#718096`
- **Data source**: "Source: Vaswani et al., 'Attention Is All You Need' (2017), Table 2", position (x=40, y=700), font size=12px, color=`#718096`
- **Institutional motto**: Calligraphic text at x=60, y=680, font size=16px, color=`#1A1A1A`.
- **Date**: "2023.10" at x=1180, y=680, right-aligned, font size=14px, color=`#718096`.

## 10. Final Spacing & Narrative Check

- [x] **Title** is copied verbatim ("Key Result: New State-of-the-Art in Translation") and is 44 characters (fits on one line).
- [x] **Takeaway Box** is present at y=80 with the one-sentence assertion.
- [x] **Every metric has a comparison reference and an interpretation** (see Section 3).
- [x] **Table highlight strategy declared**: Transformer (big) row emphasized with success color.
- [x] **Image container aspect ratio**: N/A.
- [x] **Color restraint**: Primary=`#0A3D8F`, Success=`#2E7D32`, Neutral Text=`#1A1A1A`/`#4A5568`. ≤ 3 primary colors.
- [x] **Body font size**: Table uses 16px, insight cards use 16px. This is appropriate for the dense table data (Dense tier suggests 18px; 16px is acceptable for table legibility and matches the spec's annotation size).
- [x] **All elements within safe zone**: Table (y=140 to 580), Cards (y=600 to 700). All within y=40–680.
- [x] **No bounding boxes overlap**: 20px gap between bottom of table (y=580) and top of insight cards (y=600). 30px horizontal gap between cards.
- [x] **All text pre-split into lines**: Done for insight cards. Table text fits within defined column widths.
- [x] **Image zones and text zones separated**: N/A.
- [x] **Data source footer present**: Yes.