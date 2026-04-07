### 1. Page Meta

- **Page role**: `data`
- **Style tier inferred**: `C. Top Consulting (MBB)` — Inferred from the "academic/institutional" tone, strict geometric constraints (skewed parallelograms), and the use of a high-contrast navy/off-white palette with structured data.
- **Content density**: `Dense` (4 bullet points + a 12-column technical table) → Body baseline: 18px (adjusted to 14-16px for card fit).
- **Layout mode**: `left_right_split` (Table on left 60%, Insight cards on right 40%).
- **Rationale**: The slide presents experimental results (ablation study) which requires a large table for evidence and structured cards to summarize the qualitative takeaways. The split layout allows the audience to see the data and the conclusion simultaneously.

---

### 2. Narrative & Argument Plan

- **Core conclusion**: Multi-head attention and increased model capacity (d_model, d_ff) are the primary drivers of Transformer performance.
- **Title**: "Ablation Study: What Makes the Transformer Work?"
- **Takeaway Box text**: Multi-head attention and model scaling (d_model, d_ff) are the primary drivers of Transformer performance.
- **Supporting arguments**:
    1. **Multi-head Necessity**: Performance significantly degrades when reducing the number of heads (h=1).
    2. **Key Size Sensitivity**: Reducing $d_k$ hurts quality, suggesting complex head compatibility.
    3. **Scaling Benefits**: Larger $d_{model}$ and $d_{ff}$ values consistently improve BLEU scores.
    4. **Encoding Robustness**: Sinusoidal positional encodings match learned embeddings, simplifying the architecture.

---

### 3. Data Contextualization Plan

| Metric label | Hero value | Comparison reference | Meaning annotation |
|--------------|-----------|---------------------|-------------------|
| Peak BLEU (Big) | 26.4 | Base model: 25.8 | +0.6 gain from scaling |
| Single-head BLEU | 24.9 | Base model: 25.8 | -0.9 drop without multi-head |
| Small dk BLEU | 25.1 | Base model: 25.8 | -0.7 drop from reduced key size |

- **Chart type**: Technical Table (Table 3 variation).
- **Highlight strategy**: Row "big" (peak performance) highlighted with `#0056A6` (Accent Blue) text; Row "h=1" (failure case) highlighted with `#DC3545` (Risk Red) text for the BLEU column.

---

### 4. Image Plan
*No figure included in this slide.*

---

### 5. Background & Decorations

- **Background**: `#F8F9FA` (Institutional off-white).
- **Grid Pattern**: 40px dot grid in `#E9ECEF` across the full canvas.
- **Top Accent Bar**: y=95, height 2px, color `#003D7C` (Primary Navy).
- **Header Icon**: Skewed parallelogram (skew -20°) at x=60, y=45, size 40x40, color `#003D7C`, containing 3 white horizontal lines.
- **University Logo**: Placeholder at x=1100, y=40, width 120px (Right-aligned).

---

### 6. Title Area & Takeaway Box

- **Title text**: "Ablation Study: What Makes the Transformer Work?"
- **Position**: x=110, y=65 (Left-aligned).
- **Font**: 40px Bold, `#003D7C`.
- **Takeaway Box**:
    - **Box**: x=60, y=110, w=1160, h=45, fill=`#003D7C` (opacity 0.08), no border.
    - **Text**: "Multi-head attention and model scaling (d_model, d_ff) are the primary drivers of Transformer performance."
    - **Font**: 15px Bold, `#003D7C`, centered vertically and horizontally.

---

### 7. Content Elements

#### Element 1: Ablation Results Table
**Component type**: Content Card (Table)
**Bounding box**: x=60, y=175, width=720, height=480
**Card styling**: White background, 1px `#003D7C` border, sharp corners.
**Table Structure**:
- **Header Row**: height=40, fill=`#003D7C`, text color=`#FFFFFF`, font=14px Bold.
- **Columns**: Config (120), h (80), dk (80), dff (100), Pdrop (100), BLEU (120), Params (120).
- **Data Rows** (14px Normal, `#1A1A1A`):
    - Row 1 (Base): "Base", "8", "64", "2048", "0.1", "25.8", "65M"
    - Row 2 (A): "(A) h=1", "1", "512", "2048", "0.1", "**24.9**" (Red), "65M"
    - Row 3 (B): "(B) dk=16", "8", "16", "2048", "0.1", "25.1", "58M"
    - Row 4 (C): "(C) dff=4096", "8", "64", "4096", "0.1", "26.2", "90M"
    - Row 5 (Big): "Big", "16", "64", "4096", "0.3", "**26.4**" (Accent Blue), "213M"

#### Element 2: Insight Card 1 (Multi-head)
**Component type**: Content Card (Skewed Parallelogram)
**Bounding box**: x=820, y=175, width=380, height=105
**Card styling**: Fill=`#003D7C`, skewX=-20deg.
**Ghost outline**: x=830, y=185, 1px `#003D7C` stroke, no fill.
**Body content** (Centered):
- Line 1: "Multi-head attention outperforms"
- Line 2: "single large heads; performance"
- Line 3: "drops as 'h' decreases."
- Font: 15px, weight=normal, color=`#FFFFFF`.

#### Element 3: Insight Card 2 (Key Size)
**Component type**: Content Card (Skewed Parallelogram)
**Bounding box**: x=820, y=295, width=380, height=105
**Card styling**: Fill=`#003D7C`, skewX=-20deg.
**Ghost outline**: x=830, y=305, 1px `#003D7C` stroke, no fill.
**Body content** (Centered):
- Line 1: "Reducing key size dk hurts quality,"
- Line 2: "indicating that head compatibility"
- Line 3: "is a complex dynamic."
- Font: 15px, weight=normal, color=`#FFFFFF`.

#### Element 4: Insight Card 3 (Scaling)
**Component type**: Content Card (Skewed Parallelogram)
**Bounding box**: x=820, y=415, width=380, height=105
**Card styling**: Fill=`#003D7C`, skewX=-20deg.
**Ghost outline**: x=830, y=425, 1px `#003D7C` stroke, no fill.
**Body content** (Centered):
- Line 1: "Larger models (d_model, d_ff) and"
- Line 2: "stronger dropout are essential"
- Line 3: "for reaching peak performance."
- Font: 15px, weight=normal, color=`#FFFFFF`.

#### Element 5: Insight Card 4 (Positional)
**Component type**: Content Card (Skewed Parallelogram)
**Bounding box**: x=820, y=535, width=380, height=105
**Card styling**: Fill=`#003D7C`, skewX=-20deg.
**Ghost outline**: x=830, y=545, 1px `#003D7C` stroke, no fill.
**Body content** (Centered):
- Line 1: "Sinusoidal encodings perform"
- Line 2: "identically to learned embeddings"
- Line 3: "(25.8 vs 25.7 BLEU)."
- Font: 15px, weight=normal, color=`#FFFFFF`.

---

### 8. Visual Emphasis

- **Primary Emphasis**: The "Big" model row in the table (peak performance) and the "Multi-head" insight card.
- **Technique**: The "Big" row uses the Accent Blue (`#0056A6`) for its BLEU score, while the insight cards use the high-contrast Navy/White combination with the "ghost" outline effect to draw the eye to the qualitative summaries.

---

### 9. Footer

- **Page number**: "11/15" at x=1240, y=700, right-aligned, 12px, `#808080`.
- **Data source**: "Source: Vaswani et al. (2017) 'Attention Is All You Need', Table 3" at x=60, y=700, 10px, `#808080`.
- **Motto**: "Dalian University of Technology" at x=60, y=685, 12px, `#808080`.

---

### 10. Final Spacing & Narrative Check

- [x] Title is verbatim: "Ablation Study: What Makes the Transformer Work?" (8 words).
- [x] Takeaway Box present with assertion: "Multi-head attention and model scaling...".
- [x] Table includes comparison (Base vs Big vs h=1).
- [x] Highlight strategy: Red for drop (h=1), Accent Blue for peak (Big).
- [x] Body font size: 15px (Dense content, fits skewed cards).
- [x] Safe zone: All elements between x:40-1240 and y:40-680.
- [x] No overlaps: 40px gap between table and cards.
- [x] Text pre-split: All card text split into 3 lines to fit skewed inner width.
- [x] Data source footer: Present.