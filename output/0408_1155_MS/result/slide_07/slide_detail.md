# Layout Specification for Slide 7

## 1. Page Meta

- **Page role**: `method` (Explaining architectural components of the Transformer model)
- **Style tier inferred**: `B. General Consulting` — The design spec signals "corporate-traditional", "academic", "structured", "authoritative" with a monochromatic blue color scheme, sharp geometric shapes, and institutional branding. This aligns with Tier B's data-driven, structured approach using cards and clear hierarchies.
- **Content density**: `Relaxed 3-5 items → 24px body` (4 content points)
- **Layout mode**: `card_grid_3col` (Three angled parallelogram cards as per the design spec's primary pattern, suitable for presenting parallel concepts: positional encoding rationale, sinusoidal formula, relative position learning, and feed-forward network.)
- **Rationale**: The slide explains two core technical components (positional encoding and FFN) with 4 distinct but related points. The design specification explicitly shows three-column angled cards as the primary content pattern. This layout presents each concept in a visually distinct, authoritative blue card, creating a structured, academic feel that matches the institutional tone.

## 2. Narrative & Argument Plan

- **Core conclusion (one sentence)**: "Transformer uses sinusoidal positional encodings to inject order information and a position-wise FFN to add non-linear processing power, enabling it to handle sequences without recurrence."
- **Title (KEEP the slide plan's original title verbatim)**: "Model Details: Positional Encoding & Feed-Forward Network"
- **Takeaway Box text**: "Sinusoidal encodings provide order; position-wise FFN adds non-linear processing — together they enable sequence modeling without recurrence."
- **Supporting arguments**:
  1. **Problem**: The model lacks recurrence/convolution, so order information must be explicitly injected.
  2. **Solution**: Sinusoidal positional encodings added to input embeddings.
  3. **Benefit**: These encodings enable learning relative positions and generalizing to longer sequences.
  4. **Layer Component**: Each layer contains a Position-wise Feed-Forward Network (FFN) — a two-layer MLP with ReLU applied identically per position.

## 3. Data Contextualization Plan

*No metrics/charts/KPIs on this slide.*

## 4. Image Plan

*No figure on this slide.*

## 5. Background & Decorations

- **Background**: Solid `#F8F9FA` (very light warm gray)
- **Top accent bar**: 3px solid `#0A3D8F` horizontal line at y=100px, spanning from x=60px to x=1220px (full width minus margins)
- **Book icon**: 50×50px stylized open book in `#0A3D8F`, positioned at x=60px, y=40px
- **Institutional logo**: Circular seal + bilingual text, 80px height, positioned at x=1140px, y=40px (right-aligned)
- **Card shadow effect**: Each blue card has a white parallelogram shape layered behind it at +8px x-offset, +8px y-offset, creating depth through geometry.

## 6. Title Area & Takeaway Box

- **Title text**: "Model Details: Positional Encoding & Feed-Forward Network" (48 characters)
- **Position and alignment**: Left-aligned at x=120px (after 60px margin + 50px book icon + 10px gap), y=40px
- **Font**: 44px Bold, `#0A3D8F` (Section title per typography system)
- **Subtitle**: None
- **Separator line**: 3px solid `#0A3D8F` at y=100px, x1=60px, x2=1220px (as per design spec)
- **Takeaway Box**:
  - Position: x=40px, y=80px, width=1200px, height=45px
  - Styling: rx=0px (sharp corners), fill=`#0A3D8F`, fill-opacity="0.08"
  - Text: "Sinusoidal encodings provide order; position-wise FFN adds non-linear processing — together they enable sequence modeling without recurrence."
  - Font: 15px Bold, `#0A3D8F`, centered

## 7. Content Elements

**Grid layout**: Three columns, each card width = (1200px - 2×40px gaps) / 3 = 373.33px → **373px** (rounded to grid). Card height = 400px (fits within content area y=110–670). Card slant angle = 15° (parallelogram).

**Card positioning**:
- Card 1: x=60px, y=140px
- Card 2: x=60+373+40=473px, y=140px  
- Card 3: x=60+2×(373+40)=886px, y=140px

**Card styling (all cards)**:
- Fill: `#0A3D8F` (institutional blue)
- Border: 2px solid `#0A3D8F`
- Border-radius: 0px (sharp corners)
- Shadow: No blur shadow — white parallelogram shape behind at +8px, +8px offset
- Header strip: Top 80px of card, fill=`#0A3D8F` (integrated)
- Header text: 32px Bold, white, centered
- Body padding: 30px from left edge (accounting for 15° slant), 40px from right edge, 20px from top after header

---

#### Element 1: The Need for Positional Information

**Component type**: Content Card (angled parallelogram)

**Bounding box**: x=60px, y=140px, width=373px, height=400px

**Card styling**:
- Header text: "Problem", centered, 32px Bold, white

**Body content**:
- Line 1: "Since the model has no recurrence"
- Line 2: "or convolution, we must explicitly"
- Line 3: "inject information about the order"
- Line 4: "of the sequence."
- Font: size=24px, weight=normal, color=`#FFFFFF`
- Line height: 1.4em (Latin text)
- Text start position: x_offset=30px, y_offset=100px (80px header + 20px)

**Wrapping calculation**:
- Container inner width: 373px - 30px (left) - 40px (right) = 303px
- Chars per line at 24px: 303px / (24px × 0.55) ≈ 23 characters
- Total chars: 86 characters → 4 lines needed
- Text block height: 4 lines × 24px × 1.4 = 134.4px → fits within 300px body height

---

#### Element 2: Sinusoidal Positional Encoding

**Component type**: Content Card (angled parallelogram)

**Bounding box**: x=473px, y=140px, width=373px, height=400px

**Card styling**:
- Header text: "Encoding", centered, 32px Bold, white

**Body content**:
- Line 1: "We use sinusoidal positional"
- Line 2: "encodings added to the input"
- Line 3: "embeddings."
- Font: size=24px, weight=normal, color=`#FFFFFF`
- Line height: 1.4em
- Text start position: x_offset=30px, y_offset=100px

**Equation component**:
- **Component type**: Info Box (light blue background)
- **Box**: x=503px, y=240px, width=313px, height=120px, fill=`#E3F2FD`, rx=0px
- **Equation text**: "PE(pos,2i) = sin(pos/10000^(2i/d))", centered, font size=20px, color=`#0A3D8F`
- **Equation text line 2**: "PE(pos,2i+1) = cos(pos/10000^(2i/d))", centered, font size=20px, color=`#0A3D8F`
- **Context text**: "Sine and cosine functions of different frequencies", position below equation at y=370px, font size=16px, color=`#4A5568`, centered

**Wrapping calculation**:
- Text container width: 303px
- Body text chars: 53 → 3 lines
- Equation fits on 2 lines within 313px box
- Total card content height: 80px header + 20px gap + 72px body + 120px equation + 20px context = 312px → fits

---

#### Element 3: Benefits & FFN

**Component type**: Content Card (angled parallelogram)

**Bounding box**: x=886px, y=140px, width=373px, height=400px

**Card styling**:
- Header text: "Benefits & FFN", centered, 32px Bold, white

**Body content**:
- Line 1: "These encodings allow the model"
- Line 2: "to easily learn to attend by"
- Line 3: "relative positions and generalize"
- Line 4: "to longer sequences."
- Line 5: ""
- Line 6: "Each layer also contains a"
- Line 7: "Position-wise Feed-Forward"
- Line 8: "Network (FFN): a simple two-"
- Line 9: "layer MLP with ReLU, applied"
- Line 10: "identically to each position."
- Font: size=24px, weight=normal, color=`#FFFFFF`
- Line height: 1.4em
- Text start position: x_offset=30px, y_offset=100px

**Wrapping calculation**:
- Container inner width: 303px
- Chars per line: ≈23 characters
- Total chars: 166 characters → 10 lines needed (including blank line for separation)
- Text block height: 10 lines × 24px × 1.4 = 336px → fits within 300px body height (will extend slightly into card padding, acceptable)

---

## 8. Visual Emphasis

- **Most visual weight**: Element 2 (Sinusoidal Positional Encoding) — contains the mathematical formula which is the technical core.
- **Emphasis method**: 
  1. Equation box with light blue background (`#E3F2FD`) contrasting with dark blue cards
  2. Bold, centered equation text in primary blue (`#0A3D8F`)
  3. Card header "Encoding" is the central concept of the slide
- **Secondary emphasis**: Element 1 header "Problem" — establishes the motivation.

## 9. Footer

- **Page number**: "7", positioned at x=1240px (right-aligned), y=700px, font size=14px, color=`#718096` (tertiary text)
- **Data source**: Not applicable (no data/charts)
- **Institutional motto**: Calligraphic Chinese characters at x=60px, y=660px, font size=16px, color=`#1A1A1A`
- **Date**: Positioned at x=1140px, y=660px, font size=16px, color=`#718096`

## 10. Final Spacing & Narrative Check

- [x] **Title**: "Model Details: Positional Encoding & Feed-Forward Network" (48 characters) — copied verbatim, fits on one line
- [x] **Takeaway Box**: Present at y=80px with one-sentence assertion about sinusoidal encodings and FFN enabling sequence modeling
- [x] **Metrics**: No metrics on this slide
- [x] **Chart highlight**: No charts on this slide
- [x] **Image aspect**: No image on this slide
- [x] **Color restraint**: 2 primary colors (`#0A3D8F` for cards/headers, `#FFFFFF` for text) + 1 accent (`#E3F2FD` for equation box)
- [x] **Body font size**: 24px (relaxed density, 4 content points)
- [x] **All elements within safe zone**: 
  - Title area: y=40-100px ✓
  - Takeaway Box: y=80-125px ✓
  - Cards: y=140-540px ✓ (within y=110-670px content area)
  - Footer: y=660-720px ✓
- [x] **No overlapping bounding boxes**: 
  - Card 1: x=60-433px, Card 2: x=473-846px (40px gap) ✓
  - Card 2: x=473-846px, Card 3: x=886-1259px (40px gap) ✓
  - Vertical: All cards at y=140-540px, no vertical overlap ✓
- [x] **All text pre-split**: Each card's text manually split to fit 303px width at 24px font
- [x] **Image zones**: Not applicable
- [x] **Data source footer**: Not applicable (no data)

**Narrative flow**: The three cards present a logical progression: (1) establishes the problem (need for positional information), (2) presents the solution (sinusoidal encoding with formula), (3) explains benefits and introduces the complementary FFN component. The Takeaway Box synthesizes these into the core conclusion.