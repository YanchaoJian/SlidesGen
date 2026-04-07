### 1. Page Meta

- **Page role**: `data`
- **Style tier inferred**: `C. Top Consulting (MBB)` — Inferred from the "academic paper" feel, highly structured layout, navy/off-white color restraint, and the use of geometric "ghost" outlines for depth rather than shadows.
- **Content density**: `Dense` (6+ items including table rows and bullet points) → **18px body baseline**.
- **Layout mode**: `left_right_split` (Table on left, insight cards on right).
- **Rationale**: The slide aims to prove a technical claim (SOTA quality + efficiency) using a complex table. A split layout allows the data to be the primary evidence (left) while providing structured narrative takeaways (right).

---

### 2. Narrative & Argument Plan

- **Core conclusion**: The Transformer architecture achieves superior translation quality (SOTA BLEU) while being significantly more computationally efficient (lower FLOPs) than previous RNN and CNN models.
- **Title**: `Key Results: State-of-the-Art Translation Quality`
- **Takeaway Box text**: Transformer (big) achieves SOTA BLEU scores with significantly lower training costs (FLOPs) than previous RNN/CNN architectures.
- **Supporting arguments**:
    1. **Superior Quality**: Transformer (big) outperforms previous SOTA ensembles by over 2.0 BLEU on EN-DE.
    2. **Efficiency Breakthrough**: Results achieved at a fraction of the training cost (FLOPs) compared to GNMT or ConvS2S.
    3. **Base Model Strength**: Even the base Transformer model outperforms most previous complex ensemble models.

---

### 3. Data Contextualization Plan

| Metric label | Hero value | Comparison reference | Meaning annotation |
|--------------|-----------|---------------------|-------------------|
| EN-DE BLEU | 28.4 | Prev SOTA: 26.36 (ConvS2S Ens) | Outperforms by +2.04 pts |
| EN-FR BLEU | 41.8 | Prev SOTA: 41.29 (ConvS2S Ens) | New single-model SOTA |
| Training Cost (EN-FR) | 2.3 · 10¹⁹ | GNMT Ens: 1.1 · 10²¹ | ~47x more efficient |

- **Chart type**: Academic Table (Table 2).
- **Highlight strategy**: The "Transformer (big)" row is highlighted with a light blue background (`#E6EEF7`) and bold text; BLEU scores in this row use the success color (`#28A745`).

---

### 4. Image Plan
*(No figure included in this slide plan)*

---

### 5. Background & Decorations

- **Background**: `#F8F9FA` (Institutional off-white).
- **Grid Pattern**: 40px dot grid in `#E9ECEF` across the entire canvas.
- **Top Accent Bar**: Full-width line at y=95, 2px thickness, color `#003D7C`.
- **Header Icon**: Skewed parallelogram (skew -20°) at x=60, y=40, size 30x50, color `#003D7C`, containing three white horizontal lines.
- **University Logo**: Placeholder at x=1100, y=40, width=120px (Top right).

---

### 6. Title Area & Takeaway Box

- **Title text**: "Key Results: State-of-the-Art Translation Quality"
- **Position**: Left-aligned at x=105, y=65.
- **Font**: 40px, Bold, `#003D7C` (Microsoft YaHei).
- **Takeaway Box**:
    - **Position**: x=60, y=110, w=1160, h=45.
    - **Styling**: Fill `#003D7C` at 8% opacity, no border.
    - **Text**: "Transformer (big) achieves SOTA BLEU scores with significantly lower training costs (FLOPs) than previous RNN/CNN architectures."
    - **Font**: 18px, Bold, `#003D7C`.

---

### 7. Content Elements

#### Element [1]: Performance Comparison Table
**Component type**: Content Card (Table)
**Bounding box**: x=60, y=180, width=780, height=460
**Table Styling**:
- **Header Row 1**: y=180, h=40, fill `#003D7C`, text White (Bold, 16px).
- **Header Row 2**: y=220, h=40, fill `#0056A6`, text White (Bold, 14px).
- **Data Rows**: 10 rows, h=38 each. Alternating fill `#F4F7FA` and `#FFFFFF`.
- **Highlight Row**: Row 10 (Transformer big) fill `#E6EEF7`, border 1px `#003D7C`.
**Column Widths**:
- Model: 220px (Left-aligned)
- BLEU EN-DE: 100px (Centered)
- BLEU EN-FR: 100px (Centered)
- FLOPs EN-DE: 180px (Centered)
- FLOPs EN-FR: 180px (Centered)

#### Element [2]: Quality Insight Card
**Component type**: Content Card (Parallelogram)
**Bounding box**: x=880, y=180, width=340, height=210
**Card styling**:
- Fill: `#003D7C`, skew: -20°, border: none.
- **Ghost Outline**: x=890, y=190, width=340, height=210, fill: none, border: 1px `#003D7C`, skew: -20°.
- **Header text**: "TRANSLATION QUALITY", centered, 24px, Bold, White.
**Body content**:
- Line 1: "Achieves 28.4 BLEU (EN-DE) and"
- Line 2: "41.8 BLEU (EN-FR), surpassing"
- Line 3: "all previous ensemble models"
- Line 4: "by a significant margin."
- **Font**: size=18px, weight=normal, color=#FFFFFF, centered.
**Wrapping calculation**:
- Inner width: 300px (accounting for skew/padding).
- Chars per line (18px): ~30.
- Total chars: 92 → 4 lines.

#### Element [3]: Efficiency Insight Card
**Component type**: Content Card (Parallelogram)
**Bounding box**: x=880, y=420, width=340, height=210
**Card styling**:
- Fill: `#003D7C`, skew: -20°, border: none.
- **Ghost Outline**: x=890, y=430, width=340, height=210, fill: none, border: 1px `#003D7C`, skew: -20°.
- **Header text**: "TRAINING EFFICIENCY", centered, 24px, Bold, White.
**Body content**:
- Line 1: "Training cost is a fraction of"
- Line 2: "GNMT or ConvS2S, proving"
- Line 3: "attention-only models are"
- Line 4: "highly cost-effective."
- **Font**: size=18px, weight=normal, color=#FFFFFF, centered.
**Wrapping calculation**:
- Inner width: 300px.
- Chars per line (18px): ~30.
- Total chars: 98 → 4 lines.

---

### 8. Visual Emphasis

- **Primary Emphasis**: The "Transformer (big)" row in the table. It uses a light blue highlight and bold success-green text for the BLEU scores to immediately draw the eye to the record-breaking numbers.
- **Secondary Emphasis**: The two navy skewed cards on the right provide the "So What?" factor, translating the table's raw data into narrative claims.

---

### 9. Footer

- **Page number**: "10 / 15", x=1220, y=700, right-aligned, 14px, `#808080`.
- **Data source**: "Source: Vaswani et al. (2017), 'Attention Is All You Need', Table 2", x=60, y=700, 12px, `#808080`.
- **Footer Divider**: 1px solid `#003D7C` at y=680, width 1160px (centered).

---

### 10. Final Spacing & Narrative Check

- [x] Title is verbatim: "Key Results: State-of-the-Art Translation Quality" (49 chars).
- [x] Takeaway Box is present and contains the core assertion.
- [x] Table includes comparison models (GNMT, ConvS2S) as references.
- [x] Highlight strategy: Transformer (big) row is accented.
- [x] Body font size: 18px (Dense layout).
- [x] Safe zone: All elements between x=60 and x=1220.
- [x] No overlaps: 40px gap between table and right-side cards.
- [x] Text wrapping: All card text pre-split into lines of ~30 characters.
- [x] Data source footer included.