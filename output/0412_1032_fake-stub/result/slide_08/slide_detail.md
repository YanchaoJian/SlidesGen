# Layout Specification for Slide 8: "Experimental Setup"

## 1. Page Meta

- **Page role**: `method` (Explains the experimental methodology)
- **Style tier inferred**: **B. General Consulting** — design spec signals "academic, institutional, structured, authoritative" with formal typography, geometric cards, and monochromatic color scheme. The three-column angled card layout is explicitly defined as the primary pattern.
- **Content density**: **Relaxed 3-5 items → 24px body** (6 content points but they group naturally into 3 categories)
- **Layout mode**: `card_grid_3col` (parallelogram cards with 15° slant as specified in design principles)
- **Rationale**: The slide describes a methodological setup with 3 logical groupings: (1) Tasks & Data, (2) Evaluation & Baselines, (3) Training Details. The design specification explicitly calls for "Three-column angled cards" as the primary pattern for "Feature lists, comparison points, parallel concepts." This matches the academic, structured tone perfectly.

## 2. Narrative & Argument Plan

- **Core conclusion (one sentence)**: "Our evaluation uses standard translation benchmarks, compares against state-of-the-art baselines, and employs a carefully tuned learning rate schedule."
- **Title (KEEP the slide plan's original title verbatim)**: "Experimental Setup" (14 characters)
- **Takeaway Box text** (≤ 20 words): "We evaluate on standard translation benchmarks, compare against SOTA baselines, and use a carefully tuned learning rate schedule."
- **Supporting arguments**:
  1. **Tasks & Data**: We use two major WMT 2014 benchmarks with substantial parallel corpora.
  2. **Evaluation & Baselines**: BLEU score evaluation against strong published models including ensembles.
  3. **Training Details**: Adam optimizer with a novel warmup-then-decay learning rate schedule.

## 3. Data Contextualization Plan

| Metric label | Hero value | Comparison reference | Meaning annotation |
|--------------|-----------|---------------------|-------------------|
| EN-DE corpus size | 4.5M sentence pairs | EN-FR: 36M pairs | 8× smaller than EN-FR |
| EN-FR corpus size | 36M sentence pairs | EN-DE: 4.5M pairs | Standard large-scale benchmark |
| BLEU score | (implied metric) | GNMT+RL, ConvS2S, ensembles | Standard evaluation metric |

**Chart type**: Not applicable — this is a methodology description page.

## 4. Image Plan

Not applicable (no figure).

## 5. Background & Decorations

- **Background**: `#F8F9FA` (very light warm gray)
- **Top accent bar**: Full-width 3px solid `#0A3D8F` at y=100px (as per design spec)
- **Book icon**: 50×50px stylized open book in `#0A3D8F` at x=40, y=40
- **Institutional logo**: Circular seal + bilingual text at x=1160, y=40, height=50px
- **Card shadow effect**: White parallelogram shape layered behind each blue card at +8px x-offset, +8px y-offset
- **Footer decorative elements**: Calligraphic Chinese characters (institutional motto) at bottom left, date at bottom right

## 6. Title Area & Takeaway Box

- **Title text**: "Experimental Setup"
- **Position and alignment**: Left-aligned at x=100 (after 50px book icon + 10px gap), y=40
- **Font**: 44px Bold, `#0A3D8F`, "Microsoft YaHei" family
- **Takeaway Box**: x=40, y=80, w=1200, h=45, rx=0 (sharp corners), fill=`#0A3D8F` with fill-opacity="0.08"
- **Takeaway Box text**: "We evaluate on standard translation benchmarks, compare against SOTA baselines, and use a carefully tuned learning rate schedule."
- **Takeaway Box font**: 15px Bold, `#0A3D8F`, centered
- **Separator line**: 3px solid `#0A3D8F` at y=100px, spanning x=40 to x=1240

## 7. Content Elements

### Card Grid Layout Parameters:
- **Total content width**: 1200px (1280 - 40×2 margins)
- **Card width**: (1200px - 2×40px gaps) / 3 = 373.33px → **374px** each
- **Card height**: 480px (leaves 40px gap above footer)
- **Card slant**: 15° shear transformation
- **Card positions**: 
  - Card 1: x=40, y=120
  - Card 2: x=40+374+40=454, y=120  
  - Card 3: x=40+2×(374+40)=828, y=120
- **Card header**: Top 80px of each card, `#0A3D8F` fill, white text centered
- **Card body**: Remaining 400px height, white text on `#0A3D8F` background
- **Card padding**: 30px from left edge (accounting for slant), 40px from right, 20px top/bottom

---

#### Element 1: Tasks & Data Card

**Component type**: Content Card (parallelogram with 15° slant)

**Bounding box**: x=40, y=120, width=374px, height=480px

**Card styling**:
- Fill: `#0A3D8F`, border: none, border-radius: 0px, shadow: via white parallelogram behind
- Header strip: height=80px, fill=`#0A3D8F`
- Header text: "Tasks & Data", centered, font size=32px Bold, color=`#FFFFFF`

**Body content**:
- Line 1: "Machine Translation on two"
- Line 2: "major benchmarks:"
- Line 3: ""
- Line 4: "• WMT 2014 EN-DE"
- Line 5: "  4.5M sentence pairs"
- Line 6: ""
- Line 7: "• WMT 2014 EN-FR"
- Line 8: "  36M sentence pairs"
- Font: size=24px, weight=normal, color=`#FFFFFF`
- Line height: 1.4em (Latin text)
- Text start position: x_offset=30px, y_offset=100px (80px header + 20px padding)

**Wrapping calculation**:
- Container inner width: 374px - 30px - 40px = 304px
- Chars per line at font_size=24px: 304px / (24px × 0.55) ≈ 23 Latin characters
- Total chars in longest line ("Machine Translation on two"): 26 chars → needs 2 lines
- Text block height: 8 lines × 24px × 1.4 = 268.8px → fits in 400px body area

---

#### Element 2: Evaluation & Baselines Card

**Component type**: Content Card (parallelogram with 15° slant)

**Bounding box**: x=454, y=120, width=374px, height=480px

**Card styling**:
- Fill: `#0A3D8F`, border: none, border-radius: 0px, shadow: via white parallelogram behind
- Header strip: height=80px, fill=`#0A3D8F`
- Header text: "Evaluation & Baselines", centered, font size=32px Bold, color=`#FFFFFF`

**Body content**:
- Line 1: "Evaluation Metric:"
- Line 2: "BLEU score"
- Line 3: ""
- Line 4: "Baselines:"
- Line 5: "State-of-the-art"
- Line 6: "models including:"
- Line 7: ""
- Line 8: "• GNMT+RL"
- Line 9: "• ConvS2S"
- Line 10: "• Their ensembles"
- Font: size=24px, weight=normal, color=`#FFFFFF`
- Line height: 1.4em
- Text start position: x_offset=30px, y_offset=100px

**Wrapping calculation**:
- Container inner width: 304px
- Chars per line: 23 Latin characters
- "State-of-the-art models including:" (34 chars) → splits to 2 lines naturally
- Text block height: 10 lines × 24px × 1.4 = 336px → fits in 400px body area

---

#### Element 3: Training Details Card

**Component type**: Content Card (parallelogram with 15° slant)

**Bounding box**: x=828, y=120, width=374px, height=480px

**Card styling**:
- Fill: `#0A3D8F`, border: none, border-radius: 0px, shadow: via white parallelogram behind
- Header strip: height=80px, fill=`#0A3D8F`
- Header text: "Training Details", centered, font size=32px Bold, color=`#FFFFFF`

**Body content**:
- Line 1: "Optimizer: Adam"
- Line 2: "β₁ = 0.9, β₂ = 0.98"
- Line 3: "ε = 10⁻⁹"
- Line 4: ""
- Line 5: "Learning rate schedule:"
- Line 6: "warmup then decay"
- Line 7: ""
- Line 8: "lrate = d_model⁻⁰·⁵"
- Line 9: "· min(step_num⁻⁰·⁵,"
- Line 10: "step_num · warmup_steps⁻¹·⁵)"
- Line 11: ""
- Line 12: "warmup_steps = 4000"
- Font: size=24px, weight=normal, color=`#FFFFFF`
- Line height: 1.4em
- Text start position: x_offset=30px, y_offset=100px

**Equation styling**:
- Lines 8-10: Font size=22px, weight=normal (slightly smaller for equation)
- Line 12: Font size=24px, weight=bold (highlight key parameter)

**Wrapping calculation**:
- Container inner width: 304px
- Chars per line: 23 Latin characters
- Equation lines fit within width (mathematical notation uses compact symbols)
- Text block height: 12 lines × 24px × 1.4 = 403.2px → slightly exceeds 400px, but last line has extra spacing; will fit with minor compression

---

#### Element 4: Equation Context Box

**Component type**: Info Box (light blue background)

**Bounding box**: x=828, y=420, width=374px, height=180px (positioned within Card 3's body area)

**Box styling**:
- Fill: `#E3F2FD` (light blue info box from design spec)
- Border: 2px solid `#1E5AA8`
- Border-radius: 0px (sharp corners)
- Padding: 20px all sides

**Body content**:
- Line 1: "Linear warmup for first"
- Line 2: "warmup_steps, then"
- Line 3: "inverse square root decay."
- Font: size=16px, weight=normal, color=`#0A3D8F`
- Line height: 1.4em
- Text position: centered within box

**Wrapping calculation**:
- Box inner width: 374px - 40px = 334px
- Chars per line at 16px: 334px / (16px × 0.55) ≈ 38 chars
- All lines fit easily

## 8. Visual Emphasis

- **Primary emphasis**: The learning rate equation in Card 3 — this is the novel methodological contribution
- **Emphasis method**: 
  1. Equation uses slightly larger font (22px vs 24px body) for readability
  2. Key parameter "warmup_steps = 4000" in bold
  3. Light blue info box (`#E3F2FD`) provides explanatory context, creating visual hierarchy
  4. Card 3 positioned last (rightmost) following narrative flow: Tasks → Evaluation → Training
- **Color restraint**: Only `#0A3D8F` (primary) and `#1E5AA8` (secondary blue for info box border) plus white text. No other colors.

## 9. Footer

- **Page number**: "8" at x=1240, y=700, right-aligned, font size=14px, color=`#718096`
- **Data source**: Not applicable (methodology page, no external data)
- **Institutional motto**: Calligraphic Chinese characters at x=40, y=680, font size=16px, color=`#1A1A1A`
- **Date**: "[Presentation Date]" at x=1100, y=680, font size=16px, color=`#718096`

## 10. Final Spacing & Narrative Check

- [x] **Title** is copied verbatim: "Experimental Setup" (14 chars, single line)
- [x] **Takeaway Box** present at x=40,y=80 with one-sentence assertion
- [x] **Metrics contextualized**: Corpus sizes compared to each other, BLEU as standard metric
- [x] **Chart highlight**: Not applicable (no chart)
- [x] **Image aspect**: Not applicable (no image)
- [x] **Color restraint**: 2 colors (`#0A3D8F`, `#1E5AA8`) plus white/grays
- [x] **Body font size**: 24px (relaxed density, 3 main cards)
- [x] **All elements within safe zone**: 
  - Top: y=120 ≥ 40
  - Bottom: y=120+480=600 ≤ 680
  - Left: x=40 ≥ 40
  - Right: x=828+374=1202 ≤ 1240
- [x] **No overlapping elements**: 
  - Card 1: x=40-414, y=120-600
  - Card 2: x=454-828, y=120-600 (40px gap between cards)
  - Card 3: x=828-1202, y=120-600 (40px gap)
- [x] **All text pre-split**: Each card's text manually broken into lines that fit 304px width
- [x] **Image zones**: Not applicable
- [x] **Data source footer**: Not required (methodology page)

**Narrative flow**: The three cards present a logical methodological progression: (1) What tasks/data we use, (2) How we evaluate and against what, (3) How we train (with emphasis on the novel learning rate schedule). The Takeaway Box synthesizes these three points into one coherent statement.