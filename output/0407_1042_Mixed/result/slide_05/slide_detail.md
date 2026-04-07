### 1. Page Meta

- **Page role**: `method`
- **Style tier inferred**: B. General Consulting / Academic (Inferred from "formal, institutional, highly structured", "academic paper feel", and strict geometric rules).
- **Content density**: Relaxed (4 points + 1 equation) → 20px body font (overriding standard 24px to strictly follow the Design Specification's typography system).
- **Layout mode**: `card_grid_3col` (with a hero equation box on top)
- **Rationale**: The slide explains a technical mechanism (method). Placing the core equation centrally at the top establishes the mathematical foundation, while the 3-column skewed card grid below breaks down the three logical steps (Inputs, Scaling, Output) in a highly structured, academic format.

---

### 2. Narrative & Argument Plan

- **Core conclusion**: The scaling factor in dot-product attention prevents vanishing gradients, ensuring stable training for high-dimensional data.
- **Title**: "Technical Detail: Scaled Dot-Product Attention"
- **Takeaway Box text**: "Scaling the dot product by 1/sqrt(d_k) prevents vanishing gradients, ensuring stable training in high dimensions."
- **Supporting arguments**:
  1. Queries (Q) and Keys (K) compute initial compatibility scores.
  2. The scaling factor stabilizes the softmax function.
  3. The final output is a weighted sum of the Values (V).

---

### 3. Data Contextualization Plan

*(No raw metrics or charts on this slide; the focus is on the mathematical equation and its components.)*

---

### 4. Image Plan

*(No images included in the slide plan.)*

---

### 5. Background & Decorations

- **Background**: `#F8F9FA` (Institutional off-white).
- **Background Grid**: A subtle grid pattern with 40px spacing, line color `#E9ECEF`, covering the entire canvas.
- **Top Accent Bar**: Full-width horizontal line, x=0, y=100, width=1280, height=2px, color=`#003D7C`.
- **Header Icon**: A parallelogram at x=60, y=50, width=30, height=40, `transform="skewX(-20deg)"`, fill=`#003D7C`. Inside the icon, three horizontal white lines (height=2px, width=16px) spaced 6px apart to represent a document.
- **Footer Divider**: Full-width horizontal line, x=60, y=640, width=1160, height=1px, color=`#003D7C`.

---

### 6. Title Area & Takeaway Box

- **Title text**: "Technical Detail: Scaled Dot-Product Attention"
- **Position**: Left-aligned at x=110, y=80 (leaving room for the header icon).
- **Font**: 40px, Bold, `#003D7C`.
- **Takeaway Box**:
  - Bounding box: x=60, y=115, width=1160, height=45, rx=0.
  - Fill: `#E6EEF7` (Secondary accent).
  - Text: "Scaling the dot product by 1/sqrt(d_k) prevents vanishing gradients, ensuring stable training in high dimensions."
  - Text format: Centered at x=640, y=143, 16px, Bold, `#003D7C`.

---

### 7. Content Elements

#### Element 1: Hero Equation Box
**Component type**: Info Box (Geometric)
**Bounding box**: x=240, y=190, width=800, height=120
**Styling**:
- Base shape: Rectangle with `transform="skewX(-20deg)"`.
- Fill: `#FFFFFF`, Border: 2px solid `#003D7C`.
- Shadow/Ghost outline: A secondary parallelogram (no fill, 1px `#003D7C` stroke) shifted +10px on X and +10px on Y.
**Equation text**:
- Text: "Attention(Q, K, V) = softmax( (Q K^T) / sqrt(d_k) ) V"
- Position: Centered at x=640, y=258 (Note: Text must NOT be skewed; apply skew only to the background shape, or reverse-skew the text container).
- Font: 28px, Bold, `#003D7C`.

#### Element 2: Step 1 Card (Compatibility)
**Component type**: Content Card (Parallelogram)
**Bounding box**: x=60, y=360, width=360, height=240
**Card styling**:
- Base shape: Rectangle with `transform="skewX(-20deg)"`.
- Fill: `#003D7C`.
- Shadow/Ghost outline: Secondary parallelogram (no fill, 1px `#003D7C` stroke) shifted +10px on X and +10px on Y.
**Header text**:
- Text: "1. Compatibility"
- Position: Centered at x=240, y=410 (Un-skewed).
- Font: 28px, Bold, `#FFFFFF`.
**Body content** (Un-skewed, centered at x=240):
- Line 1: "Queries (Q) and Keys (K)"
- Line 2: "compute the initial"
- Line 3: "compatibility scores."
- Font: size=20px, weight=normal, color=`#FFFFFF`.
- Line height: 1.4em (28px). First line starts at y=460.
**Wrapping calculation**:
- Container safe inner width: ~260px (accounting for 20-degree skew loss).
- Chars per line at 20px: ~23.
- Line 1 (24 chars) fits tightly; Line 2 (19 chars) fits; Line 3 (21 chars) fits.

#### Element 3: Step 2 Card (Scaling Factor)
**Component type**: Content Card (Parallelogram)
**Bounding box**: x=460, y=360, width=360, height=240
**Card styling**:
- Base shape: Rectangle with `transform="skewX(-20deg)"`.
- Fill: `#003D7C`.
- Shadow/Ghost outline: Secondary parallelogram (no fill, 1px `#003D7C` stroke) shifted +10px on X and +10px on Y.
**Header text**:
- Text: "2. Scaling Factor"
- Position: Centered at x=640, y=410 (Un-skewed).
- Font: 28px, Bold, `#FFFFFF`.
**Body content** (Un-skewed, centered at x=640):
- Line 1: "Dividing by sqrt(d_k)"
- Line 2: "prevents large dot"
- Line 3: "products & vanishing"
- Line 4: "gradients in softmax."
- Font: size=20px, weight=normal, color=`#FFFFFF`.
- Line height: 1.4em (28px). First line starts at y=460.
**Wrapping calculation**:
- Line 1 (21 chars), Line 2 (18 chars), Line 3 (20 chars), Line 4 (21 chars). All fit within 260px safe width.

#### Element 4: Step 3 Card (Final Output)
**Component type**: Content Card (Parallelogram)
**Bounding box**: x=860, y=360, width=360, height=240
**Card styling**:
- Base shape: Rectangle with `transform="skewX(-20deg)"`.
- Fill: `#003D7C`.
- Shadow/Ghost outline: Secondary parallelogram (no fill, 1px `#003D7C` stroke) shifted +10px on X and +10px on Y.
**Header text**:
- Text: "3. Final Output"
- Position: Centered at x=1040, y=410 (Un-skewed).
- Font: 28px, Bold, `#FFFFFF`.
**Body content** (Un-skewed, centered at x=1040):
- Line 1: "The resulting weights"
- Line 2: "are multiplied by"
- Line 3: "Values (V) to form"
- Line 4: "the final output."
- Font: size=20px, weight=normal, color=`#FFFFFF`.
- Line height: 1.4em (28px). First line starts at y=460.
**Wrapping calculation**:
- Line 1 (21 chars), Line 2 (17 chars), Line 3 (18 chars), Line 4 (17 chars). All fit within 260px safe width.

---

### 8. Visual Emphasis

- **Hero Element**: The central equation box is the focal point, isolated with ample whitespace and framed by a geometric border.
- **Thematic Consistency**: The strict adherence to the -20 degree skew on all containers (header icon, equation box, and the three content cards) creates the highly structured, academic rhythm requested in the design spec.
- **Depth**: The +10px hard-edge "ghost" outlines on all major shapes provide the required geometric depth without using soft drop shadows.

---

### 9. Footer

- **Motto / Institution**: text="Dalian University", position left-aligned at x=60, y=680, font size=14px, color=`#808080`.
- **Page number**: text="5", position right-aligned at x=1220, y=680, font size=14px, color=`#808080`.
- **Decorative carryover**: A large navy blue parallelogram in the bottom right corner (x=1240, y=680, width=60, height=40, `transform="skewX(-20deg)"`, fill=`#003D7C`, opacity=0.1) to anchor the page.

---

### 10. Final Spacing & Narrative Check

- [x] Title is copied verbatim and fits on one line (46 chars).
- [x] Takeaway Box is present directly under the title with the core assertion.
- [x] Equation is prominently displayed and accurately transcribed.
- [x] Strict adherence to the Dalian University Academic Blue theme (colors, typography, -20deg skew, hard-edge offsets).
- [x] Body font size is 20px, matching the specific theme typography rules.
- [x] All elements are within the safe zone (y-coordinates range from 50 to 680).
- [x] No bounding boxes overlap (Equation box ends at y=310; Cards start at y=360, leaving a 50px gap).
- [x] All text has been pre-split into lines that fit their skewed containers.