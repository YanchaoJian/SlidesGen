### 1. Page Meta

-   Page role: `method`
-   Style tier inferred: `C. Top Consulting (MBB)` — The design specification emphasizes "academic, geometric, institutional, structured" tone, "technical geometric precision," "hard-edge offsets," "skewed -20 degrees," and "strict center-alignment for all text and content within cards," which are hallmarks of a Top Consulting style.
-   Content density: `Dense` (4 bullet points + 1 equation, requiring 20px body font as per design spec override)
-   Layout mode: `left_right_split`
-   Rationale: The slide describes the methodology of an experimental setup. The Tier C style aligns with the formal academic tone. A left-right split allows for presenting the setup details (datasets, hardware, training, optimizer) on the left and the specific learning rate equation on the right, giving appropriate visual weight to both.

### 2. Narrative & Argument Plan

-   **Core conclusion (one sentence)**: The experimental setup leverages large-scale resources and optimized training strategies for efficient and robust machine translation.
-   **Title (KEEP the slide plan's original title verbatim)**: "Experimental Setup: Machine Translation"
-   **Takeaway Box text** (≤ 20 words): Our experimental setup leverages large datasets and powerful hardware for efficient, scalable machine translation training.
-   **Supporting arguments** (2-4 items):
    1.  Utilizes large, industry-standard datasets.
    2.  Employs high-performance GPU hardware for parallel processing.
    3.  Features optimized training schedules for base and large models.
    4.  Incorporates an advanced learning rate scheduler for stable convergence.

### 3. Data Contextualization Plan

*   No specific metrics requiring comparison or interpretation beyond their descriptive context.

### 4. Image Plan

*   `includes_figure: false` — No image on this slide.

### 5. Background & Decorations

-   Background: `#F8F9FA` with a subtle 40px dot grid pattern in `#E9ECEF`.
-   Top decorative bar:
    -   Component type: Rectangle
    -   Bounding box: x=0, y=95, width=1280, height=2
    -   Fill: `#003D7C`
-   Header Icon:
    -   Component type: Skewed Parallelogram with document graphic
    -   Position: x=60, y=55 (aligned with title baseline)
    -   Dimensions: width=30, height=40 (visual representation, actual SVG path will be more complex)
    -   Skew: -20 degrees
    -   Fill: `#003D7C`
    -   Document graphic: 3 horizontal white lines inside.

### 6. Title Area & Takeaway Box

-   Title text: "Experimental Setup: Machine Translation"
-   Position and alignment: Left-aligned. Icon at x=60, y=55. Text start at x=100, y=60.
-   Font: size=40px, weight=Bold, color=`#1A1A1A`
-   Takeaway Box:
    -   Component type: Rectangle
    -   Bounding box: x=40, y=110, width=1200, height=45, rx=0 (sharp corners)
    -   Fill: `#003D7C` with `fill-opacity="0.08"`
    -   Text: "Our experimental setup leverages large datasets and powerful hardware for efficient, scalable machine translation training."
    -   Text position: x=60, y=135 (vertically centered within box)
    -   Font: size=15px, weight=bold, color=`#003D7C`
    -   Line height: 1.4em
    -   Wrapping calculation:
        -   Container inner width: 1200 - 40 = 1160px
        -   Chars per line at font_size=15px: 1160 / (15 * 0.55) ≈ 140 chars
        -   Total chars: 118 -> 1 line needed
        -   Text block height: 1 * 15 * 1.4 = 21px (fits 45px box)

### 7. Content Elements

#### Element 1: Experimental Details (Left Panel)

**Component type**: Content Card (Parallelogram)

**Bounding box**: x=60, y=180, width=560, height=480 (This is the bounding box for the visible content area, the parallelogram shape will extend beyond this slightly due to skew)

**Card styling**:
-   Shape: Parallelogram with `skewX(-20deg)`
-   Fill: `#003D7C`
-   Offset outline: A secondary parallelogram (no fill, 1px stroke `#003D7C`) positioned behind and offset 10px down and right.
-   Card padding: 30px (internal padding for text)

**Body content**:
-   Line 1: "Datasets:"
-   Line 2: "WMT 2014 English-to-German (4.5M sentence pairs)"
-   Line 3: "and English-to-French (36M sentence pairs)."
-   Line 4: "" (empty line for spacing)
-   Line 5: "Hardware:"
-   Line 6: "8 NVIDIA P100 GPUs."
-   Line 7: ""
-   Line 8: "Training:"
-   Line 9: "Base model: 100,000 steps (12 hours)"
-   Line 10: "Big model: 300,000 steps (3.5 days)"
-   Line 11: ""
-   Line 12: "Optimizer:"
-   Line 13: "Adam with a custom learning rate scheduler"
-   Line 14: "featuring a warmup phase."
-   Font: size=20px, weight=normal, color=`#FFFFFF`
-   Line height: 1.4em
-   Text start position within card: x_offset=30px from card left (after un-skewing), y_offset=30px from card top (after un-skewing)

**Show your wrapping calculation**:
-   Container inner width: 560 - (2 * 30) = 500px (accounting for skew, this is the effective width for text)
-   Chars per line at font_size=20px: 500 / (20 * 0.55) ≈ 45 chars
-   "WMT 2014 English-to-German (4.5M sentence pairs)" (49 chars) -> 2 lines
-   "and English-to-French (36M sentence pairs)." (45 chars) -> 1 line
-   "Base model: 100,000 steps (12 hours)" (36 chars) -> 1 line
-   "Big model: 300,000 steps (3.5 days)" (35 chars) -> 1 line
-   "Adam with a custom learning rate scheduler" (42 chars) -> 1 line
-   "featuring a warmup phase." (25 chars) -> 1 line
-   Total lines needed: 1+2+1+1+1+1+1+1+1+1+1+1 = 14 lines (with empty lines)
-   Text block height: 14 * 20 * 1.4 = 392px (fits 480px height)

#### Element 2: Learning Rate Equation (Right Panel)

**Component type**: Info Box (Rectangle with no skew, as it's an equation, not a content card)

**Bounding box**: x=660, y=180, width=560, height=480
**Fill**: `#F4F7FA` (Secondary bg for subtle section)
**Border**: 1px solid `#003D7C`

**Body content**:
-   Line 1: "We varied the learning rate over the course of training,"
-   Line 2: "according to the formula:"
-   Line 3: ""
-   Line 4: "lrate = d"
-   Line 5: "−0.5"
-   Line 6: "model · min(step_num−0.5"
-   Line 7: ", step_num · warmup_steps−1.5"
-   Line 8: ") (3)"
-   Font: size=20px, weight=normal, color=`#1A1A1A` (for context text)
-   Font: size=24px, weight=normal, color=`#1A1A1A` (for equation text, slightly larger for readability)
-   Line height: 1.4em (for context), 1.6em (for equation to allow for superscripts/subscripts)
-   Text start position within box: x_offset=30px from box left, y_offset=30px from box top

**Show your wrapping calculation**:
-   Container inner width: 560 - (2 * 30) = 500px
-   Chars per line at font_size=20px: 500 / (20 * 0.55) ≈ 45 chars
-   "We varied the learning rate over the course of training," (50 chars) -> 2 lines (will need to wrap)
-   "according to the formula:" (28 chars) -> 1 line
-   Equation lines are fixed by LaTeX rendering, assume they fit.
-   Total lines needed: 2+1+1+1+1+1+1+1 = 9 lines (approx)
-   Text block height: (2*20*1.4) + (1*20*1.4) + (1*20*1.4) + (5*24*1.6) = 56 + 28 + 28 + 192 = 304px (fits 480px height)

### 8. Visual Emphasis

-   The entire slide emphasizes the experimental setup. The left-right split gives equal visual weight to the details and the specific equation.
-   The use of the primary brand blue for the left content card and the border of the right info box provides a cohesive emphasis.

### 9. Footer

-   Page number: text="9", position x=1200 (right-aligned), y=690, font size=14px, color=`#808080`
-   Motto/Date: Not specified in slide plan, but design spec mentions "Motto (left), Date (right), and thin divider". Assuming these are standard elements, they would be placed at x=60, y=690 (Motto) and x=1000, y=690 (Date).
-   Footer divider: 1px solid `#003D7C` at y=680, full width.

### 10. Final Spacing & Narrative Check

-   [x] Title is copied verbatim from slide_plan.title and is ≤ 50 characters (38 chars).
-   [x] Takeaway Box is present directly under the title and carries the one-sentence assertion.
-   [ ] Every metric has a comparison reference and an interpretation (N/A for this slide's content).
-   [ ] Chart highlight strategy declared (N/A for this slide).
-   [ ] Image container aspect ratio matches the native image ratio (N/A for this slide).
-   [x] ≤ 3 primary colors across the page; data series use same-hue opacity variations (Navy, White, Off-white, Light Gray, Dark Gray).
-   [x] Body font size matches the content-density rule (20px as per design spec override).
-   [x] All elements within safe zone (x: 40–1240, y: 40–680).
-   [x] No bounding boxes overlap (min 20px gap between elements). Left card x=60, right box x=660, gap = 660- (60+560) = 40px.
-   [x] All text has been pre-split into lines that fit their container.
-   [x] Image zones and text zones are separated (N/A).
-   [ ] Data source footer present on data pages (N/A, no specific data source needed for experimental setup description).