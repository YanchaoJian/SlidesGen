### 1. Page Meta
- **Page role**: `cover`
- **Style tier inferred**: `C. Top Consulting (MBB)` / `Academic Institutional` — Inferred from the "Dalian University Academic Blue" theme, which emphasizes formal structure, geometric precision (skewed parallelograms), and a restrained navy/off-white palette.
- **Content density**: `Relaxed` (Title + 4 descriptive items)
- **Layout mode**: `cover_centered` (adapted for left-aligned academic style per spec)
- **Rationale**: As the opening slide, it establishes the institutional identity using the theme's specific cover page requirements (large skewed parallelogram, specific title positioning, and academic tone).

### 2. Narrative & Argument Plan
- **Core conclusion**: Introduction of the Transformer architecture as a revolutionary attention-only sequence model.
- **Title**: "Attention Is All You Need"
- **Takeaway Box text**: (N/A for cover page)
- **Supporting arguments**:
    1. Authorship from Google Brain, Google Research, and Uof Toronto.
    2. Presentation at NeurIPS 2017.
    3. Core thesis: Replacing recurrence/convolutions with pure attention.

### 3. Data Contextualization Plan
(N/A for cover page)

### 4. Image Plan
(N/A for cover page)

### 5. Background & Decorations
- **Background**: Solid `#F8F9FA` (Institutional off-white).
- **Background Grid**: 40px dot grid pattern in `#E9ECEF` across the entire canvas.
- **Main Decorative Shape**: Large navy blue parallelogram (`#003D7C`) occupying the right 40% of the screen.
    - **Position**: x=1000, y=0, width=480, height=720.
    - **Transform**: `skewX(-20deg)`.
- **Ghost Outline**: Thin blue outline parallelogram (`#003D7C`, 1px stroke).
    - **Position**: x=980, y=20, width=480, height=720.
    - **Transform**: `skewX(-20deg)`.
- **Header Icon**: Navy blue parallelogram icon (`#003D7C`).
    - **Position**: x=30, y=275, width=30, height=50.
    - **Transform**: `skewX(-20deg)`.
    - **Detail**: Three horizontal white lines (2px thick) centered within the icon.

### 6. Title Area & Takeaway Box
- **Title text**: "Attention Is All You Need"
- **Position**: Left-aligned at x=80, y=300.
- **Font**: 60px, Bold, `#003D7C` (DUT Brand Blue).
- **Subtitle (Authors)**:
    - **Text**: Split into 3 lines (see Content Elements).
    - **Position**: Starts at x=80, y=360.
    - **Font**: 28px, SemiBold, `#808080` (Gray).

### 7. Content Elements

#### Element 1: Author List
- **Component type**: Plain Text Block
- **Bounding box**: x=80, y=360, width=670, height=120
- **Body content**:
    - Line 1: "Ashish Vaswani, Noam Shazeer, Niki Parmar,"
    - Line 2: "Jakob Uszkoreit, Llion Jones, Aidan N. Gomez,"
    - Line 3: "Łukasz Kaiser, Illia Polosukhin"
- **Font**: size=28px, weight=semibold, color=#808080
- **Wrapping calculation**:
    - Container width: 670px
    - Chars per line (28px): ~43
    - Line 1: 42 chars (Fits)
    - Line 2: 45 chars (Fits)
    - Line 3: 31 chars (Fits)

#### Element 2: Affiliations & Conference
- **Component type**: Plain Text Block
- **Bounding box**: x=80, y=500, width=700, height=60
- **Body content**:
    - Line 1: "Google Brain · Google Research · University of Toronto"
    - Line 2: "31st Conference on Neural Information Processing Systems (NeurIPS 2017)"
- **Font**: size=20px, weight=normal, color=#808080
- **Wrapping calculation**:
    - Line 1: 55 chars (55 * 20 * 0.55 = 605px) -> Fits.
    - Line 2: 70 chars (70 * 20 * 0.55 = 770px) -> **Split needed**.
    - *Revised Line 2*: "31st Conference on Neural Information Processing Systems"
    - *Revised Line 3*: "(NeurIPS 2017)"

#### Element 3: Research Summary
- **Component type**: Info Box (Subtle)
- **Bounding box**: x=80, y=580, width=680, height=80
- **Styling**: No fill, no border (clean academic look).
- **Body content**:
    - Line 1: "A new simple network architecture, the Transformer, based solely on"
    - Line 2: "attention mechanisms, dispensing with recurrence and convolutions entirely."
- **Font**: size=18px, weight=normal, color=#1A1A1A
- **Wrapping calculation**:
    - Container width: 680px
    - Chars per line (18px): ~68
    - Line 1: 67 chars (Fits)
    - Line 2: 65 chars (Fits)

### 8. Visual Emphasis
- **Primary Emphasis**: The Title "Attention Is All You Need" in 60px Navy Blue.
- **Secondary Emphasis**: The large skewed navy parallelogram on the right, providing the "Institutional/Academic" weight.
- **Tertiary Emphasis**: The "Document" icon preceding the title.

### 9. Footer
- **Divider Line**: 1px solid `#003D7C` at y=640, from x=60 to x=1220.
- **Motto (Left)**: "Self-Reliance and Rigorous Scholarship; Seeking Truth and Promoting Innovation"
    - **Position**: x=60, y=680, left-aligned.
    - **Font**: 14px, `#808080`.
- **Date (Right)**: "December 2017"
    - **Position**: x=1220, y=680, right-aligned.
    - **Font**: 14px, `#808080`.
- **Page Number**: "1 / [Total]" at x=1240, y=705, right-aligned, 14px.

### 10. Final Spacing & Narrative Check
- [x] Title is verbatim: "Attention Is All You Need" (5 words).
- [x] No Takeaway Box (Cover page exception).
- [x] Skew consistency: All decorative shapes use `-20deg`.
- [x] Safe zone: All text is within x=80 to x=750, avoiding the right-side graphic.
- [x] Colors: Strictly Navy (`#003D7C`), Gray (`#808080`), and Off-white (`#F8F9FA`).
- [x] Spacing: 20px-40px gaps between all text blocks.