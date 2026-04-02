# ==============================================================================
# SVG 生成 Prompt（LLM → SVG 源码 → DrawingML → 可编辑 PPTX）
# ==============================================================================

SVG_GENERATION_SYSTEM_PROMPT = """\
# Role: Senior SVG Slide Designer

You are a presentation slide designer who outputs **SVG source code** that will be \
converted to native editable PowerPoint shapes via a DrawingML converter. \
Every element you create becomes a real, clickable, editable PowerPoint object — \
not an embedded image.

---

## Canvas Specification

- **Fixed canvas**: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">`
- **Coordinate system**: Pixels. Origin (0,0) is top-left. X→right, Y→down.
- **Safe margins**: Keep important content within x=40..1240, y=40..680.
- **Background**: Always start with a full-canvas `<rect>` for the page background color.

---

## 🚫 Banned Features (Will Break PPTX Export)

The following SVG features are **absolutely forbidden** — the DrawingML converter \
cannot handle them and PPTX export will fail:

| Banned | Use Instead |
|--------|------------|
| `clipPath`, `mask` | Overlay a rect to visually crop |
| `<style>`, `class`, external CSS | Inline attributes only (`fill="..."`, `font-size="..."`) |
| `<foreignObject>` | Use `<text>` with `<tspan>` for line breaks |
| `<symbol>` + `<use>` (except icon placeholders) | Duplicate the element |
| `textPath` | Position text manually |
| `@font-face` | System fonts only |
| `<animate*>`, `<set>`, `<script>` | Static SVG only |
| `marker`, `marker-end` | Draw arrow with `<polygon>` |
| `fill="rgba(...)"` | `fill="#HEX" fill-opacity="0.x"` |
| `<g opacity="0.x">` | Set `fill-opacity` / `stroke-opacity` on each child |
| `<image opacity="0.x">` | Overlay a semi-transparent `<rect>` on top |
| `<iframe>` | Not supported |

---

## Typography

Use **system fonts only**. Apply fonts via inline `font-family` attribute.

**Default sizes** (override with the Design Specification if provided):

| Role | Size | Font (Chinese) | Font (English) | Weight |
|------|------|----------------|----------------|--------|
| Main title | 36-48px | Microsoft YaHei | Arial | bold |
| Subtitle | 24-28px | Microsoft YaHei | Arial | bold |
| Body text | 18-22px | Microsoft YaHei | Calibri | normal |
| Caption / annotation | 12-14px | Microsoft YaHei | Arial | normal |
| Page number | 12-14px | — | Arial | normal |

> If the user prompt includes a "Design Specification" section with a Typography System table, \
use those sizes, fonts, and weights instead of the defaults above.

**Text rules**:
- Use `text-anchor="middle"` for centered text (x = center point).
- Use `text-anchor="start"` for left-aligned text (x = left edge).
- Line breaks: use `<tspan x="..." dy="...">` inside `<text>`. Never use `<foreignObject>`.
- Long text: split into multiple `<tspan>` elements with appropriate `dy` spacing.
- CJK text line height: dy="1.6em" to "1.8em". Latin text: dy="1.4em".

---

## Supported Visual Techniques

### Gradients (linear & radial)

Define in `<defs>`, reference with `fill="url(#id)"`. Converts to native PPTX gradient fill.

```xml
<defs>
  <linearGradient id="headerGrad" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#003366"/>
    <stop offset="100%" stop-color="#005599"/>
  </linearGradient>
</defs>
<rect x="0" y="0" width="1280" height="120" fill="url(#headerGrad)"/>
```

### Filter Shadow (auto-converts to PPTX outer shadow)

```xml
<defs>
  <filter id="shadow" x="-15%" y="-15%" width="140%" height="140%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="12"/>
    <feOffset dx="0" dy="6" result="offsetBlur"/>
    <feFlood flood-color="#000000" flood-opacity="0.15" result="shadowColor"/>
    <feComposite in="shadowColor" in2="offsetBlur" operator="in" result="shadow"/>
    <feMerge>
      <feMergeNode in="shadow"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
</defs>
<rect ... filter="url(#shadow)"/>
```

### Filter Glow (auto-converts to PPTX glow — NO feOffset)

```xml
<defs>
  <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="6" result="blur"/>
    <feFlood flood-color="#1A73E8" flood-opacity="0.45" result="glowColor"/>
    <feComposite in="glowColor" in2="blur" operator="in" result="glow"/>
    <feMerge>
      <feMergeNode in="glow"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
</defs>
```

### Image Overlay (replace banned `<image opacity>`)

```xml
<image href="..." x="0" y="0" width="1280" height="720" preserveAspectRatio="xMidYMid slice"/>
<defs>
  <linearGradient id="overlay" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%"   stop-color="#000000" stop-opacity="0"/>
    <stop offset="100%" stop-color="#000000" stop-opacity="0.72"/>
  </linearGradient>
</defs>
<rect x="0" y="0" width="1280" height="720" fill="url(#overlay)"/>
```

### Dashed / Dotted Strokes (converts to PPTX dash presets)

| `stroke-dasharray` | Effect |
|--------------------|--------|
| `4,4` | Dash |
| `2,2` | Dot |
| `8,4` | Long dash |
| `8,4,2,4` | Dash-dot |

### Rounded Rectangles

```xml
<rect x="60" y="80" width="400" height="200" rx="12" fill="#FFFFFF" filter="url(#shadow)"/>
```

### Text Decorations

`text-decoration="underline"` and `text-decoration="line-through"` are supported.

### Image Card (MANDATORY for all `<image>` elements)

Images extracted from academic papers always have **white backgrounds**. When the slide \
background is colored, the white edges look jarring. You **MUST** wrap every `<image>` \
element with a white rounded-rectangle card + soft shadow to make the white background \
look intentional and professional.

**Pattern** (always use this when placing an image):

```xml
<!-- Step 1: White card backing (slightly larger than the image, with padding) -->
<rect x="648" y="148" width="424" height="324"
      rx="8" fill="#FFFFFF" filter="url(#shadow)"/>
<!-- Step 2: Image on top of the card (inset by the padding) -->
<image href="figure.png" x="660" y="160" width="400" height="300"
       preserveAspectRatio="xMidYMid meet"/>
```

Rules:
- Card padding: **12px** on each side (card is 24px wider and 24px taller than the image).
- Card corner radius: `rx="8"` (or match the design spec's border radius).
- Card fill: always `#FFFFFF` regardless of slide background color.
- Card shadow: use the `filter="url(#shadow)"` defined in `<defs>`. If no shadow filter \
is defined yet, add one (see the shadow pattern above).
- The `<rect>` card must appear **before** the `<image>` in SVG source (z-order: card below image).
- Caption text (if any) should sit **below the card**, not overlapping it.

---

## Layout Patterns (1280×720 canvas)

**Default layouts** (override with the Design Specification if provided):

| Pattern | Description | Key Coordinates |
|---------|-------------|----------------|
| Title + subtitle centered | Cover / chapter page | Title y≈300, subtitle y≈380 |
| Top header bar + body | Standard content page | Header h=100-120, body starts y≈160 |
| Left-right split | Image + text | Left x=40..620, Right x=660..1240 |
| Three-column cards | Feature list | x=40,440,840 each w=380, gap=20 |
| Full-image + overlay | Visual impact cover | Image fills canvas, gradient overlay, text on top |

> If the user prompt includes a "Design Specification" with Layout Principles (zone heights, margins, \
spacing), use those values for page structure instead of the defaults above.

---

## Geometry & Spacing Rules (CRITICAL — violations cause rejection)

### Safe Zone
All visible content **must** stay within the safe zone: **x: 40–1240, y: 40–680**.
Elements outside this range will be clipped or overflow the slide.

### Minimum Spacing
- Adjacent elements (text blocks, images, shapes) must have **≥20px gap** between their bounding boxes.
- Between title and body content: **≥30px** vertical gap.
- Between body text lines: use `dy="1.6em"` to `"2.0em"` (never less than `"1.4em"`).

### Text Box Sizing
- Estimate characters per line: `line_width / (font_size × 0.55)` for Latin, `line_width / (font_size × 1.0)` for CJK.
- If text is longer than one line, split into multiple `<tspan>` elements.
- Always set text block width explicitly — do NOT let long text overflow into adjacent elements.

### Image + Text Coexistence
When a slide has both text and an image:
- **Left-right layout**: text zone x=40..600, image zone x=640..1240 (or vice versa). Zones must NOT overlap.
- **Top-bottom layout**: allocate vertical space proportionally. Image + caption must fit within their zone.
- After placing all elements, mentally verify: no bounding box intersects another.

### Pre-output Self-Check
Before outputting SVG, verify:
1. Every element's `x + width ≤ 1280` and `y + height ≤ 720`.
2. No two sibling elements share overlapping coordinate ranges (both x-range AND y-range overlap = collision).
3. Text blocks have enough height for all `<tspan>` lines (count lines × line-height).
4. Images do not extend beyond their allocated zone.

---

## Output Requirements

1. Output **only** the raw SVG source code — no markdown fences, no explanation.
2. The SVG must be **well-formed XML** (all tags closed, attributes quoted).
3. First child element must be a full-canvas background `<rect>`.
4. All `<defs>` (gradients, filters) must come before elements that reference them.
5. Z-order: background → decorations → content cards → text → foreground accents.
6. Include a page number in the bottom-right corner (e.g., `01 / 10`).
"""


def build_svg_slide_prompt(
    slide_plan: dict,
    style_protocol: str,
    total_pages: int = 10,
    slide_detail: str = "",
    failed_svg: str = "",
    error_context: str = "",
    design_critique: str = "",
) -> str:
    """
    构建单页 SVG 生成的 user prompt。

    Args:
        slide_plan: 单页幻灯片计划 dict，包含 slide_page, title, content,
                    includes_figure, figure_reference, includes_table,
                    table_reference, includes_equation, equation_reference,
                    presenter_notes 等字段。
        style_protocol: 设计规范字符串（来自 style_analyst）。
        total_pages: 总页数，用于页码显示。
        slide_detail: 由 expand_slide_plan 生成的详细页面描述（可选）。
        failed_svg: 上次失败的 SVG 代码（重试时传入）。
        error_context: 上次的错误日志（语法/结构验证失败时传入）。
        design_critique: 视觉评审反馈（设计质量检查未通过时传入）。

    Returns:
        完整的 user prompt 字符串。
    """
    page = slide_plan.get("slide_page", 1)
    title = slide_plan.get("title", "")
    content_items = slide_plan.get("content", [])
    notes = slide_plan.get("presenter_notes", "")

    # ── 构建内容描述 ──
    sections = []

    sections.append(f"## Slide {page} / {total_pages}\n")

    # 设计规范（从参考图提取的主题风格）
    sections.append("### Design Specification\n")
    sections.append("Follow the color scheme, typography, layout principles, and visual features ")
    sections.append("defined below. These override the default values in the system prompt.\n")
    sections.append(f"{style_protocol}\n")

    # 详细页面描述（由 expand_slide_plan 生成）
    if slide_detail:
        sections.append("### Detailed Slide Description\n")
        sections.append("The following is a detailed layout and content description expanded from the outline. ")
        sections.append("Use this as the primary guide for element placement and visual decisions.\n")
        sections.append(f"{slide_detail}\n")

    # 页面内容
    sections.append("### Page Content\n")
    sections.append(f"**Title**: {title}\n")

    if content_items:
        sections.append("**Body Points**:")
        for i, item in enumerate(content_items, 1):
            sections.append(f"  {i}. {item}")
        sections.append("")

    # 图片引用
    if slide_plan.get("includes_figure") and slide_plan.get("figure_reference"):
        fig = slide_plan["figure_reference"]
        fig_path = fig.get("path", "")
        fig_caption = fig.get("caption", "")
        sections.append("**Figure**:")
        sections.append(f"  - Path: `{fig_path}`")
        sections.append(f"  - Caption: {fig_caption}")
        sections.append(f'  - Use: `<image href="{fig_path}" preserveAspectRatio="xMidYMid slice"/>`')
        sections.append("")

    # 表格引用
    if slide_plan.get("includes_table") and slide_plan.get("table_reference"):
        tbl = slide_plan["table_reference"]
        sections.append("**Table** (render as SVG rectangles + text, NOT as HTML):")
        sections.append(f"  - Caption: {tbl.get('caption', '')}")
        sections.append(f"  - Data:\n```\n{tbl.get('markdown', '')}\n```")
        sections.append("")

    # 公式引用
    if slide_plan.get("includes_equation") and slide_plan.get("equation_reference"):
        eq = slide_plan["equation_reference"]
        sections.append("**Equation** (render as SVG `<text>` with mathematical symbols):")
        sections.append(f"  - LaTeX: `{eq.get('latex', '')}`")
        sections.append(f"  - Context: {eq.get('context', '')}")
        sections.append("")

    # 演讲备注
    if notes:
        sections.append(f"**Presenter Notes** (for context, do NOT display on slide): {notes}\n")

    # 页面类型提示
    if page == 1:
        sections.append("### Layout Hint\n")
        sections.append("This is the **cover page**. Use a visually striking layout: "
                        "large centered title, subtitle below, decorative elements, "
                        "and the page background should make a strong first impression.\n")
    elif page == total_pages:
        sections.append("### Layout Hint\n")
        sections.append("This is the **closing page**. Use a clean, memorable layout: "
                        "thank-you message, key takeaway, or call to action.\n")

    # 重试上下文
    if failed_svg or error_context or design_critique:
        sections.append("### ⚠️ Retry Context\n")

        if design_critique:
            sections.append("The previous SVG **passed syntax validation** but **failed visual design review**. "
                            "A visual auditor examined the rendered slide screenshot and found layout/aesthetic issues.\n")
            sections.append(f"**Visual Critique (you MUST fix all issues listed below)**:\n```\n{design_critique}\n```\n")
            sections.append("**Instructions**: Carefully read the critique above. Each issue includes the specific SVG element "
                            "and attribute that needs to change, along with the suggested fix values. Apply ALL suggested fixes "
                            "to the previous SVG below. Do NOT just regenerate from scratch — modify the specific coordinates, "
                            "sizes, and positions mentioned in the critique.\n")
        elif error_context:
            sections.append("The previous SVG generation failed **syntax/structure validation**. Fix the issues below.\n")
            sections.append(f"**Error Log**:\n```\n{error_context}\n```\n")

        if failed_svg:
            sections.append(f"**Previous SVG (apply fixes to this)**:\n```xml\n{failed_svg}\n```\n")

    # 最终指令
    sections.append("---\n")
    sections.append("Generate the complete SVG source code for this slide. "
                    "Output only the SVG, nothing else.")

    return "\n".join(sections)


# ==============================================================================
# Demo
# ==============================================================================

if __name__ == "__main__":
    example_plan = {
        "slide_page": 4,
        "title": "Scaled Dot-Product Attention",
        "content": [
            "The Transformer uses scaled dot-product attention to compute attention weights.",
            "This mechanism ensures stable gradients for large dimensions.",
            "The formula below shows the calculation of attention scores.",
        ],
        "includes_figure": False,
        "figure_reference": None,
        "includes_table": False,
        "table_reference": None,
        "includes_equation": True,
        "equation_reference": {
            "latex": r"\text{Attention}(Q, K, V) = \text{softmax}(\frac{QK^T}{\sqrt{d_k}})V",
            "context": "We employ a self-attention mechanism... The formula below shows the calculation of attention scores.",
        },
        "presenter_notes": "Explain the attention mechanism and its role in the Transformer.",
    }

    example_style = """## I. Theme Overview

| Item | Value |
| ---- | ----- |
| **Theme Name** | Academic Blue |
| **Atmosphere** | Professional, clean academic style for technical reports |
| **Tone** | professional / academic / minimalist |
| **Theme Mode** | Light |

## II. Color Scheme

| Role | HEX | Purpose |
| ---- | --- | ------- |
| **Background** | `#F5F5F5` | Page background |
| **Secondary bg** | `#FFFFFF` | Card background |
| **Primary** | `#003366` | Title decorations, header bar |
| **Accent** | `#E94560` | Data highlights, key numbers |
| **Body text** | `#333333` | Main body text |
| **Secondary text** | `#666666` | Captions |
| **Tertiary text** | `#999999` | Page numbers |
| **Border / divider** | `#E0E0E0` | Card borders |

### Gradient Definitions
```
<linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%">
  <stop offset="0%" stop-color="#003366"/>
  <stop offset="100%" stop-color="#005599"/>
</linearGradient>
```

## III. Typography System

| Role | Size (px) | Weight | Color Role |
| ---- | --------- | ------ | ---------- |
| Cover title | 48px | Bold | Light text (#FFFFFF) |
| Section title | 36px | Bold | Primary (#003366) |
| Subtitle | 24px | SemiBold | Body text |
| **Body** | **18px** | Normal | Body text |
| Annotation | 14px | Normal | Secondary text |
| Page number | 12px | Normal | Tertiary text |

**Font stack**: `Arial, 'Microsoft YaHei', sans-serif`

## IV. Layout Principles

| Zone | Y-range (px) | Height (px) | Description |
| ---- | ------------ | ----------- | ----------- |
| Header area | 0 – 100 | 100px | Dark blue gradient, white title text |
| Content area | 140 – 660 | 520px | White/light gray cards |
| Footer area | 680 – 720 | 40px | Page number, subtle line |

| Element | Value (px) |
| ------- | ---------- |
| Left / right margin | 40px |
| Card gap | 24px |
| Card border radius | 12px |

## V. Visual Features

### Decorative Elements
- Header bar with gradient fill (#003366 → #005599)
- Subtle separator lines between sections

### Shadow Effects
- Soft card shadow: color #000000, opacity 0.1, offset 0 4px, blur 12px

### Shape Style
- Rounded rectangles (rx=12)"""

    prompt = build_svg_slide_prompt(
        slide_plan=example_plan,
        style_protocol=example_style,
        total_pages=10,
    )

    print("=" * 60)
    print("SVG_GENERATION_SYSTEM_PROMPT (first 200 chars):")
    print(SVG_GENERATION_SYSTEM_PROMPT[:200] + "...")
    print()
    print("=" * 60)
    print("User Prompt (build_svg_slide_prompt):")
    print("=" * 60)
    print(prompt)
