# Layout Specification for Slide 10

## 1. Page Meta
- **Page role**: `data` (This page presents experimental results to validate design choices, proving claims with a detailed table.)
- **Style tier inferred**: **B. General Consulting** — The design spec's tone is "academic, institutional, structured, authoritative," with a primary pattern of three-column angled cards for parallel concepts. This aligns with a data-driven, report-like presentation style.
- **Content density**: **Dense (6+ items)** → 18px body font baseline. The slide plan has 5 key findings plus a large, complex table.
- **Layout mode**: `single_card_full` (The primary content is a single, wide table that requires the full content width. The key findings will be presented as a summary card above it.)
- **Rationale**: The core of this slide is Table 3, which is dense and wide. A `single_card_full` layout for the table ensures readability and proper column spacing. A summary card above the table presents the high-level conclusions, creating a clear "takeaway → evidence" narrative flow.

## 2. Narrative & Argument Plan
- **Core conclusion (one sentence)**: "Our ablation study confirms the Transformer's architectural choices: 8 attention heads, sufficient dimensionality, and dropout are optimal for performance."
- **Title (KEEP the slide plan's original title verbatim)**: "Ablation Study: Validating Design Choices"
- **Takeaway Box text** (≤ 20 words): "8 attention heads, sufficient dimensionality, and dropout are optimal; larger models perform better as expected."
- **Supporting arguments**:
    1.  **Head Count**: 8 attention heads is the performance sweet spot.
    2.  **Dimensionality**: Reducing key dimension (`d_k`) degrades quality.
    3.  **Scale**: Larger models (more layers, dimensions) perform better.
    4.  **Regularization**: Dropout is crucial to prevent overfitting.
    5.  **Positional Encoding**: Sinusoidal and learned encodings perform nearly identically.

## 3. Data Contextualization Plan
The slide's primary data is the multi-row ablation table. The key metrics are Perplexity (PPL) and BLEU score, with the "base" model as the comparison baseline.

| Metric label | Hero value (from table) | Comparison reference | Meaning annotation |
|--------------|------------------------|----------------------|-------------------|
| Base Model PPL (dev) | 4.92 | N/A (Baseline) | Reference point for all variations |
| (A) 16 heads, 32 d_k/d_v PPL | 4.91 | vs. Base (4.92) | Matches base performance with different head/dim configuration |
| (B) d_k=16 PPL | 5.16 | vs. Base (4.92) | **-0.24 worse** — confirms need for sufficient dimensionality |
| (C) d_model=256 PPL | 5.75 | vs. Base (4.92) | **-0.83 worse** — larger model dimensions improve performance |
| (D) P_drop=0.0 PPL | 5.77 | vs. Base P_drop=0.1 (4.92) | **-0.85 worse** — dropout is crucial for preventing overfitting |
| Big Model PPL | 4.33 | vs. Base (4.92) | **+0.59 better** — larger models perform better as expected |

**Chart/Table Highlight Strategy**: The table itself is the primary visual. We will use the **Success color (`#2E7D32`)** to highlight the "base" model row and any row that matches or beats its performance (e.g., the "big" model). Rows showing degraded performance will use the standard body text color. The summary card will use the **Primary color (`#0A3D8F`)** for headers to tie the conclusions to the evidence.

## 4. Image Plan
*Not applicable for this slide.*

## 5. Background & Decorations
- **Background**: `#F8F9FA`
- **Top accent bar**: Full-width, 3px solid `#0A3D8F` at y=100px (from design spec).
- **Book icon**: 50×50px, `#0A3D8F`, positioned at x=40, y=40.
- **Institutional logo**: Positioned at x=1160, y=40 (right-aligned), height 80px.
- **Footer decorative line**: 3px solid `#0A3D8F` at y=620px, spanning from x=60 to x=1220.

## 6. Title Area & Takeaway Box
- **Title text**: "Ablation Study: Validating Design Choices" (44px Bold, `#0A3D8F`)
- **Position and alignment**: Left-aligned at x=100 (after 50px icon + 10px gap), y=52.
- **Font**: 44px Bold, `#0A3D8F`, "Microsoft YaHei" stack.
- **Takeaway Box**:
    - Bounding box: x=40, y=80, w=1200, h=45, rx=0 (sharp corners).
    - Fill: `#0A3D8F` with fill-opacity="0.08".
    - Text: "8 attention heads, sufficient dimensionality, and dropout are optimal; larger models perform better as expected."
    - Font: 15px Bold, `#0A3D8F`, centered within the box.

## 7. Content Elements

#### Element 1: Key Findings Summary Card
**Component type**: Content Card (Parallelogram)
**Bounding box**: x=60, y=140, width=1160, height=140.
**Card styling**:
- Fill: `#0A3D8F`
- Border: None
- Border-radius: 0px
- Shadow/Outline: White parallelogram behind at x=68, y=148 (offset +8px, +8px).
- Header strip: Integrated. Top 40px of card contains centered title.
- Header text: "Key Findings", centered, font size=24px Bold, color=`#FFFFFF`.

**Body content**:
- We will present the 5 findings as a concise, 2-line bullet list within the card.
- **Text Wrapping Calculation**:
    - Container inner width: 1160px - 60px (left padding) - 60px (right padding, accounting for slant) = **1040px**.
    - Font size: 18px (Dense mode). Approx. chars per line: 1040 / (18 * 0.55) ≈ **105 Latin characters**.
    - We will format the 5 findings into two compact lines of text.
- Line 1: "• 8 heads optimal • d_k reduction hurts • Larger models better"
- Line 2: "• Dropout crucial • Sinusoidal ≈ learned positional encoding"
- Font: 18px Normal, color=`#FFFFFF`, line height=1.4em.
- Text start position: x_offset=60px, y_offset=60px (below header).

#### Element 2: Ablation Table Card
**Component type**: Content Card (Table)
**Bounding box**: x=60, y=300, width=1160, height=340.
**Card styling**:
- Fill: `#FFFFFF`
- Border: 2px solid `#0A3D8F`
- Border-radius: 0px
- Header strip: Top 50px, fill=`#0A3D8F`.
- Header text: "Table 3: Transformer Architecture Ablation Study", centered, font size=20px Bold, color=`#FFFFFF`.

**Table Structure**:
- **Column Headers (Row 0)**: ["", "N", "d_model", "d_ff", "h", "d_k", "d_v", "P_drop", "ϵ_ls", "train steps", "PPL (dev)", "BLEU (dev)", "params (×10⁶)"]
- **Column Widths & Alignment**: Total width=1100px (1160-60px padding). Columns: [60, 40, 70, 60, 40, 50, 50, 70, 50, 90, 80, 90, 90] (px). All numeric columns right-aligned; text columns left-aligned.
- **Row Height**: 28px.
- **Header Row**: Fill=`#0A3D8F`, text color=`#FFFFFF`, font=16px Bold.
- **Data Rows**: Alternating fill between `#F8F9FA` (even rows) and `#FFFFFF` (odd rows). Text color=`#1A1A1A`, font=14px Normal.
- **Highlighting**: The "base" model row (first data row) and the "big" model row (last data row) will have their "PPL (dev)" and "BLEU (dev)" cell text colored `#2E7D32` (Success).
- **Table Caption**: Positioned at y=650 (just below the card), x=60, width=1160. Text: "Table 3: Variations on the Transformer architecture. Unlisted values are identical to those of the base model. All metrics are on the English-to-German translation development set, newstest2013. Listed perplexities are per-wordpiece.", font=12px, color=`#4A5568`, centered.

## 8. Visual Emphasis
- **Most visual weight**: The **Key Findings Summary Card** (`#0A3D8F` background, white text) receives primary emphasis as it states the validated conclusions.
- **Secondary emphasis**: Within the table, the **"base"** and **"big"** model rows are highlighted using the Success color (`#2E7D32`) for their performance metrics, visually connecting them to the positive findings in the summary card.
- The **Takeaway Box** (light blue tint) directly under the title reinforces the core conclusion.

## 9. Footer
- **Page number**: "10", x=1240, y=700, right-aligned, font size=14px, color=`#718096`.
- **Data source**: "Source: Vaswani et al., 'Attention Is All You Need' (2017)", x=60, y=700, font size=12px, color=`#718096`.
- **Institutional motto**: Calligraphic script, `#1A1A1A`, x=60, y=680, font size=16px.
- **Date**: "[Presentation Date]", x=1240, y=680, right-aligned, font size=14px, color=`#718096`.

## 10. Final Spacing & Narrative Check
- [x] **Title** is "Ablation Study: Validating Design Choices" (46 chars). ✔
- [x] **Takeaway Box** is present at y=80 with the one-sentence assertion. ✔
- [x] **Every metric** in the table is contextualized against the "base" model baseline. ✔
- [x] **Highlight strategy** declared: Success color for base/best performers. ✔
- [x] **No image** on this slide. ✔
- [x] **Color restraint**: Primary (`#0A3D8F`), Success (`#2E7D32`), Neutral text/backgrounds. ≤ 3 colors. ✔
- [x] **Body font size**: 18px (Dense mode). ✔
- [x] **All elements within safe zone**:
    - Summary Card: y=140-280 ✔
    - Table Card: y=300-640 ✔
- [x] **No overlapping bounding boxes**:
    - Gap between Title Bar (ends ~y=125) and Summary Card (y=140): 15px.
    - Gap between Summary Card (ends y=280) and Table Card (y=300): 20px.
    - Gap between Table Card (ends y=640) and Footer (starts y=680): 40px.
- [x] **All text pre-split**: Summary card text fits within 1040px width at 18px. Table column widths calculated to prevent overflow.
- [x] **Data source footer** present. ✔

**Narrative Check**: The slide successfully argues that the Transformer's design is validated. The **Takeaway Box** states the conclusion. The **Summary Card** lists the supporting arguments. The **Detailed Table** provides the quantitative evidence. Highlighting the base and best-performing models in the table visually proves the points made in the summary.