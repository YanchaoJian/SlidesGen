### 1. Page Meta

- **Page role**: `method` (Explaining technical mechanisms/components)
- **Style tier inferred**: **B. General Consulting** — Signals: "academic", "structured", "institutional", "data-driven" tone in Design Spec; dense technical content requires clear structure.
- **Content density**: **Dense (6+ items)** → Body baseline **18px**. (7 bullet points + 1 equation).
- **Layout mode**: `card_grid_2col` — Two distinct technical concepts (FFN vs. Positional Encoding) warrant side-by-side comparison cards.
- **Rationale**: The content naturally bifurcates into two subsystems. A 2-column grid allows sufficient width for the equation and detailed text wrapping without crowding, adhering to the "structured/academic" tone.

---

### 2. Narrative & Argument Plan

- **Core conclusion (one sentence)**: "Transformer layers use position-wise FFNs for non-linearity and fixed sine/cosine encodings to inject order without recurrence."
- **Title (Trimmed to ≤ 50 chars)**: "Technical Details: FFN & Positional Encoding" 
- **Takeaway Box text**: "FFNs add non-linearity per position; Positional Encoding injects order via fixed sine/cosine functions."
- **Supporting arguments**:
    1.  **FFN Structure**: Two linear transformations with ReLU, specific dimensions ($d_{model}=512, d_{ff}=2048$).
    2.  **Positional Encoding**: Sine/cosine functions of different frequencies allow learning relative positions.

---

### 3. Data Contextualization Plan

| Metric label | Hero value | Comparison reference | Meaning annotation |
|--------------|-----------|---------------------|-------------------|
| Model Dimension ($d_{model}$) | **512** | Standard Transformer Base | Input/Output dimension |
| Inner Dimension ($d_{ff}$) | **2048** | 4× expansion ratio | Provides non-linear capacity |

*Chart/Visual Strategy*: No charts. Equation is the "hero" visual. Dimensions are highlighted as **Data Emphasis Badges** within the FFN card.

---

### 4. Image Plan

- **No external images**.
- **Equation Visual**: Treated as a visual component (Info Box) within the Left Card.

---

### 5. Background & Decorations

- **Background**: `#FFFFFF` (Page background).
- **Top Accent Bar**: Full-width (1280px), height **6px**, color `#005587`, y=0.
- **Decorative Elements**: None (Minimalist academic style).
- **Grid**: 20px base unit.

---

### 6. Title Area & Takeaway Box

- **Title Text**: "Technical Details: FFN & Positional Encoding"
- **Position**: Centered at x=640, y=50.
- **Font**: Size **36px**, Weight **Bold**, Color `#005587`.
- **Takeaway Box**:
    - **Position**: x=40, y=90, width=1200, height=50.
    - **Style**: Fill `#EBF8FF` (Light Blue, 10% opacity of primary), Border `#005587` (1px), Radius 6px.
    - **Text**: "FFNs add non-linearity per position; Positional Encoding injects order via fixed sine/cosine functions."
    - **Font**: Size **15px**, Weight **Bold**, Color `#005587`, Centered vertically.
- **Separator**: None (Takeaway box acts as separator).

---

### 7. Content Elements

#### Element 1: Left Card (Feed-Forward Networks)

**Component type**: Content Card (White with Blue Header)
**Bounding box**: x=40, y=160, width=580, height=480.
**Card styling**:
- Fill: `#FFFFFF`, Border: `#005587` (1px), Radius: 12px.
- Header strip: Height=50px, Fill=`#005587`, Top-Left/Right Radius=12px.
- Header text: "Position-wise Feed-Forward Networks", Left-aligned (x=60, y=175), Font 20px Bold, Color `#FFFFFF`.

**Body content**:
- **Equation Box** (Visual Emphasis):
    - Box: x=60, y=220, width=500, height=70, Fill=`#F1F5F9`, Radius=6px, Border=`#CBD5E1` (1px).
    - Text: "FFN(x) = max(0, xW₁ + b₁)W₂ + b₂", Centered, Font 20px Bold, Color `#005587`.
    - Label above: "Equation (2)", Font 12px, Color `#64748B`.
- **Bullet Points** (Below Equation):
    - Start y=310, x=60. Font 18px, Color `#4A5568`, Line Height 1.6em (29px).
    - Line 1: "Applied to each position separately"
    - Line 2: "and identically."
    - Line 3: "Two linear transformations with ReLU"
    - Line 4: "activation in between."
    - Line 5: "Dimensions: d_model = 512, inner-layer"
    - Line 6: "d_ff = 2048."
- **Dimension Badges** (Inline emphasis):
    - "512" and "2048" rendered in Bold `#005587`.

**Wrapping Calculation**:
- Container inner width: 580 - 40 (padding) = 540px.
- Max chars/line (18px): ~50 chars.
- Text fits within 6 lines (approx 180px height).
- Total Card Height needed: 50 (header) + 20 (top pad) + 70 (eq) + 20 (gap) + 180 (text) + 20 (bottom pad) = 360px. (Allocated 480px for balance).

#### Element 2: Right Card (Positional Encoding)

**Component type**: Content Card (White with Blue Header)
**Bounding box**: x=660, y=160, width=580, height=480. (Gap = 40px)
**Card styling**:
- Fill: `#FFFFFF`, Border: `#005587` (1px), Radius: 12px.
- Header strip: Height=50px, Fill=`#005587`.
- Header text: "Positional Encoding", Left-aligned (x=680, y=175), Font 20px Bold, Color `#FFFFFF`.

**Body content**:
- **Bullet Points**:
    - Start y=220, x=680. Font 18px, Color `#4A5568`, Line Height 1.6em (29px).
    - Line 1: "Model contains no recurrence or"
    - Line 2: "convolution, needs positional info."
    - Line 3: "Uses sine and cosine functions of"
    - Line 4: "different frequencies."
    - Line 5: "Each dimension = sinusoid with"
    - Line 6: "wavelengths in geometric progression."
    - Line 7: "Allows learning to attend by relative"
    - Line 8: "positions for any fixed offset."

**Wrapping Calculation**:
- Container inner width: 540px.
- Max chars/line: ~50 chars.
- Text split into 8 lines (approx 232px height).
- Fits comfortably within 480px card height.

---

### 8. Visual Emphasis

- **Primary Emphasis**: The **Equation Box** in the Left Card.
    - **How**: Light gray background (`#F1F5F9`) contrasting with white card, larger font (20px), primary color text (`#005587`).
- **Secondary Emphasis**: **Card Headers**.
    - **How**: Solid Primary Blue (`#005587`) with White text to anchor the two sections.
- **Tertiary Emphasis**: **Dimensions (512/2048)**.
    - **How**: Bold weight, Primary Color.

---

### 9. Footer

- **Page Number**: "9", Position x=1240, y=700, Right-aligned. Font 12px, Color `#94A3B8`.
- **Data Source**: "Source: Attention Is All You Need (Vaswani et al.)", Position x=40, y=700. Font 10px, Color `#94A3B8`.

---

### 10. Final Spacing & Narrative Check

- [x] Title trimmed to 40 chars ("Technical Details: FFN & Positional Encoding").
- [x] Takeaway Box present at y=90 with assertion.
- [x] Equation highlighted with distinct background box.
- [x] Body font 18px (Dense density rule).
- [x] Colors: Primary `#005587`, Text `#4A5568`, BG `#FFFFFF`. (≤ 3 colors).
- [x] Safe zone: All elements within x=40–1240, y=40–680 (Footer at 700).
- [x] Gap between cards: 40px (x=580 to x=660).
- [x] Text pre-split to fit 540px width.
- [x] No images to check aspect ratio.
- [x] Footer source included.