### 1. Page Meta

- **Page role**: `method`
- **Style tier inferred**: **C. Top Consulting (MBB)** — The design spec emphasizes "academic," "institutional," "highly structured," and uses a "geometric precision" with a "ghost outline" effect, which aligns with high-end, structured strategic/technical reporting.
- **Content density**: **Relaxed** (4 bullet points + 1 equation) → **20px body baseline** (per design spec typography table).
- **Layout mode**: `card_grid_3col` (adapted for 3 main conceptual blocks + 1 equation block).
- **Rationale**: The content explains a technical process (FFN). A structured grid of skewed cards fits the "academic blue" theme while organizing the "what, how, and where" of the FFN.

---

### 2. Narrative & Argument Plan

- **Core conclusion**: The FFN provides essential position-wise non-linearity to the Transformer architecture through identical but independent processing.
- **Title**: Technical Detail: Position-wise Feed-Forward Networks
- **Takeaway Box text**: FFNs apply identical transformations to each position independently, introducing non-linearity via ReLU between two linear layers.
- **Supporting arguments**:
    1. **Universal Application**: Applied to every position in both encoder and decoder layers.
    2. **Architecture**: Two-step linear transformation with a ReLU activation bottleneck.
    3. **Parameterization**: Weights are shared across positions but unique to each layer.

---

### 3. Data Contextualization Plan
*Not applicable (No quantitative metrics provided).*

---

### 4. Image Plan
*Not applicable (No figure provided).*

---

### 5. Background & Decorations

- **Background**: `#F8F9FA` (Institutional off-white).
- **Grid Pattern**: 40px dot grid in `#E9ECEF` across the content area.
- **Top Accent Bar**: Thin navy blue line (2px) at y=95, spanning x=0 to 1280.
- **Header Icon**: Navy blue parallelogram (40x40px, skew -20°) at x=60, y=40, containing three white horizontal lines.
- **University Logo**: Placeholder for DUT logo at x=1100, y=40, width=120px.

---

### 6. Title Area & Takeaway Box

- **Title text**: "Technical Detail: Position-wise Feed-Forward Networks"
- **Position**: x=110, y=65 (Left-aligned, following the icon).
- **Font**: 40px, Bold, `#003D7C` (DUT Brand Blue).
- **Takeaway Box**:
    - **Box**: x=60, y=110, w=1160, h=45, fill=`#003D7C` (8% opacity), no border.
    - **Text**: "FFNs apply identical transformations to each position independently, introducing non-linearity via ReLU between two linear layers."
    - **Font**: 18px, Bold, `#003D7C`.

---

### 7. Content Elements

#### Element [1]: Application Card (Left)
- **Component type**: Content Card (Skewed Parallelogram)
- **Bounding box**: x=60, y=180, width=360, height=220
- **Card styling**:
    - **Fill**: `#003D7C` (Primary Navy), **Skew**: -20°
    - **Ghost Outline**: x=70, y=190, width=360, height=220, stroke=`#003D7C` (1px), no fill.
- **Header text**: "APPLICATION", centered, 24px, Bold, `#FFFFFF`.
- **Body content**:
    - Line 1: "Applied to each position"
    - Line 2: "separately and identically"
    - Line 3: "across encoder and"
    - Line 4: "decoder layers."
    - Font: 20px, Normal, `#FFFFFF`, Line height: 1.4em.
- **Wrapping calculation**: Inner width ~300px. Chars/line (Latin) @ 20px: ~30. Text fits comfortably.

#### Element [2]: Structure Card (Center)
- **Component type**: Content Card (Skewed Parallelogram)
- **Bounding box**: x=460, y=180, width=360, height=220
- **Card styling**:
    - **Fill**: `#003D7C`, **Skew**: -20°
    - **Ghost Outline**: x=470, y=190, width=360, height=220, stroke=`#003D7C` (1px).
- **Header text**: "STRUCTURE", centered, 24px, Bold, `#FFFFFF`.
- **Body content**:
    - Line 1: "Two linear transformations"
    - Line 2: "with a ReLU activation"
    - Line 3: "function in between."
    - Font: 20px, Normal, `#FFFFFF`, Line height: 1.4em.
- **Wrapping calculation**: Inner width ~300px. Chars/line: ~30. Text fits.

#### Element [3]: Parameters Card (Right)
- **Component type**: Content Card (Skewed Parallelogram)
- **Bounding box**: x=860, y=180, width=360, height=220
- **Card styling**:
    - **Fill**: `#003D7C`, **Skew**: -20°
    - **Ghost Outline**: x=870, y=190, width=360, height=220, stroke=`#003D7C` (1px).
- **Header text**: "PARAMETERS", centered, 24px, Bold, `#FFFFFF`.
- **Body content**:
    - Line 1: "Same across positions,"
    - Line 2: "but different parameters"
    - Line 3: "from layer to layer."
    - Font: 20px, Normal, `#FFFFFF`, Line height: 1.4em.
- **Wrapping calculation**: Inner width ~300px. Chars/line: ~30. Text fits.

#### Element [4]: Equation Block
- **Component type**: Info Box (Geometric)
- **Bounding box**: x=60, y=460, width=1160, height=160
- **Card styling**:
    - **Fill**: `#F4F7FA` (Secondary bg), border-left: 8px solid `#003D7C`.
- **Equation text**:
    - Line 1: "FFN(x) = max(0, xW₁ + b₁)W₂ + b₂"
    - Font: 32px, Bold, `#1A1A1A` (Body text), Centered at x=640, y=530.
- **Context text**:
    - Line 1: "The linear transformations are applied to each position identically."
    - Font: 16px, Normal, `#808080` (Tertiary), Centered at x=640, y=580.

---

### 8. Visual Emphasis

- **Visual Weight**: The Equation Block (Element 4) and the three Navy cards carry equal weight to show the "Logic + Math" relationship.
- **Emphasis**: The use of the DUT Navy (`#003D7C`) for the cards creates a strong institutional anchor, while the equation is highlighted by the light secondary background and the heavy left-border accent.

---

### 9. Footer

- **Motto**: "Dalian University of Technology" at x=60, y=700, font 14px, color `#808080`.
- **Page number**: "7 / 12" at x=1220, y=700, right-aligned, font 14px, color `#808080`.
- **Divider**: 1px solid `#003D7C` at y=680, from x=60 to 1220.

---

### 10. Final Spacing & Narrative Check

- [x] Title is verbatim: "Technical Detail: Position-wise Feed-Forward Networks" (50 chars).
- [x] Takeaway Box is present at y=110.
- [x] No metrics present; no comparison needed.
- [x] No charts present.
- [x] No images present.
- [x] Colors: Navy (#003D7C), Off-white (#F8F9FA), Gray (#808080). (3 total).
- [x] Body font: 20px (Relaxed density).
- [x] Safe zone: All elements between x=60 and x=1220, y=40 and y=700.
- [x] No overlaps: 40px gap between cards; 60px gap between card row and equation block.
- [x] Text pre-split: All card text split into 3-4 lines.