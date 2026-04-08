"""
Strip full-canvas background rects from a slide SVG.

The PPTX slide master owns the background, header, footer, logo and page
number. Each individual slide must therefore not draw a full-canvas
background — otherwise it would cover the master and break the chrome
inheritance. This module is the deterministic safety net for the case where
the LLM still emits one despite the prompt rules.

Strategy: regex-match every self-closing ``<rect ... width="1280"
height="720" .../>`` (the canonical full-canvas background written by the
generator) and remove it. Both attribute orders (``width`` before ``height``
and vice versa) are handled.
"""

import logging
import re
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)


_FULL_CANVAS_RECT_RE = re.compile(
    r'<rect\b[^/>]*\bwidth\s*=\s*"1280"[^/>]*\bheight\s*=\s*"720"[^/>]*/\s*>',
    re.IGNORECASE,
)
_FULL_CANVAS_RECT_RE_REVERSED = re.compile(
    r'<rect\b[^/>]*\bheight\s*=\s*"720"[^/>]*\bwidth\s*=\s*"1280"[^/>]*/\s*>',
    re.IGNORECASE,
)


def strip_full_canvas_background(svg_text: str) -> Tuple[str, int]:
    """Remove every full-canvas (1280x720) self-closing rect from svg_text.

    Returns:
        (new_svg_text, removed_count)
    """
    new_text, n1 = _FULL_CANVAS_RECT_RE.subn("", svg_text)
    new_text, n2 = _FULL_CANVAS_RECT_RE_REVERSED.subn("", new_text)
    return new_text, n1 + n2


def strip_full_canvas_background_in_file(svg_path: str) -> int:
    """Apply ``strip_full_canvas_background`` to a file in place.

    Returns the number of removed rects.
    """
    path = Path(svg_path)
    text = path.read_text(encoding="utf-8")
    new_text, n = strip_full_canvas_background(text)
    if n > 0:
        path.write_text(new_text, encoding="utf-8")
        logger.debug(f"   -> stripped {n} full-canvas background rect(s) from {path.name}")
    return n
