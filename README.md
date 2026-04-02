# SlidesGen

AI-powered presentation generator that converts academic PDF papers into editable PowerPoint slides using multi-agent workflows.

**Pipeline**: PDF &rarr; Content Extraction &rarr; Style Analysis &rarr; Slide Planning &rarr; SVG Generation &rarr; SVG Validation & Finalize &rarr; DrawingML Conversion &rarr; Editable PPTX

## Features

- **End-to-end automation** &mdash; drop in a PDF and a style reference image, get a polished PPTX
- **Style transfer** &mdash; extracts a reusable Design Specification from any reference slide image (colors, typography, layout, components)
- **SVG-native pipeline** &mdash; LLM generates SVG source code that is converted to native, editable PowerPoint shapes (not embedded images)
- **Component-driven design** &mdash; built-in design component library (content cards, numbered badges, info/warning boxes, flow arrows, data badges) ensures professional-quality output
- **Visual quality assurance** &mdash; automated screenshot-based critique with geometric validation and aesthetic scoring (P0 geometry &rarr; P1 readability &rarr; P2 design polish)
- **Feedback loop** &mdash; visual critique feedback is passed back to the SVG generator for targeted fixes
- **Human-in-the-loop** &mdash; two interactive checkpoints for plan review and final PPTX approval
- **Session resumption** &mdash; interrupt and resume any workflow via SQLite checkpoints
- **Parallel slide generation** &mdash; slides are generated concurrently (max 4) via LangGraph's `Send` API
- **Multi-model support** &mdash; configure separate models for vision, SVG generation, and text tasks

## Quick Start

### Prerequisites

- Python 3.11+
- [LibreOffice](https://www.libreoffice.org/) (for PPTX &rarr; screenshot conversion during visual critique)
- [Poppler](https://poppler.freedesktop.org/) (for PDF &rarr; image rendering)

### Installation

```bash
# Clone the repository
git clone <repo-url> && cd SlidesGen

# Create and activate conda environment
conda create -n slides-gen python=3.11 -y
conda activate slides-gen

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_BASE_URL=https://your-api-endpoint.com/v1
OPENAI_API_KEY=your-api-key
```

### Usage

```bash
# Basic usage
python main.py --pdf_path paper.pdf --style_image_path style.png

# With custom models for different stages
python main.py --pdf_path paper.pdf --style_image_path style.png \
    --model_name gpt-4o \
    --vision_model gpt-4o \
    --svg_model gpt-4o \
    --text_model gpt-4o

# Skip interactive reviews (fully automated)
python main.py --pdf_path paper.pdf --style_image_path style.png \
    --skip_plan_review --skip_pptx_review

# Resume an interrupted session
python main.py --pdf_path paper.pdf --style_image_path style.png \
    --thread_id 0324_1557

# Enable debug logging
python main.py --pdf_path paper.pdf --style_image_path style.png --verbose
```

### Command-Line Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--pdf_path` | *required* | Path to the input PDF file |
| `--style_image_path` | *required* | Path to the reference style image |
| `--output_dir` | `output` | Root directory for all outputs |
| `--model_name` | `gpt-4o` | Default LLM model (fallback for all stages) |
| `--vision_model` | *model_name* | Model for vision tasks (style extraction, image orientation) |
| `--svg_model` | *model_name* | Model for SVG code generation |
| `--text_model` | *model_name* | Model for text tasks (planning, expansion, critique) |
| `--marker_path` | `models/marker` | Path to the local Marker model directory |
| `--skip_plan_review` | `false` | Auto-approve the presentation plan |
| `--skip_pptx_review` | `false` | Auto-approve the final PPTX |
| `--thread_id` | *auto* | Session ID for resuming an interrupted workflow |
| `--verbose` | `false` | Enable debug logging |

## Architecture

### Workflow Overview

The system uses a LangGraph state-machine workflow with two parallel pipelines that converge:

```
Pipeline A (Style):
  analyze_image_style --> check_style_protocol ──┐
                                                 ├──> dispatch_slide_tasks --> merge --> review
Pipeline B (Content):                            │                                       |
  extract_pdf --> plan --> review ────────────────┘                            Human-in-the-loop
```

### Slide Generation Subgraph (per slide, runs in parallel)

```
expand_slide_plan --> generate_slide_svg --> check_svg_execution ──┐
                          ^                                        ├──> check_slide_design --> END
                          └──── retry (syntax errors) ────────────┘          |
                          └──── retry (design critique) ─────────────────────┘
```

### Agent Modules

| Module | Directory | Purpose |
|--------|-----------|---------|
| **PDF Parser** | `agents/pdf_parser/` | PDF content extraction via Marker + multimodal image orientation fix |
| **Style Analyst** | `agents/style_analyst/` | Design Specification extraction from reference image + self-critique |
| **PPT Planner** | `agents/ppt_planner/` | Presentation outline generation (PMRC framework) |
| **Slide Planner** | `agents/slide_planner/` | Per-slide layout expansion with component type selection |
| **Slide Composer** | `agents/slide_composer/` | SVG generation with design component library |
| **Slide Reviewer** | `agents/slide_reviewer/` | Visual quality critique (P0 geometry, P1 readability, P2 design polish) |

### SVG Pipeline

1. **SVG Generation** &mdash; LLM generates SVG using a component library (cards, badges, info boxes, flow arrows)
2. **SVG Validation** &mdash; checks banned features (clipPath, mask, style, etc.) + geometric pre-validation (overlap/overflow detection)
3. **SVG Finalize** &mdash; 5-step post-processing:
   - `fix_image_aspect` &rarr; correct image aspect ratios for PowerPoint
   - `add_image_card` &rarr; add white card backing for paper-extracted images
   - `embed_images` &rarr; inline external images as base64
   - `flatten_tspan` &rarr; convert tspan elements to independent text elements
   - `svg_rect_to_path` &rarr; convert rounded rects to paths (preserves corners in PPTX)
4. **SVG &rarr; PPTX** &mdash; converts SVG elements to native DrawingML XML

### Design Component Library

The SVG generator uses a built-in component library to produce professional slides:

| Component | Purpose |
|-----------|---------|
| **Content Card** | White rounded rect + colored header strip + body content |
| **Numbered Badge** | Colored circle with white number for ordered items |
| **Info/Warning/Success Box** | Colored background strip for contextual messages |
| **Decorative Elements** | Top accent bar, corner circles, separator lines |
| **Flow Arrows** | Path + polygon connectors for process diagrams |
| **Data Emphasis Badge** | Bordered rect for highlighting key metrics |

## Output Structure

```
output/
└── {session_id}/              # e.g. "0324_1557"
    ├── plan/                  # Presentation plan, paper content JSON
    ├── raw/                   # Extracted PDF content
    ├── style/                 # Style protocols and critiques
    ├── result/                # Generated slides
    │   ├── slide_01/          # Per-slide outputs
    │   │   ├── slide_v0.svg   # SVG versions (v0, v1, ... for retries)
    │   │   └── slide_v0_critique.json
    │   └── Final_Presentation.pptx
    ├── checkpoints/           # LangGraph checkpoint SQLite
    └── final_snapshot.json    # Final workflow state
```

## Utility Scripts

```bash
# Visualize the LangGraph workflow as a PNG
python scripts/visualize_workflow.py

# Manually merge individual slide SVG files into one PPTX deck
python scripts/merge_slides.py
```

## Testing

```bash
# Run all tests
python -m pytest test/

# Run a specific test
python test/test_slide_review_regen.py
```

## License

All rights reserved.
