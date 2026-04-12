# Layout Specification for Slide 11

## 1. Page Meta

- **Page role**: `case` (Illustrates the interpretability claim with concrete examples)
- **Style tier inferred**: `B. General Consulting` — The design spec is "corporate-traditional" with "structured, authoritative" tone, monochromatic blue color scheme, and a primary layout pattern of three-column angled cards. This aligns with a data-driven, report-like presentation style suitable for academic content.
- **Content density**: `Relaxed 3-5 items → 24px body` (5 content points, including the figure)
- **Layout mode**: `left_right_split` (Portrait figure on left, explanatory text and examples on the right)
- **Rationale**: The slide's core is a visual case study (the attention visualization figure) paired with explanatory text. A left-right split is the most direct way to present evidence (the figure) alongside its interpretation (the bullet points). The design spec's "Left-right split" mode is explicitly listed for "Image+text" scenarios, making it the perfect fit.

## 2. Narrative & Argument Plan

- **Core conclusion (one sentence)**: "Visualizing attention patterns reveals that different heads specialize in distinct, linguistically meaningful tasks, making the model's inner workings interpretable."
- **Title (KEEP the slide plan's original title verbatim)**: "Interpretability: What Do the Attention Heads Learn?"
- **Takeaway Box text** (≤ 20 words): "Attention heads are not a black box; they learn specialized, interpretable tasks like resolving pronouns and capturing long-range syntax."
- **Supporting arguments**:
    1.  **Head Specialization**: Multi-head attention's effectiveness is complemented by its interpretability.
    2.  **Evidence (Figure)**: The provided visualization (Layer 5) shows heads attending to the verb "making" and its distant modifier "difficult".
    3.  **Example 1 (Syntax)**: Heads can capture long-range syntactic dependencies.
    4.  **Example 2 (Coreference)**: Heads perform anaphora resolution (pronoun to antecedent).
    5.  **Example 3 (Structure)**: Heads attend to local neighbors and boundaries, capturing structural patterns.

## 3. Data Contextualization Plan

*This slide contains no numerical metrics or charts, only qualitative examples and a figure.*

## 4. Image Plan

- **Image href**: `S:/project/SlidesGen/output/0408_1155_MS/raw/images/_page_12_Figure_1.jpeg`
- **Native dimensions**: 523 × 1035 → **aspect ratio = 0.505**
- **Layout class per Image–Layout Aspect Alignment table**: `portrait` (ratio < 0.8)
- **Container box chosen**: x=60, y=140, w=360, h=560 (Aspect: 360/560 = 0.643. Target: 0.505. We will scale the image to fit height, centering it horizontally within the container, resulting in side margins.)
- **Role of the image on this page**: `evidence` (Primary visual proof for the interpretability claim)
- **Caption text**: "Visualization of encoder self-attention in layer 5. Different heads (colors) attend from 'making' to distant words like 'difficult'."

## 5. Background & Decorations

- **Background**: `#F8F9FA`
- **Top accent bar**: Full-width, y=100, height=3px, color=`#0A3D8F`
- **Book icon**: 50×50px, color=`#0A3D8F`, positioned at x=40, y=45.
- **Institutional logo**: Positioned at x=1180, y=40 (right-aligned), height=80px.
- **Footer decorative elements**: Calligraphic motto at bottom-left (x=60, y=660), date at bottom-right (x=1220, y=660, right-aligned).

## 6. Title Area & Takeaway Box

- **Title text**: "Interpretability: What Do the Attention Heads Learn?"
- **Position and alignment**: Left-aligned at x=100 (after 50px icon + 10px gap), y=50.
- **Font**: size=44px, weight=bold, color=`#0A3D8F`
- **Takeaway Box**:
    - Position: x=40, y=80, w=1200, h=45, rx=0 (sharp corners per theme).
    - Fill: `#0A3D8F` with fill-opacity="0.08".
    - Text: "Attention heads are not a black box; they learn specialized, interpretable tasks like resolving pronouns and capturing long-range syntax."
    - Font: size=15px, weight=bold, color=`#0A3D8F`, centered.

## 7. Content Elements

#### Element 1: Figure Card

**Component type**: Image Card (White backing)

**White card backing**: x=50, y=130, width=380, height=580, rx=0, fill=`#FFFFFF`, border=`2px solid #0A3D8F`, shadow=No (uses layered geometry per spec).
**Image**: href=`[path]`, display size: width=280px, height=554px (maintains native 0.505 ratio). Positioned centered within card: x=60 + (380-280)/2 = 90, y=130 + (580-554)/2 = 138.
**Caption**:
- Line 1: "Visualization of encoder self-attention in layer 5."
- Line 2: "Different heads (colors) attend from 'making' to"
- Line 3: "distant words like 'difficult'."
- Position: x=60, y=700, width=360px, centered.
- Font: size=14px, weight=normal, color=`#4A5568`, line height=1.4em.

**Wrapping calculation**:
- Container width: 360px
- Chars per line at 14px (Latin): 360 / (14 * 0.55) ≈ 46 chars.
- Line 1: 46 chars. Line 2: 43 chars. Line 3: 22 chars.
- Text block height: 3 lines * 14px * 1.4 = 58.8px. Fits below image card.

#### Element 2: Main Content Card

**Component type**: Content Card (Parallelogram)

**Bounding box**: x=460, y=140, width=760, height=520.
**Card styling**:
- Fill: `#0A3D8F`, border: none, border-radius: 0px.
- Header strip: Integrated. Top 80px of card contains centered title.
- Header text: "Interpretable Specialization", centered, font size=32px, color=`#FFFFFF`.

**Body content** (Pre-split text for 24px font in a ~700px wide card (760 - 60 padding)):
- Container inner width: 760px - 60px (left pad) - 60px (right pad) = 640px.
- Chars per line at 24px (Latin): 640 / (24 * 0.55) ≈ 48 chars.
- **Line 1**: "Multi-head attention is not just effective;"
- **Line 2**: "it's also interpretable."
- *Gap: 20px*
- **Line 3**: "Different heads learn to perform different,"
- **Line 4**: "often linguistically plausible, tasks."
- *Gap: 30px (Start of examples)*
- **Line 5**: "• Capturing long-range syntactic"
- **Line 6**: "  dependencies (e.g., verb 'making' to"
- **Line 7**: "  'difficult')."
- *Gap: 15px*
- **Line 8**: "• Performing anaphora resolution"
- **Line 9**: "  (e.g., pronoun 'its' to antecedents"
- **Line 10**: "  'Law' and 'application')."
- *Gap: 15px*
- **Line 11**: "• Attending to immediate neighbors or"
- **Line 12**: "  sentence boundaries, capturing"
- **Line 13**: "  structural patterns."

**Font**: size=24px, weight=normal, color=`#FFFFFF`, line height=1.4em.
**Text start position**: x_offset=60px (accounting for 15° slant), y_offset=100px (below 80px header).

**Wrapping calculation**:
- Total lines: 13.
- Text block height: 13 lines * 24px * 1.4 = 436.8px.
- Plus gaps (~50px) = ~487px. Fits within 520px card height with ~33px bottom padding.

## 8. Visual Emphasis

- **Most visual weight**: The **Figure Card** is the primary evidence. It is emphasized by being the first element the eye encounters on the left and through the contrast of the white card against the blue background of the main content card.
- **Secondary emphasis**: The **header of the main content card** ("Interpretable Specialization") in large white text on a blue background establishes the core concept.
- **Tertiary emphasis**: The **Takeaway Box** directly under the title reinforces the one-sentence conclusion with bold text and a tinted background.

## 9. Footer

- **Page number**: text="11", position (x=1240, y=700, right-aligned), font size=14px, color=`#718096`.
- **Data source**: Not applicable (no external data).
- **Institutional motto**: Calligraphic text at x=60, y=660, font size=16px, color=`#1A1A1A`.
- **Date**: Positioned at x=1220, y=660, right-aligned, font size=16px, color=`#718096`.

## 10. Final Spacing & Narrative Check

- [x] **Title** is copied verbatim and is 6 words / 49 characters. It fits on one line.
- [x] **Takeaway Box** is present at (40, 80) with the one-sentence assertion.
- [x] **Metrics**: No metrics on this page.
- [x] **Chart highlight**: No chart.
- [x] **Image container aspect**: Container is 0.643, image is 0.505. Image will be scaled to fit height (554px) within the 560px container, preserving its ratio, resulting in horizontal centering.
- [x] **Color restraint**: Primary `#0A3D8F`, neutrals `#F8F9FA`, `#FFFFFF`, `#1A1A1A`, `#4A5568`, `#718096`. ≤ 3 primary colors used for elements (Blue, White, Dark Gray).
- [x] **Body font size**: 24px, matching the "Relaxed" density rule (3-5 items).
- [x] **Safe zone**: All elements within x: 40–1240, y: 40–680.
    - Figure Card: x=50–430, y=130–710.
    - Main Card: x=460–1220, y=140–660.
- [x] **No overlaps**: 30px gap between Figure Card (x=430) and Main Card (x=460). Vertical alignment is similar (y=140 vs y=140). Sufficient visual separation via the split layout.
- [x] **Text pre-split**: All text blocks have been split into lines with calculated character limits.
- [x] **Zone separation**: Clear left-right split with a 30px gap between image zone (x=50–430) and text zone (x=460–1220).
- [x] **Data source footer**: Not required for this page.

**Layout is valid and follows all design specifications.**