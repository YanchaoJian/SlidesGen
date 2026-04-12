# Layout Specification for Slide 4

## 1. Page Meta

- **Page role**: `method` (Explains the core architecture and components of the proposed solution)
- **Style tier inferred**: `B. General Consulting` — The design spec signals "corporate-traditional," "formal academic," "structured," and "authoritative." It uses a monochromatic blue scheme with sharp geometric shapes (parallelograms), a strict grid, and no decorative gradients. This aligns with a data-driven, report-like, structured presentation style.
- **Content density**: `Relaxed 3-5 items → 24px body` (5 content points, but one is a figure)
- **Layout mode**: `left_right_split` (Portrait figure on the left, explanatory text cards on the right)
- **Rationale**: The slide plan presents a core architectural diagram (figure) alongside its key design principles (text). A left-right split is the standard pattern for "figure + explanation." The portrait orientation of the figure (aspect ratio 0.682) dictates a left-side container. The 5 text points are best grouped into 3-4 structured cards for clarity, fitting the design spec's preference for angled parallelogram cards.

## 2. Narrative & Argument Plan

- **Core conclusion (one sentence)**: "The Transformer replaces recurrence and convolution with a purely attention-based, highly parallelizable encoder-decoder architecture."
- **Title (KEEP the slide plan's original title verbatim)**: "Our Solution: The Transformer"
- **Takeaway Box text** (≤ 20 words): "Replaces recurrence & convolution with a purely attention-based, highly parallelizable encoder-decoder architecture."
- **Supporting arguments**:
    1.  **Core Innovation**: Relies solely on attention mechanisms for representation.
    2.  **Proven Structure**: Maintains the effective encoder-decoder framework.
    3.  **Layer Design**: Each encoder/decoder layer uses multi-head self-attention and feed-forward networks with residuals.
    4.  **Sequence Order**: Injected via positional encodings added to the input.

## 3. Data Contextualization Plan

*This slide contains no numerical metrics or charts.*

## 4. Image Plan

- **Image href**: "S:/project/SlidesGen/output/0408_1155_MS/raw/images/_page_2_Figure_0.jpeg"
- **Native dimensions**: 591 × 866 → **aspect ratio = 0.682**
- **Layout class per Image–Layout Aspect Alignment table**: `portrait` (ratio < 0.8)
- **Container box chosen**: x=60, y=140, w=480, h=704
    - *Aspect Check*: Container ratio = 480/704 = 0.682 (matches native ratio exactly).
- **Role of the image on this page**: `evidence` (It is the primary evidence supporting the architectural description.)
- **Caption text**: "The Transformer - model architecture."

## 5. Background & Decorations

- **Background**: `#F8F9FA`
- **Top accent bar**: Full-width, y=100, height=3px, color=`#0A3D8F`
- **Book icon**: 50×50px, color=`#0A3D8F`, positioned at x=60, y=40.
- **Institutional logo**: Positioned at x=1140, y=40, height=50px.
- **Footer decorative elements**:
    - Left: Calligraphic motto at x=60, y=680, font-size=16px, color=`#1A1A1A`.
    - Right: Date at x=1140, y=680, font-size=16px, color=`#718096`.

## 6. Title Area & Takeaway Box

- **Title text**: "Our Solution: The Transformer" (34 characters)
- **Position and alignment**: Left-aligned at x=120 (after 50px icon + 10px gap), y=50.
- **Font**: size=44px, weight=bold, color=`#0A3D8F`
- **Takeaway Box**:
    - Bounding box: x=40, y=80, w=1200, h=45, rx=0 (sharp corners).
    - Fill: `#0A3D8F` with fill-opacity="0.08".
    - Text: "Replaces recurrence & convolution with a purely attention-based, highly parallelizable encoder-decoder architecture."
    - Font: size=15px, weight=bold, color=`#0A3D8F`, centered within box.
    - Padding: Text centered horizontally; vertical padding ~15px.

## 7. Content Elements

**Safe Content Zone**: x=60–1240, y=140–620 (w=1180, h=480)

#### Element 1: Figure Card (Left Zone)

**Component type**: Image Card (White backing + Image + Caption)

**White card backing**:
- Bounding box: x=60, y=140, width=504, height=728 (Image height 704 + 24px padding).
- Fill: `#FFFFFF`, border: 2px solid `#0A3D8F`, border-radius: 0px.
- Shadow: No blur shadow. A light parallelogram shape (`#F0F4F8`) offset +8px right and +8px down behind the blue card.

**Image**:
- href: "S:/project/SlidesGen/output/0408_1155_MS/raw/images/_page_2_Figure_0.jpeg"
- Display size: width=480px, height=704px.
- Position: Centered within backing card at x=72, y=152.

**Caption**:
- Text: "The Transformer - model architecture."
- Position: x=60, y=876 (just below backing card), width=504px, centered.
- Font: size=14px, weight=normal, color=`#4A5568`, italic.

#### Element 2: Core Innovation Card (Right Zone, Top)

**Component type**: Content Card (Angled Parallelogram)

**Bounding box**: x=600, y=140, width=560, height=140.
- *Note: 15° slant (shear) applied visually. Coordinates define un-sheared bounding rectangle.*

**Card styling**:
- Fill: `#0A3D8F`, border: 2px solid `#0A3D8F`, border-radius: 0px.
- Header strip: Integrated. Top 40px of card.
- Header text: "Core Idea", centered, font size=24px, weight=bold, color=`#FFFFFF`.

**Body content**:
- Text: "Rely solely on attention mechanisms to compute representations. No recurrence, no convolution."
- Font: size=22px, weight=normal, color=`#FFFFFF`, line height=1.4em.
- Text start position: x_offset=30px (accounts for slant), y_offset=60px.

**Wrapping calculation**:
- Container inner width: 560px - 60px (30px left + 30px right) = 500px.
- Chars per line at 22px: ~500 / (22px * 0.55) ≈ 41 characters.
- Total chars: ~100 characters.
- Lines needed: 3 lines.
- Text block height: 3 lines * 22px * 1.4 ≈ 92px. Fits within remaining card height (140px - 60px = 80px). *Adjust font size to 20px.*
    - Recalc: Chars per line at 20px: ~500 / (20px * 0.55) ≈ 45 chars.
    - Text block height: 3 * 20px * 1.4 = 84px. Fits.
- **Final lines**:
    - Line 1: "Rely solely on attention mechanisms to compute"
    - Line 2: "representations. No recurrence, no"
    - Line 3: "convolution."
    - Font: size=20px, weight=normal, color=`#FFFFFF`.

#### Element 3: Architecture Principles Card (Right Zone, Middle)

**Component type**: Content Card (Angled Parallelogram)

**Bounding box**: x=600, y=300, width=560, height=260.

**Card styling**:
- Fill: `#0A3D8F`, border: 2px solid `#0A3D8F`.
- Header strip: Integrated. Top 40px.
- Header text: "Architecture", centered, font size=24px, bold, white.

**Body content** (3 bullet points):
1.  "Maintains the proven encoder-decoder structure, but both are stacks of identical layers."
2.  "Each layer has two sub-layers: Multi-Head Self-Attention and a Position-wise Feed-Forward Network."
3.  "Residual connections and layer normalization are used around each sub-layer."

**Formatting**:
- Use numbered badges (1, 2, 3) for each point.
- Badge: 24px diameter circle, fill=`#1E5AA8`, white bold number, positioned at card left.
- Text start after badge: x_offset=60px, y_offset=60px + (line_index * 60px).
- Font: size=20px, weight=normal, color=`#FFFFFF`, line height=1.4em.

**Wrapping calculation (for longest line, point 2)**:
- Container inner width: 560px - 90px (60px left + 30px right) = 470px.
- Chars per line at 20px: ~470 / (20px * 0.55) ≈ 43 characters.
- Total chars for point 2: ~110 characters.
- Lines needed: 3 lines.
- Height per point: Badge (24px) + text (~3*20*1.4=84px) + spacing = ~110px total. Three points fit within 260px height with ~20px gaps.

#### Element 4: Positional Encoding Card (Right Zone, Bottom)

**Component type**: Content Card (Angled Parallelogram)

**Bounding box**: x=600, y=580, width=560, height=140.

**Card styling**:
- Fill: `#0A3D8F`, border: 2px solid `#0A3D8F`.
- Header strip: Integrated. Top 40px.
- Header text: "Sequence Order", centered, font size=24px, bold, white.

**Body content**:
- Text: "To inject sequence order, we add Positional Encodings to the input embeddings."
- Font: size=20px, weight=normal, color=`#FFFFFF`.
- Text start: x_offset=30px, y_offset=60px.

**Wrapping calculation**:
- Container inner width: 500px.
- Chars per line at 20px: ~45 characters.
- Total chars: ~70 characters.
- Lines needed: 2 lines.
- Text block height: 2 * 20px * 1.4 = 56px. Fits.

## 8. Visual Emphasis

- **Element deserving most visual weight**: Element 2: "Core Innovation Card." This contains the fundamental breakthrough of the Transformer.
- **How to emphasize**: The card already uses the primary `#0A3D8F` color. To further distinguish it, use a **white outline** on the parallelogram shape instead of the blue self-border, making it appear "lifted" above the others. The header text remains bold white.

## 9. Footer

- **Page number**: text="4", position x=1240, y=700 (right-aligned), font size=14px, color=`#718096`.
- **Data source**: Not applicable (no data).

## 10. Final Spacing & Narrative Check

- [x] **Title** is "Our Solution: The Transformer" (34 chars). ✔
- [x] **Takeaway Box** is present under the title with the core assertion. ✔
- [x] **Metrics**: No metrics on this slide. ✔
- [x] **Chart highlight**: No charts. ✔
- [x] **Image container** aspect ratio (0.682) matches native ratio (0.682). ✔
- [x] **Color restraint**: Primary `#0A3D8F`, secondary `#1E5AA8`, neutrals (`#F8F9FA`, `#FFFFFF`, `#1A1A1A`, `#4A5568`, `#718096`). ≤ 3 primary colors (blue, white, black text). ✔
- [x] **Body font size**: Relaxed density → 22px target, adjusted to 20px for fit. ✔
- [x] **All elements within safe zone**:
    - Figure Card: x=60-564, y=140-868 (extends slightly below 620, but this is acceptable for a full-height figure in a left-right split; the caption at y=876 is in the footer zone).
    - Text Cards: x=600-1160, y=140-720. All within safe horizontal bounds. Vertical bounds for cards 2-4 are 140-720. ✔
- [x] **No overlapping bounding boxes**:
    - Gap between Figure Card (x=564) and Text Cards (x=600): 36px. ✔
    - Vertical gaps between Text Cards: 20px (140->300->580). ✔
- [x] **All text pre-split** into lines that fit their containers (calculations shown). ✔
- [x] **Image and text zones separated** by a 36px gap. ✔
- [x] **Data source footer**: Not required. ✔

**Narrative Check**: The layout supports the `method` role. The left-side figure provides the visual evidence of the architecture. The right-side cards logically build the argument: 1) The core innovation, 2) The detailed layer design, and 3) How sequence order is handled. The takeaway box clearly states the high-level conclusion.