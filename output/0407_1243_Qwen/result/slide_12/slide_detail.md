### 1. Page Meta

- **Page role**: `data` (Proving a claim with numbers/table)
- **Style tier inferred**: **B. General Consulting** — Design spec signals "academic, structured, institutional" with "KPI dashboards / tables" suitable for research summaries.
- **Content density**: **Dense** (7 bullet points + 11-row table) → Body baseline **18px** (Table data **13px** to fit).
- **Layout mode**: `card_grid_3col` (Top row for key stats) + `single_card_full` (Bottom row for detailed table).
- **Rationale**: The slide presents a dense comparison. Splitting key insights into 3 summary cards (Quality, Speed, Cost) allows immediate digestion of the "Key Results" before diving into the granular table data below. This adheres to the "Conclusion First" principle.

---

### 2. Narrative & Argument Plan

- **Core conclusion (one sentence)**: Transformer achieves state-of-the-art translation quality with significantly lower computational cost than previous ensemble models.
- **Title (KEEP verbatim)**: Key Results: English-to-German Translation Performance
- **Takeaway Box text**: Transformer (big) achieves 28.4 BLEU, outperforming all ensembles at a fraction of the training cost.
- **Supporting arguments**:
    1.  **Quality**: New SOTA at 28.4 BLEU (+2.04 vs previous best).
    2.  **Efficiency**: Trains in 3.5 days (vs weeks for others).
    3.  **Cost**: 77% fewer FLOPs than ConvS2S Ensemble.

---

### 3. Data Contextualization Plan

| Metric label | Hero value | Comparison reference | Meaning annotation |
|--------------|-----------|---------------------|-------------------|
| **BLEU Score** | 28.4 | ConvS2S Ensemble: 26.36 | **+2.04 pts improvement** |
| **Training Time** | 3.5 days | Typical Ensemble: ~1 week | **~50% faster** |
| **Compute Cost** | 2.3·10^19 FLOPs | ConvS2S Ensemble: 7.7·10^19 | **70% reduction** |

- **Chart/Table Type**: **Benchmarking Matrix** (Table).
- **Highlight Strategy**: The two "Transformer" rows (Base & Big) will use **Primary Color (`#005587`) bold text** for the BLEU and Cost columns. All other rows remain Secondary Text (`#64748B`).

---

### 4. Image Plan

- **N/A**: This slide contains a table, not an image file.

---

### 5. Background & Decorations

- **Background**: Color `#FFFFFF` (White).
- **Top Accent Bar**: Full-width, height 6px, color `#005587` (Primary), y=0.
- **Decorative Elements**: None (Minimalist academic style).
- **Grid**: All elements aligned to 20px grid.

---

### 6. Title Area & Takeaway Box

- **Title text**: "Key Results: English-to-German Translation Performance"
- **Position**: Centered at x=640, y=45.
- **Font**: Size 32px (adjusted to fit width), Weight Bold, Color `#005587`.
- **Takeaway Box**:
    - **Position**: x=40, y=90, w=1200, h=45.
    - **Style**: Fill `#EBF8FF` (Light Primary, 10% opacity), Border `#005587` (1px), Radius 6px.
    - **Text**: "Transformer (big) achieves 28.4 BLEU, outperforming all ensembles at a fraction of the training cost."
    - **Font**: Size 16px, Weight Bold, Color `#005587`, Centered vertically.
- **Separator**: None (Takeaway box acts as separator).

---

### 7. Content Elements

#### Element 1: Key Stat Card (Quality)
**Component type**: Content Card
**Bounding box**: x=40, y=150, width=380, height=140
**Card styling**:
- Fill: `#FFFFFF`, Border: `#005587` (1px), Radius: 12px
- Header strip: Height 40px, Fill `#005587`
- Header text: "New SOTA Quality", Left-aligned (x=60, y=165), Font 18px Bold, Color `#FFFFFF`
**Body content**:
- Line 1: "28.4 BLEU on WMT 2014"
- Line 2: "Beats ConvS2S Ensemble"
- Line 3: "(26.36) by +2.04 points"
- Font: Size 16px, Weight Normal, Color `#4A5568`
- Line height: 1.5em
- Text start: x=60, y=205
**Wrapping calculation**:
- Inner width: 340px. Max chars ≈ 34. Lines fit easily.

#### Element 2: Key Stat Card (Speed)
**Component type**: Content Card
**Bounding box**: x=440, y=150, width=380, height=140
**Card styling**: Same as Element 1.
- Header text: "Fast Training"
**Body content**:
- Line 1: "3.5 days on 8 P100 GPUs"
- Line 2: "Base model trains even"
- Line 3: "faster at lower cost"
- Font: Size 16px, Color `#4A5568`
- Text start: x=60, y=205

#### Element 3: Key Stat Card (Efficiency)
**Component type**: Content Card
**Bounding box**: x=840, y=150, width=380, height=140
**Card styling**: Same as Element 1.
- Header text: "Low Compute Cost"
**Body content**:
- Line 1: "2.3·10^19 FLOPs total"
- Line 2: "77% less than ConvS2S"
- Line 3: "Ensemble (7.7·10^19)"
- Font: Size 16px, Color `#4A5568`
- Text start: x=60, y=205

#### Element 4: Benchmark Table Card
**Component type**: Content Card (Table)
**Bounding box**: x=40, y=310, width=1200, height=360
**Card styling**:
- Fill: `#FFFFFF`, Border: `#005587` (1px), Radius: 12px
- Header strip: Height 40px, Fill `#005587`
- Header text: "Model Comparison (BLEU & Training Cost)", Left-aligned (x=60, y=325), Font 18px Bold, Color `#FFFFFF`
**Table Structure**:
- **Columns**: 7 columns total.
    - Col 1 (Model): width 240px, Align Left
    - Col 2 (EN-DE): width 100px, Align Center
    - Col 3 (EN-FR): width 100px, Align Center
    - Col 4 (Cost DE): width 180px, Align Center
    - Col 5 (Cost FR): width 180px, Align Center
    - Col 6/7 (Empty/Merged): width 400px (Spacer)
- **Rows**: 1 Header Row + 10 Data Rows.
- **Row Height**: 28px (to fit 11 rows in ~310px body height).
- **Font**: Size 13px, Color `#64748B` (Secondary Text).
- **Header Row**: Fill `#F8FAFC`, Text `#005587` Bold.
- **Data Rows**: Alternating Fill `#FFFFFF` / `#F8FAFC` (Zebra striping).
- **Highlighting**:
    - Rows 9 & 10 (Transformer Base/Big): Text Color `#005587` (Bold) for BLEU and Cost columns.
    - Row 10 (Transformer Big): Background Fill `#EBF8FF` (Light Blue) to emphasize the winner.

**Table Content (Pre-calculated for 13px font)**:
- *Header*: Model | EN-DE | EN-FR | Cost DE | Cost FR
- *Row 1*: ByteNet [18] | 23.75 | - | - | -
- *Row 2*: Deep-Att + PosUnk | - | 39.2 | - | 1.0·10^20
- *Row 3*: GNMT + RL [38] | 24.6 | 39.92 | 2.3·10^19 | 1.4·10^20
- *Row 4*: ConvS2S [9] | 25.16 | 40.46 | 9.6·10^18 | 1.5·10^20
- *Row 5*: MoE [32] | 26.03 | 40.56 | 2.0·10^19 | 1.2·10^20
- *Row 6*: Deep-Att Ensemble | - | 40.4 | - | 8.0·10^20
- *Row 7*: GNMT + RL Ensemble | 26.30 | 41.16 | 1.8·10^20 | 1.1·10^21
- *Row 8*: ConvS2S Ensemble | 26.36 | 41.29 | 7.7·10^19 | 1.2·10^21
- *Row 9*: Transformer (base) | 27.3 | 38.1 | - | 3.3·10^18
- *Row 10*: Transformer (big) | 28.4 | 41.8 | - | 2.3·10^19

**Wrapping calculation**:
- Col 1 width 240px. 13px font ≈ 24 chars max. Model names are short enough.
- Numbers are short. No wrapping needed.

---

### 8. Visual Emphasis

- **Primary Emphasis**: **Transformer (big)** row in the table.
    - **Method**: Background fill `#EBF8FF` (Light Primary), Text `#005587` Bold.
- **Secondary Emphasis**: **Takeaway Box**.
    - **Method**: Distinct background color and bold typography at the top.
- **Tertiary Emphasis**: **Top 3 Stat Cards**.
    - **Method**: Solid Blue Headers (`#005587`) draw the eye down from the title.

---

### 9. Footer

- **Page number**: "12", Position x=1240, y=700, Right-aligned, Font 12px, Color `#94A3B8`.
- **Data source**: "Source: Attention Is All You Need (Vaswani et al., 2017)", Position x=40, y=700, Font 10px, Color `#94A3B8`.

---

### 10. Final Spacing & Narrative Check

- [x] Title is copied verbatim ("Key Results: English-to-German Translation Performance", 49 chars).
- [x] Takeaway Box is present at y=90 with the assertion.
- [x] Metrics have comparisons (e.g., "+2.04 points", "77% less").
- [x] Table highlight strategy declared (Transformer rows in Blue).
- [x] N/A for Image aspect ratio.
- [x] Colors: Primary `#005587`, Secondary `#64748B`, Background `#FFFFFF`. (3 colors).
- [x] Body font 16-18px (Relaxed/Dense mix for cards vs table).
- [x] Elements within safe zone (Max y=670 for table bottom).
    - Table Bottom: 310 (y) + 360 (h) = 670. Perfect fit.
- [x] No overlaps (20px gaps between cards).
- [x] Text pre-split (Table rows defined).
- [x] Data source footer present.