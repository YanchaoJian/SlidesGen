### 1. Page Meta

- **Page role**: `method` (Explains the process/logic of the training schedule)
- **Style tier inferred**: **B. General Consulting** — Cited signal: "corporate-traditional", "academic", "structured", "data-driven" tone in Design Specification.
- **Content density**: **Dense** (7 content points + 1 equation) → Body baseline **18px**.
- **Layout mode**: `left_right_split` — Left zone for the Equation (Visual Hero), Right zone for 3 stacked explanation cards (Logic Flow).
- **Rationale**: The equation is the core "method" artifact and requires visual prominence (Left). The 7 bullet points logically group into 3 phases (Warmup, Decay, Impact), fitting perfectly into 3 stacked cards on the Right. This balances visual weight and ensures readability of the dense text.

---

### 2. Narrative & Argument Plan

- **Core conclusion (one sentence)**: "Warmup prevents early divergence while inverse-square-root decay ensures efficient convergence."
- **Title (KEEP verbatim)**: "Training Optimization: Learning Rate Schedule" (43 characters)
- **Takeaway Box text**: "Warmup prevents early divergence; inverse-square-root decay enables fine convergence."
- **Supporting arguments**:
    1.  **Warmup Phase**: Linear increase for first 4000 steps prevents instability.
    2.  **Decay Phase**: Proportional decrease (inverse square root) refines learning.
    3.  **Optimization**: Combined with Adam, enables faster convergence than fixed rates.

---

### 3. Data Contextualization Plan

- **Metric**: `warmup_steps`
    - **Hero value**: 4000
    - **Comparison reference**: Standard baseline for Transformer models
    - **Meaning annotation**: "Fixed for all experiments to ensure stability"
- **Chart/Visual**: Equation acts as the "Data".
    - **Highlight strategy**: Accent color (`#005587`) on the `warmup_steps` variable within the equation to link it to the first explanation card.

---

### 4. Image Plan

- **N/A**: No external image file. The Equation is rendered as text/SVG shapes within a card.

---

### 5. Background & Decorations

- **Background**: Color `#FFFFFF` (White)
- **Top accent bar**: Full-width (1280px), height 6px, color `#005587` (Primary), y=0
- **Decorative elements**: None (Minimalist academic style per Design Spec).
- **Grid**: 20px base unit alignment.

---

### 6. Title Area & Takeaway Box

- **Title text**: "Training Optimization: Learning Rate Schedule"
- **Position**: Centered at x=640, y=50 (Baseline)
- **Font**: Size 36px, Weight Bold, Color `#005587`
- **Takeaway Box**:
    - **Position**: x=40, y=95, width=1200, height=50
    - **Style**: Fill `#F1F5F9` (Light Gray-Blue, 10% opacity of primary), Border Left 4px `#005587`
    - **Text**: "Warmup prevents early divergence; inverse-square-root decay enables fine convergence."
    - **Font**: Size 16px, Weight Bold, Color `#005587`
    - **Alignment**: Left-aligned, padding-left 20px, vertical-center

---

### 7. Content Elements

#### Element 1: Equation Card (Left Zone)

**Component type**: Content Card (White body, Blue Header Strip)
**Bounding box**: x=40, y=160, width=580, height=480
**Card styling**:
- Fill: `#FFFFFF`, Border: `#005587` (1px), Radius: 8px
- Header strip: Height 6px, Top edge, Color `#005587`
- Header text: "Learning Rate Formula", Left-aligned, x=60, y=185, Font 20px Bold `#005587`

**Body content** (Equation Rendered as Text):
- **Line 1**: "lrate = d_model^(-0.5) · min(step_num^(-0.5),"
- **Line 2**: "           step_num · warmup_steps^(-1.5))"
- **Font**: Size 20px, Weight Normal, Color `#334155` (Dark Slate for readability)
- **Line height**: 1.5em
- **Position**: x=60, y=230
- **Highlight**: The term `warmup_steps` in Line 2 should be colored `#005587` (Accent) to draw attention.

**Context Text** (Below Equation):
- **Line 1**: "Used warmup_steps = 4000 for all experiments."
- **Font**: Size 16px, Weight Normal, Color `#64748B` (Secondary Text)
- **Position**: x=60, y=300
- **Decoration**: Small Info Badge background `#F1F5F9`, padding 10px, radius 4px.

**Wrapping Calculation**:
- Container inner width: 580 - 40 (padding) = 540px.
- Equation is pre-broken into 2 logical lines.
- Context text: 49 chars. 540 / (16*0.55) ≈ 61 chars/line. Fits on 1 line.

#### Element 2: Warmup Phase Card (Right Zone, Top)

**Component type**: Content Card
**Bounding box**: x=660, y=160, width=580, height=140
**Card styling**:
- Fill: `#FFFFFF`, Border: `#E2E8F0` (Light Gray), Radius: 8px
- Header strip: Height 6px, Top edge, Color `#005587`
- Header text: "1. Warmup Phase", Left-aligned, x=680, y=185, Font 18px Bold `#005587`

**Body content**:
- **Line 1**: "Corresponds to increasing learning rate linearly"
- **Line 2**: "for first warmup_steps training steps."
- **Font**: Size 18px, Weight Normal, Color `#334155`
- **Line height**: 1.5em
- **Position**: x=680, y=215

**Wrapping Calculation**:
- Container inner width: 580 - 40 = 540px.
- Max chars/line (18px): 540 / 9.9 ≈ 54 chars.
- Line 1: 49 chars (Fits).
- Line 2: 39 chars (Fits).
- Total height needed: 2 lines * 27px + padding ≈ 90px. Card height 140px is sufficient.

#### Element 3: Decay Phase Card (Right Zone, Middle)

**Component type**: Content Card
**Bounding box**: x=660, y=320, width=580, height=140
**Card styling**:
- Fill: `#FFFFFF`, Border: `#E2E8F0`, Radius: 8px
- Header strip: Height 6px, Top edge, Color `#005587`
- Header text: "2. Decay Phase", Left-aligned, x=680, y=345, Font 18px Bold `#005587`

**Body content**:
- **Line 1**: "Then decreasing it thereafter proportionally"
- **Line 2**: "to inverse square root of step number."
- **Font**: Size 18px, Weight Normal, Color `#334155`
- **Line height**: 1.5em
- **Position**: x=680, y=375

**Wrapping Calculation**:
- Line 1: 47 chars (Fits).
- Line 2: 43 chars (Fits).
- Fits within 140px height.

#### Element 4: Optimization Impact Card (Right Zone, Bottom)

**Component type**: Content Card
**Bounding box**: x=660, y=480, width=580, height=160
**Card styling**:
- Fill: `#FFFFFF`, Border: `#E2E8F0`, Radius: 8px
- Header strip: Height 6px, Top edge, Color `#005587`
- Header text: "3. Optimization Impact", Left-aligned, x=680, y=505, Font 18px Bold `#005587`

**Body content**:
- **Line 1**: "Combined with Adam optimizer enables efficient"
- **Line 2**: "training of the architecture. Allows model to"
- **Line 3**: "reach convergence faster than fixed rate approaches."
- **Font**: Size 18px, Weight Normal, Color `#334155`
- **Line height**: 1.5em
- **Position**: x=680, y=535

**Wrapping Calculation**:
- Line 1: 49 chars (Fits).
- Line 2: 43 chars (Fits).
- Line 3: 53 chars (Fits, borderline).
- Total height: 3 lines * 27px + padding ≈ 120px. Card height 160px is sufficient.

---

### 8. Visual Emphasis

- **Primary Emphasis**: The **Equation Card** (Left). It is taller (480px vs 140px) and contains the mathematical "truth".
- **Secondary Emphasis**: The term `warmup_steps` inside the equation and the Header of Card 1 ("Warmup Phase").
- **Method**: Use Primary Color `#005587` for the equation highlight and card headers. All other text is neutral dark gray `#334155`.

---

### 9. Footer

- **Page number**: "11", Position x=1240, y=700, Right-aligned, Font 12px, Color `#94A3B8`
- **Data source**: "Source: Transformer Model Training Specs", Position x=40, y=700, Font 10px, Color `#94A3B8`

---

### 10. Final Spacing & Narrative Check

- [x] Title is copied verbatim ("Training Optimization: Learning Rate Schedule") and is ≤ 50 characters.
- [x] Takeaway Box is present directly under the title (y=95) with the assertion.
- [x] Metric `warmup_steps = 4000` is highlighted in the Equation Card context.
- [x] Layout uses `left_right_split` to separate Formula (Left) from Logic (Right).
- [x] Colors: Primary `#005587`, Background `#FFFFFF`, Text `#334155`/`#64748B`. (≤ 3 colors).
- [x] Body font size 18px matches Dense content rule.
- [x] All elements within safe zone (x: 40–1240, y: 40–680).
    - Left Card Bottom: 160 + 480 = 640 (Fits).
    - Right Card Bottom: 480 + 160 = 640 (Fits).
- [x] No bounding boxes overlap (40px gap between Left/Right zones).
- [x] All text pre-split into lines (verified char counts).
- [x] Data source footer present.