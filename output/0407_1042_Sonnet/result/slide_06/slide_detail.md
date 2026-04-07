### 1. Page Meta
- **Page role**: `method` (Explains the mechanics of the Multi-Head Attention component)
- **Style tier inferred**: `B. General Consulting` — Inferred from "academic", "structured", and "institutional" keywords in the design spec, requiring clear data/diagram presentation with geometric rigor.
- **Content density**: `Dense` (4 bullet points + 1 complex figure + 1 multi-line equation) → **18px body baseline**.
- **Layout mode**: `left_right_split` (4:6 ratio as per Design Spec)
- **Rationale**: The content describes a technical process. A split layout allows the architectural diagram (figure) to serve as the primary reference while the text and equations provide the formal definition and functional explanation.

---

### 2. Narrative & Argument Plan
- **Core conclusion**: Multi-head attention enables the model to capture diverse linguistic relationships by processing information in parallel representation subspaces.
- **Title**: Technical Detail: Multi-Head Attention
- **Takeaway Box text**: Parallel attention heads capture distinct features like syntax and semantics, then combine them for a richer representation.
- **Supporting arguments**:
    1. **Parallelism**: $h$ attention functions run simultaneously rather than a single pass.
    2. **Subspace Diversity**: Each head attends to different positions and representation subspaces.
    3. **Feature Specialization**: Individual heads specialize in specific relationship types (e.g., syntax vs. semantics).
    4. **Aggregation**: Results are concatenated and projected back to the target dimensionality.

---

### 3. Data Contextualization Plan
*No quantitative metrics provided in the slide plan. The focus is on structural/mathematical logic.*

---

### 4. Image Plan
- **Image href**: "S:/project/SlidesGen/output/0407_1042/raw/images/_page_3_Figure_0.jpeg"
- **Native dimensions**: 850 × 452 → aspect ratio = 1.88
- **Layout class**: `landscape` (Wide)
- **Container box chosen**: x=60, y=175, w=600, h=319 (Matches 1.88 aspect ratio)
- **Role of the image**: `evidence` (Primary architectural diagram of the mechanism)
- **Caption text**: (left) Scaled Dot-Product Attention. (right) Multi-Head Attention consists of several attention layers running in parallel.

---

### 5. Background & Decorations
- **Background**: `#F8F9FA` (Institutional off-white)
- **Grid Pattern**: 40px dot grid in `#E9ECEF` across the full canvas.
- **Top accent bar**: y=95, height=2px, color=`#003D7C` (Navy).
- **Header Icon**: Skewed parallelogram (width 40, height 40, skew -20°) at x=60, y=40, color=`#003D7C` with 3 white lines.
- **University Logo**: Placeholder at x=1100, y=40, w=120, h=40 (Right-aligned in header).

---

### 6. Title Area & Takeaway Box
- **Title text**: "Technical Detail: Multi-Head Attention"
- **Position**: x=110, y=65 (Left-aligned, following the icon)
- **Font**: 40px, Bold, `#003D7C`
- **Takeaway Box**: 
    - **Box**: x=60, y=110, w=1160, h=45, fill=`#003D7C` (opacity 0.08), no border.
    - **Text**: "Parallel attention heads capture distinct features like syntax and semantics, then combine them for a richer representation."
    - **Font**: 18px, Bold, `#003D7C`, centered vertically.

---

### 7. Content Elements

#### Element 1: Figure Card
- **Component type**: Image Card (Skewed)
- **Bounding box**: x=60, y=175, width=600, height=319
- **Styling**: 
    - **Ghost Outline**: x=70, y=185, width=600, height=319, stroke=`#003D7C`, fill=none, skewX=-20deg.
    - **Image Container**: x=60, y=175, width=600, height=319, fill=white, skewX=-20deg.
- **Caption**: x=60, y=505, text="(left) Scaled Dot-Product Attention. (right) Multi-Head Attention architecture.", font=14px, color=`#808080`.

#### Element 2: Equation Box
- **Component type**: Info Box
- **Bounding box**: x=680, y=175, width=540, height=100
- **Styling**: Fill=`#E6EEF7` (Secondary accent), border=`#0056A6`, skewX=-20deg.
- **Content**:
    - Line 1: "MultiHead(Q, K, V) = Concat(head1, ..., headh)WO"
    - Line 2: "where headi = Attention(QWQi, KWKi, VWVi)"
    - Font: 18px, Bold (Monospace feel), `#003D7C`, centered.

#### Element 3: Parallelism Card
- **Component type**: Content Card (Skewed)
- **Bounding box**: x=680, y=295, width=540, height=150
- **Card styling**: Fill=`#003D7C`, skewX=-20deg.
- **Ghost Outline**: x=690, y=305, width=540, height=150, stroke=`#003D7C`, fill=none, skewX=-20deg.
- **Body content**:
    - Line 1: "Parallel Attention: Performs h independent"
    - Line 2: "attention operations to capture information"
    - Line 3: "from different representation subspaces."
    - Font: 18px, Normal, `#FFFFFF`, centered.
- **Wrapping calculation**: Inner width 480px / (18 * 0.55) ≈ 48 chars. Lines are ~40 chars.

#### Element 4: Feature Diversity Card
- **Component type**: Content Card (Skewed)
- **Bounding box**: x=680, y=465, width=540, height=150
- **Card styling**: Fill=`#003D7C`, skewX=-20deg.
- **Ghost Outline**: x=690, y=475, width=540, height=150, stroke=`#003D7C`, fill=none, skewX=-20deg.
- **Body content**:
    - Line 1: "Feature Diversity: Different heads focus on"
    - Line 2: "distinct linguistic relationships, such as"
    - Line 3: "syntax or semantic dependencies."
    - Font: 18px, Normal, `#FFFFFF`, centered.

#### Element 5: Analogy Callout
- **Component type**: Info Box
- **Bounding box**: x=60, y=540, width=600, height=80
- **Styling**: Fill=`#F4F7FA`, border-left=4px solid `#0056A6`, skewX=-20deg.
- **Content**:
    - Line 1: "Analogy: Like multiple filters in a CNN, each head"
    - Line 2: "captures a different 'feature' of the input sequence."
    - Font: 16px, Italic, `#1A1A1A`, left-aligned (x_offset=30).

---

### 8. Visual Emphasis
- **Primary Emphasis**: The **Multi-Head Attention Figure** (Element 1) occupies the largest visual area on the left.
- **Secondary Emphasis**: The **Equation Box** (Element 2) uses a high-contrast light blue fill to stand out from the navy cards.
- **Tertiary Emphasis**: The **Takeaway Box** uses a subtle tint to frame the core conclusion immediately under the title.

---

### 9. Footer
- **Page number**: "6 / 12", x=1220, y=700, right-aligned, 14px, `#808080`.
- **Data source**: "Source: Vaswani et al. (2017) 'Attention Is All You Need'", x=60, y=700, 12px, `#808080`.
- **Motto**: "Dalian University of Technology", x=60, y=685, 12px, `#003D7C`, Bold.

---

### 10. Final Spacing & Narrative Check
- [x] Title is verbatim: "Technical Detail: Multi-Head Attention" (Fits on one line).
- [x] Takeaway Box present: Yes, at y=110.
- [x] Image aspect ratio: 600/319 = 1.88 (Matches native 1.88).
- [x] Skew consistency: All cards and boxes use `-20deg` skew.
- [x] Ghost outlines: Present on all primary content cards.
- [x] Safe zone: All elements between x=60 and x=1220, y=40 and y=640.
- [x] No overlaps: 20px vertical gap between all right-side elements.
- [x] Text wrapping: Pre-calculated for 18px font on 540px cards.