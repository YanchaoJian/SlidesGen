### 1. Page Meta
- **Page role**: `complication`
- **Style tier inferred**: `C. Top Consulting (MBB)` — Inferred from the "Academic Blue" theme's extreme structural restraint, geometric precision (skewed parallelograms), and formal institutional tone.
- **Content density**: `Dense` (4 points + 1 complex table) → 18px body baseline.
- **Layout mode**: `left_right_split` (45:55 split)
- **Rationale**: The slide identifies a technical bottleneck (complication). A split layout allows for the qualitative problems (left) to be directly benchmarked against the quantitative complexity table (right), proving the "bottleneck" argument.

---

### 2. Narrative & Argument Plan
- **Core conclusion**: Recurrent models' sequential nature creates an $O(n)$ bottleneck in both computation and path length, which Self-Attention overcomes with $O(1)$ parallelization.
- **Title**: "The Problem: Sequential Computation Bottlenecks"
- **Takeaway Box text**: Recurrent models face $O(n)$ sequential constraints; Self-Attention enables full parallelization and constant-time global dependency linking for long sequences.
- **Supporting arguments**:
    1. Sequential processing inhibits parallel training.
    2. Hidden state chains create memory bottlenecks for long sequences.
    3. Convolutional models improve parallelization but fail at long-range global context.
    4. Path length between distant positions grows linearly in RNNs, hindering learning.

---

### 3. Data Contextualization Plan

| Metric label | Hero value | Comparison reference | Meaning annotation |
|--------------|-----------|---------------------|-------------------|
| RNN Seq. Ops | $O(n)$ | Self-Attention: $O(1)$ | Linear scaling prevents parallelization |
| RNN Path Length | $O(n)$ | Self-Attention: $O(1)$ | Harder to learn long-range dependencies |
| Complexity (n < d) | $O(n^2 \cdot d)$ | Recurrent: $O(n \cdot d^2)$ | Self-Attention is faster for typical sequence lengths |

- **Chart type**: Comparison Table (Table 1).
- **Highlight strategy**: Row 1 (Self-Attention) highlighted in Success Green (`#28A745`) text/border to show the solution; Row 2 (Recurrent) highlighted with a subtle Warning Red (`#DC3545`) border to emphasize the "Problem".

---

### 4. Background & Decorations
- **Background**: `#F8F9FA` (Off-white) with a subtle `#E9ECEF` grid pattern (40px spacing).
- **Top accent bar**: Full-width (1280px), height 2px, color `#003D7C` at y=95.
- **Header Icon**: Skewed parallelogram (skew -20°) at x=60, y=40, size 40x40, color `#003D7C`, containing 3 white horizontal lines.
- **University Logo**: Placeholder at x=1100, y=40, width=120px (Institutional branding).

---

### 5. Title Area & Takeaway Box
- **Title text**: "The Problem: Sequential Computation Bottlenecks"
- **Position**: x=110, y=65 (Left-aligned, following the icon).
- **Font**: 40px, Bold, `#003D7C` (Microsoft YaHei).
- **Takeaway Box**: 
    - **Box**: x=60, y=110, w=1160, h=50, fill=`#003D7C` (opacity 0.08), no border.
    - **Text**: "Recurrent models face O(n) sequential constraints; Self-Attention enables parallelization and constant-time global dependency linking."
    - **Font**: 18px, Bold, `#003D7C`, centered.

---

### 6. Content Elements: Left Column (Problem Points)

#### Elements [1-4]: Problem Cards
**Component type**: Content Card (Parallelogram)
- **Shape**: Rectangle skewed -20° horizontally.
- **Styling**: Fill `#003D7C`, no border.
- **Ghost Shadow**: Offset +10px (down/right), 1px stroke `#003D7C`, no fill.
- **Dimensions**: x=60, width=500, height=100.
- **Text Styling**: 18px, Normal, `#FFFFFF`, strictly centered.

**Element 1: Parallelization (y=180)**
- Line 1: "Sequential processing prevents"
- Line 2: "parallelization within training examples,"
- Line 3: "leading to massive training times."

**Element 2: Memory (y=295)**
- Line 1: "Memory constraints become critical for"
- Line 2: "long sequences as the model must"
- Line 3: "maintain a chain of hidden states."

**Element 3: Convolution (y=410)**
- Line 1: "Convolutional alternatives attempt"
- Line 2: "parallelization but struggle with"
- Line 3: "long-range dependencies."

**Element 4: Distance (y=525)**
- Line 1: "The computational cost to link distant"
- Line 2: "positions grows with distance, making"
- Line 3: "it hard to learn global context."

---

### 7. Content Elements: Right Column (Complexity Table)

#### Element [5]: Complexity Comparison Table
**Component type**: Content Card (Table)
- **Bounding box**: x=620, y=180, width=600, height=445.
- **Card styling**: White background, 1px `#003D7C` border, no skew on the table itself (for readability), but placed inside a skewed container frame.

**Table Structure**:
- **Header Row (y=180, h=50)**: Fill `#003D7C`, Text `#FFFFFF` (16px Bold).
    - Col 1 (200px): "Layer Type"
    - Col 2 (150px): "Complexity / Layer"
    - Col 3 (120px): "Seq. Ops"
    - Col 4 (130px): "Max Path"
- **Row 1 (Self-Attention)**: Fill `#E6EEF7` (Secondary Accent).
    - Text: "Self-Attention", "$O(n^2 \cdot d)$", "$O(1)$", "$O(1)$"
    - *Highlight*: Text color `#28A745` (Success) for $O(1)$ values.
- **Row 2 (Recurrent)**: Fill `#FFFFFF`.
    - Text: "Recurrent", "$O(n \cdot d^2)$", "$O(n)$", "$O(n)$"
    - *Highlight*: Border `#DC3545` (Warning) around this row.
- **Row 3 (Convolutional)**: Fill `#F4F7FA`.
    - Text: "Convolutional", "$O(k \cdot n \cdot d^2)$", "$O(1)$", "$O(log_k(n))$"
- **Row 4 (Restricted)**: Fill `#FFFFFF`.
    - Text: "Self-Atten. (restr.)", "$O(r \cdot n \cdot d)$", "$O(1)$", "$O(n/r)$"

**Table Caption**:
- Position: x=620, y=635, font 14px, color `#808080`.
- Text: "Table 1: Comparison of layer types in terms of complexity and sequential operations."

---

### 8. Visual Emphasis
- **Primary Emphasis**: The "Recurrent" row in the table is outlined in `#DC3545` (Red) to visually signal the "Problem" mentioned in the title.
- **Secondary Emphasis**: The "Self-Attention" row uses `#28A745` (Green) for its $O(1)$ metrics to show the superior alternative.
- **Geometric Theme**: All 4 problem cards on the left use the -20° skew and ghost outline to maintain the "Academic Blue" institutional style.

---

### 9. Footer
- **Divider**: 1px solid `#003D7C` at y=680.
- **Motto**: "Self-discipline and Social Commitment" at x=60, y=700, font 14px, color `#808080`.
- **Page Number**: "3 / 12" at x=1220, y=700, font 14px, color `#808080`.
- **Data Source**: "Source: Vaswani et al. (2017) 'Attention Is All You Need'" at x=400, y=700, font 10px, color `#808080`.

---

### 10. Final Spacing & Narrative Check
- [x] Title is verbatim and fits one line.
- [x] Takeaway box clarifies the "Problem" vs "Solution" immediately.
- [x] Table metrics are contextualized with $O(1)$ vs $O(n)$ comparisons.
- [x] All elements are within the 40-1240 / 40-680 safe zone.
- [x] 20px gap maintained between the left card stack and the right table.
- [x] Text in skewed cards is pre-split into 3 lines to ensure centering and no clipping.