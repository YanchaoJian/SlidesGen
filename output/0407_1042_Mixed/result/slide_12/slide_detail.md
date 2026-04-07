## 1. Page Meta

- **Page role**: `data`
- **Style tier**: `B. General Consulting` (Signal: data-driven, structured table, academic tone)
- **Content density**: Dense (4 points + table) → 18px body
- **Layout mode**: `left_right_split`
- **Rationale**: The table provides the empirical evidence (data), while the right-hand cards provide the narrative argument (the "why"). This split allows for a clear, side-by-side comparison of evidence and insight.

---

## 2. Narrative & Argument Plan

- **Core conclusion**: The Transformer architecture generalizes effectively to English constituency parsing, achieving state-of-the-art results without explicit inductive biases.
- **Title**: "Generalization: English Constituency Parsing"
- **Takeaway Box text**: "Transformer achieves state-of-the-art 92.7 F1 in constituency parsing, proving its ability to learn structural grammar."
- **Supporting arguments**:
    1. Competitive performance on structural tasks.
    2. Outperforms previous SOTA in semi-supervised settings.
    3. Learns task-specific structures without explicit inductive biases.

---

## 3. Data Contextualization Plan

| Metric label | Hero value | Comparison reference | Meaning annotation |
|--------------|-----------|---------------------|-------------------|
| Transformer F1 | 92.7 | Previous SOTA 92.1 | Outperforms SOTA by 0.6 pts |

- **Table Highlight Strategy**: The row "Transformer (4 layers) | semi-supervised | 92.7" will be highlighted with a `#0056A6` background fill and white text to draw the eye. All other rows remain neutral gray/white.

---

## 5. Background & Decorations

- **Background**: `#F8F9FA` with a subtle 40px grid pattern in `#E9ECEF`.
- **Top accent bar**: Full-width, y=95, height=4px, color=`#003D7C`.
- **Header Icon**: Parallelogram (40x40px, skew -20°) at x=40, y=50, color=`#003D7C`.

---

## 6. Title Area & Takeaway Box

- **Title text**: "Generalization: English Constituency Parsing"
- **Position**: Left-aligned at x=90, y=60, font=40px, weight=Bold, color=`#003D7C`.
- **Takeaway Box**: x=40, y=110, w=1200, h=45, rx=0, fill=`#E6EEF7`.
- **Takeaway Text**: "Transformer achieves state-of-the-art 92.7 F1 in constituency parsing, proving its ability to learn structural grammar.", font=15px, weight=Bold, color=`#003D7C`, centered vertically in box.

---

## 7. Content Elements

### Element 1: Table (Left)
- **Component type**: Content Card (Table)
- **Bounding box**: x=40, y=170, w=600, h=480
- **Header row**: height=40px, fill=`#003D7C`, text=`#FFFFFF`
- **Data rows**: height=35px, alternating fill=`#F4F7FA`
- **Highlight row**: Row 10 (Transformer semi-supervised), fill=`#0056A6`, text=`#FFFFFF`
- **Column widths**: Parser (300px), Training (180px), F1 (120px)

### Element 2: Argument Cards (Right)
- **Component type**: 3 Parallelogram Cards (skew -20°)
- **Bounding box**: x=680, y=170, w=560, h=480
- **Card 1 (x=680, y=170, w=560, h=140)**:
    - Header: "Structural Competence"
    - Body: "Despite strong structural constraints, the Transformer achieved competitive results."
- **Card 2 (x=680, y=330, w=560, h=140)**:
    - Header: "SOTA Performance"
    - Body: "In a semi-supervised setting, it achieved 92.7 F1, outperforming previous state-of-the-art models."
- **Card 3 (x=680, y=490, w=560, h=140)**:
    - Header: "Inductive Bias"
    - Body: "Demonstrates that attention learns task-specific structures without explicit inductive biases."

**Wrapping Calculation (for cards):**
- Container inner width: 520px
- Chars per line (18px): ~45 chars
- Text block height: 3 lines × 18px × 1.4 = ~76px (Fits within 140px card)

---

## 8. Visual Emphasis

- **Emphasis**: The table's highlighted row and the Takeaway Box are the primary focus.
- **Accent**: Use `#0056A6` for the highlighted table row and the card headers to maintain the "Dalian University" academic blue theme.

---

## 9. Footer

- **Page number**: "12/12", x=1240, y=700, right-aligned, font=14px, color=`#808080`.
- **Data source**: "Source: Table 4, Section 23 of WSJ", x=40, y=700, font=14px, color=`#808080`.

---

## 10. Final Spacing & Narrative Check

- [x] Title is verbatim and ≤ 50 chars.
- [x] Takeaway Box is present and carries the assertion.
- [x] Metric has comparison (92.7 vs 92.1).
- [x] Table highlight strategy is defined.
- [x] Body font size is 18px (dense).
- [x] All elements within safe zone (x: 40–1240, y: 40–680).
- [x] No bounding boxes overlap (20px gap maintained).
- [x] Data source footer present.