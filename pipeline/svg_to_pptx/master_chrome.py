"""
Inject a 'Master Chrome SVG' into a PPTX slide master.

The style_analyst writes an IV-bis section into the design specification that
contains a complete Master Chrome SVG (full-canvas background + optional
header/footer/logo/page-number elements). This module:

1. Extracts that SVG block out of the style protocol markdown.
2. Converts it through the existing SVG → DrawingML pipeline.
3. Slices the resulting <p:spTree> shapes out of the converted slide XML.
4. Replaces a ``PGNUM_PLACEHOLDER`` text run (if present) with a PowerPoint
   slide-number field that auto-increments per slide.
5. Appends the shapes into ``ppt/slideMasters/slideMaster1.xml`` and writes any
   media / relationship entries into the master with a ``chrome_`` prefix.

All XML manipulation is deterministic (linear scan, no greedy regex over
nested structures) — verified by ``test/test_master_chrome_injection.py``.
"""

from __future__ import annotations

import logging
import re
import tempfile
from pathlib import Path
from typing import Optional

from pipeline.svg_to_pptx.drawingml_converter import convert_svg_to_slide_shapes

logger = logging.getLogger(__name__)


PAGE_NUMBER_MARKER = "PGNUM_PLACEHOLDER"

_SLIDE_NUM_FIELD_TEMPLATE = (
    '<a:fld id="{{B1B2B3B4-0000-0000-0000-000000000001}}" type="slidenum">'
    '{rPr}<a:t>1</a:t></a:fld>'
)

# Match the IV-bis Master Chrome Contract section's first ```xml``` block.
_CHROME_SVG_BLOCK_RE = re.compile(
    r"##\s*IV-bis\..*?```xml\s*(<svg\b.*?</svg>)\s*```",
    re.DOTALL | re.IGNORECASE,
)

# Fallback: any ```xml``` block that contains a complete <svg>...</svg>
_FALLBACK_SVG_BLOCK_RE = re.compile(
    r"```(?:xml|svg)\s*(<svg\b.*?</svg>)\s*```",
    re.DOTALL | re.IGNORECASE,
)


def extract_master_chrome_svg(style_protocol: Optional[str]) -> Optional[str]:
    """Extract the Master Chrome SVG from the style protocol markdown.

    Returns the SVG string, or None if the protocol does not contain a
    chrome contract block.
    """
    if not style_protocol:
        return None
    m = _CHROME_SVG_BLOCK_RE.search(style_protocol)
    if m:
        return m.group(1).strip()
    # Fallback: look at any xml/svg fenced block in the protocol. We do not
    # want to silently inject random SVG, so only accept this if the protocol
    # mentions IV-bis somewhere.
    if "IV-bis" in style_protocol or "Master Chrome" in style_protocol:
        m2 = _FALLBACK_SVG_BLOCK_RE.search(style_protocol)
        if m2:
            return m2.group(1).strip()
    return None


def _slice_sptree_shapes(full_slide_xml: str) -> str:
    """Cut the shape children out of a converted slide XML so they can be
    appended into another <p:spTree> (e.g. the slide master's spTree).
    """
    m = re.search(
        r"</p:grpSpPr>\s*(.*?)\s*</p:spTree>",
        full_slide_xml,
        re.DOTALL,
    )
    if not m:
        raise RuntimeError(
            "Cannot slice spTree shapes from converted chrome SVG XML; "
            "convert_svg_to_slide_shapes output format unexpected."
        )
    return m.group(1)


def _replace_page_number_marker(shapes_xml: str) -> str:
    """Replace any <a:r>...PGNUM_PLACEHOLDER...</a:r> run with a
    <a:fld type="slidenum"> field, preserving the original <a:rPr>.

    Uses a linear scan (find marker → walk left for <a:r> → walk right for
    </a:r>) instead of greedy regex, to avoid matching across sibling shapes.
    """
    if PAGE_NUMBER_MARKER not in shapes_xml:
        return shapes_xml

    rpr_re = re.compile(r"<a:rPr\b[^>]*(?:/>|>.*?</a:rPr>)", re.DOTALL)
    out = shapes_xml
    replaced = 0

    while PAGE_NUMBER_MARKER in out:
        marker_pos = out.find(PAGE_NUMBER_MARKER)
        left_open = out.rfind("<a:r>", 0, marker_pos)
        left_close_check = out.rfind("</a:r>", 0, marker_pos)
        if left_open == -1 or (left_close_check != -1 and left_close_check > left_open):
            logger.warning(
                "Page number marker found but not enclosed in <a:r>; skipping further replacements."
            )
            break

        right_close = out.find("</a:r>", marker_pos)
        if right_close == -1:
            logger.warning("Page number marker has no matching </a:r>; aborting replacement.")
            break
        right_close_end = right_close + len("</a:r>")

        run_block = out[left_open:right_close_end]
        rpr_match = rpr_re.search(run_block)
        rpr_xml = rpr_match.group(0) if rpr_match else '<a:rPr lang="en-US"/>'

        fld_xml = _SLIDE_NUM_FIELD_TEMPLATE.format(rPr=rpr_xml)
        out = out[:left_open] + fld_xml + out[right_close_end:]
        replaced += 1

    if replaced > 0:
        logger.info(f"   -> replaced {replaced} page-number marker(s) with slide-number field")
    return out


def build_chrome_shapes(chrome_svg_text: str) -> tuple[str, dict, list]:
    """Convert chrome SVG text into spTree-ready shape XML + media + rels."""
    with tempfile.TemporaryDirectory(prefix="chrome_master_") as tmp:
        chrome_path = Path(tmp) / "chrome.svg"
        chrome_path.write_text(chrome_svg_text, encoding="utf-8")
        full_slide_xml, media_files, rel_entries = convert_svg_to_slide_shapes(
            chrome_path, slide_num=0, verbose=False
        )

    shapes_xml = _slice_sptree_shapes(full_slide_xml)
    shapes_xml = _replace_page_number_marker(shapes_xml)
    return shapes_xml, media_files, rel_entries


def inject_chrome_into_master(
    extract_dir: Path,
    chrome_svg_text: str,
) -> None:
    """Inject the chrome SVG into ``ppt/slideMasters/slideMaster1.xml``.

    Writes any media files into ``ppt/media/`` with a ``chrome_`` prefix and
    appends matching relationship entries to the slideMaster's rels file.
    """
    shapes_xml, media_files, rel_entries = build_chrome_shapes(chrome_svg_text)

    master_xml_path = extract_dir / "ppt" / "slideMasters" / "slideMaster1.xml"
    if not master_xml_path.exists():
        raise FileNotFoundError(f"slideMaster1.xml not found at {master_xml_path}")

    master_text = master_xml_path.read_text(encoding="utf-8")
    if "</p:spTree>" not in master_text:
        raise RuntimeError("slideMaster1.xml is malformed: missing </p:spTree>")
    new_master_text = master_text.replace(
        "</p:spTree>",
        f"\n{shapes_xml}\n</p:spTree>",
        1,
    )
    master_xml_path.write_text(new_master_text, encoding="utf-8")
    logger.info(f"   -> injected chrome shapes into {master_xml_path.relative_to(extract_dir)}")

    # Media files (prefixed to avoid collision with slide media)
    if media_files:
        media_dir = extract_dir / "ppt" / "media"
        media_dir.mkdir(exist_ok=True)
        for name, data in media_files.items():
            (media_dir / f"chrome_{name}").write_bytes(data)
        logger.info(f"   -> wrote {len(media_files)} chrome media file(s)")

    # Append rels (rewrite media targets to chrome_ prefix)
    if rel_entries:
        rels_path = extract_dir / "ppt" / "slideMasters" / "_rels" / "slideMaster1.xml.rels"
        if not rels_path.exists():
            logger.warning(f"slideMaster1.xml.rels not found at {rels_path}; skipping rels append")
            return
        rels_text = rels_path.read_text(encoding="utf-8")
        extra = ""
        for rel in rel_entries:
            target = rel["target"]
            if target.startswith("../media/"):
                target = target.replace("../media/", "../media/chrome_", 1)
            extra += (
                f'\n  <Relationship Id="{rel["id"]}" '
                f'Type="{rel["type"]}" Target="{target}"/>'
            )
        new_rels_text = rels_text.replace(
            "</Relationships>",
            f"{extra}\n</Relationships>",
            1,
        )
        rels_path.write_text(new_rels_text, encoding="utf-8")
        logger.info(f"   -> appended {len(rel_entries)} chrome rel(s) to slideMaster1.xml.rels")
