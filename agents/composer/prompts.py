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

| Role | Size | Font (Chinese) | Font (English) | Weight |
|------|------|----------------|----------------|--------|
| Main title | 36-48px | Microsoft YaHei | Arial | bold |
| Subtitle | 24-28px | Microsoft YaHei | Arial | bold |
| Body text | 18-22px | Microsoft YaHei | Calibri | normal |
| Caption / annotation | 12-14px | Microsoft YaHei | Arial | normal |
| Page number | 12-14px | — | Arial | normal |

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

---

## Layout Patterns (1280×720 canvas)

| Pattern | Description | Key Coordinates |
|---------|-------------|----------------|
| Title + subtitle centered | Cover / chapter page | Title y≈300, subtitle y≈380 |
| Top header bar + body | Standard content page | Header h=100-120, body starts y≈160 |
| Left-right split | Image + text | Left x=40..620, Right x=660..1240 |
| Three-column cards | Feature list | x=40,440,840 each w=380, gap=20 |
| Full-image + overlay | Visual impact cover | Image fills canvas, gradient overlay, text on top |

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
    failed_svg: str = "",
    error_context: str = "",
) -> str:
    """
    构建单页 SVG 生成的 user prompt。

    Args:
        slide_plan: 单页幻灯片计划 dict，包含 slide_page, title, content,
                    includes_figure, figure_reference, includes_table,
                    table_reference, includes_equation, equation_reference,
                    presenter_notes 等字段。
        style_protocol: 风格协议字符串（来自 style_analyst）。
        total_pages: 总页数，用于页码显示。
        failed_svg: 上次失败的 SVG 代码（重试时传入）。
        error_context: 上次的错误日志（重试时传入）。

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

    # 风格协议
    sections.append("### Style Protocol\n")
    sections.append(f"{style_protocol}\n")

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
        sections.append(f"  - Description: {eq.get('description', '')}")
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
    if failed_svg or error_context:
        sections.append("### ⚠️ Retry Context\n")
        sections.append("The previous SVG generation failed. Fix the issues below.\n")
        if error_context:
            sections.append(f"**Error Log**:\n```\n{error_context}\n```\n")
        if failed_svg:
            sections.append(f"**Previous Failed SVG**:\n```xml\n{failed_svg}\n```\n")

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
            "description": "Scaled Dot-Product Attention formula",
        },
        "presenter_notes": "Explain the attention mechanism and its role in the Transformer.",
    }

    example_style = """[Theme Name] Academic Blue

[Color System]
- Primary: #003366 (titles, header bar)
- Accent: #E94560 (highlights, key numbers)
- Background: #F5F5F5 (main), #FFFFFF (cards)
- Text: #333333 (body), #FFFFFF (on dark backgrounds)

[Typography]
- Title: Microsoft YaHei + Arial, 36px, bold, #FFFFFF on dark header
- Body: Microsoft YaHei + Calibri, 18px, regular, #333333

[Visual Features]
- Rounded cards (rx=12) with soft shadow
- Header bar with gradient fill (#003366 → #005599)
- Subtle separator lines between sections

[Layout Principles]
- Top header: 100px tall, dark blue gradient, white title text
- Content area: y=140 to y=660, white/light gray cards
- Side margins: 40px left and right"""

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
