# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SlidesGen** — AI-powered PowerPoint presentation generator from academic PDF papers using multi-agent workflows.

Pipeline: PDF → Content Extraction → Style Analysis → Plan → Expand → LLM generates SVG → CRAP optimization → Design review → SVG→DrawingML → editable PPTX.

## Quick Start

### Environment Setup

- **Python**: 3.11+ required
- **Conda env**: `slides-gen` (`conda activate slides-gen`)

```bash
pip install -r requirements.txt
```

### Required Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_BASE_URL=https://your-api-endpoint.com/v1
OPENAI_API_KEY=your-api-key
```

### Running the Application

```bash
# Generate slides from a PDF
python main.py --pdf_path path/to/paper.pdf --style_image_path path/to/style.png

# With custom options
python main.py --pdf_path paper.pdf --style_image_path style.png \
    --model_name gpt-4o \
    --output_dir output \
    --verbose

# Resume interrupted session
python main.py --pdf_path paper.pdf --style_image_path style.png --thread_id 0324_1557
```

### Testing

```bash
python -m pytest test/
python test/test_planner.py
```

### Utility Scripts

```bash
python scripts/visualize_workflow.py   # Visualize the LangGraph workflow as PNG
```

## Architecture

### Core Workflow (LangGraph-based)

Two parallel pipelines converge at `dispatch_slide_tasks`:

```
Pipeline A (Style): analyze_image_style → check_style_protocol ─┐
                                                                 ├→ dispatch_slide_tasks → merge → review
Pipeline B (Content): extract_pdf → plan → review ──────────────┘                              |
                                                                                    Human-in-the-loop
```

`dispatch_slide_tasks` is a no-op fan-out node (`lambda state: {}`). Its conditional edge (`map_slides_to_tasks`) dispatches parallel `Send("generate_single_slide", ...)` tasks.

The workflow is **async** — `asyncio.run()` entry point, `AsyncSqliteSaver` checkpointing, `astream()` streaming.

### Slide Subgraph (per slide, runs in parallel)

```
expand_slide_plan → generate_slide_svg → optimize_svg_crap ─┐
                           ^                   | (retry ≤3)  ├→ check_slide_design → END
                           └───────────────────┘             │        |
                           └─────────────────────────────────┘  (retry ≤5)
```

Each slide runs as an independent `SlideState` subgraph compiled by `build_slide_subgraph()` in `workflow/graph.py`.

- `optimize_svg_crap` handles both SVG validation and CRAP design optimization in one node
- On validation failure, routes back to `generate_slide_svg` (max 3 retries)
- On design critique failure, routes back to `generate_slide_svg` (max 5 retries)

### State Management

Two TypedDict state classes (`workflow/state.py`):

- **OverallState**: Main graph state. `generated_slide_paths` uses `Annotated[List, operator.add]` for parallel accumulation.
- **SlideState**: Per-slide subgraph state.

`retry_slide_pages`: `None` = regenerate all; non-empty list = specific pages only; empty list = skip all.

### Agent Modules (organized by phase)

Agents are grouped under `agents/` by workflow phase:

| Phase | Module | Purpose | Key Files |
|-------|--------|---------|-----------|
| Perception | `agents/perception/pdf_parser` | PDF content extraction via Marker + image orientation fix | `extractor.py`, `image_orientation.py` |
| Perception | `agents/perception/style_analyst` | Visual style analysis and critique from reference image | `analyzer.py`, `critic.py` |
| Planning | `agents/planning` | Presentation outline + per-slide layout expansion | `ppt_planner.py`, `slide_expander.py` |
| Execution | `agents/execution` | SVG generation + CRAP optimization + visual critique | `svg_generator.py`, `svg_optimizer.py`, `slide_critic.py` |
| Delivery | `agents/delivery` | User feedback analysis for final PPTX review routing | `feedback_analyzer.py` |

Each phase directory has a `prompts.py` containing only string constants (prompt/code separation convention).

### Pipeline Modules (non-LLM processing)

SVG processing pipeline under `pipeline/`:

| Module | Purpose |
|--------|---------|
| `pipeline/svg_validator.py` | XML validation + banned feature checks + geometry detection + `finalize_single_svg` entry |
| `pipeline/svg_finalize/` | 5-step SVG post-processing (fix aspect → add image cards → embed images → flatten tspan → rect to path) |
| `pipeline/svg_to_pptx/` | SVG → DrawingML conversion engine (11 files) |
| `pipeline/pptx_merger.py` | Merge multiple SVG slides into one PPTX |

### SVG Pipeline

1. **Generation** (`agents/execution/svg_generator.py`): LLM generates SVG from expanded plan + style protocol
2. **Validation** (`pipeline/svg_validator.py:validate_svg`): Checks XML well-formedness + 15 banned features (clipPath, mask, `<style>`, class, foreignObject, etc.)
3. **CRAP Optimization** (`agents/execution/svg_optimizer.py`): Runs geometry checks → feeds issues + SVG to LLM for design improvement
4. **Finalize** (`pipeline/svg_validator.py:finalize_single_svg`): 5-step post-processing — `fix_image_aspect` → `add_image_cards` → `embed_images` → `flatten_tspan` → `svg_rect_to_path`
5. **SVG→PPTX** (`pipeline/svg_to_pptx/`): Converts SVG elements to native DrawingML XML

### Node Configuration

All nodes receive `RunnableConfig` and extract via `config["configurable"]`. Helper `_get_llm_config(configurable, stage)` builds `LLMConfig` with multi-model support:
- `"vision"` — style extraction, image orientation (uses `vision_model`)
- `"svg"` — SVG code generation (uses `svg_model`)
- `"text"` — planning, expansion, text review (uses `text_model`, default)

Falls back to `model_name` if stage-specific model is not configured.

### Review Cycles

```python
class ReviewCycle(TypedDict):
    verified: bool
    retry_count: int
    critique: Optional[str]
```

Retry limits: Style protocol ≤2, SVG validation ≤3, Design check ≤5.

### Human-in-the-Loop

Two `interrupt()` checkpoints:
1. **Plan Review** (`review_plan_node`): User approves/revises outline
2. **Final PPTX Review** (`review_pptx_design_node`): User approves or requests changes

Feedback analysis (`analyze_feedback()` in `agents/delivery/feedback_analyzer.py`) returns a `FeedbackAnalysis` Pydantic model:
- `scope`: `"local"` | `"global_style"` | `"global_plan"` | `"ambiguous"`
- Routing: `global_style` → re-analyze style, `global_plan` → regenerate plan, `local` → regenerate specific slides, `ambiguous` → end

## Key Conventions

### Prompt/Code Separation

All `prompts.py` files contain **only string constants** — no functions, imports, or logic. Business logic that builds prompts from templates lives in the corresponding agent module (e.g., `build_svg_slide_prompt()` is in `svg_generator.py`, not `prompts.py`).

### LLM Configuration

```python
from utils.llm import LLMConfig, create_llm
config = LLMConfig(model_name="gpt-4o", api_key="...", base_url="...")
llm = create_llm(config, temperature=0.0)
```

### Output Structure

```
output/{session_id}/        # e.g., "0324_1557"
├── plan/                   # Presentation plans, paper content JSON
├── raw/                    # Extracted PDF content
├── style/                  # Style protocols and critiques
├── result/
│   ├── slide_01/           # Per-slide: slide_v*.svg, slide_critique.json
│   └── Final_Presentation.pptx
├── checkpoints/            # LangGraph checkpoint SQLite
└── final_snapshot.json
```

### Session Resumption

Use `--thread_id` to resume. Session ID format: `MMDD_HHMM`. When resuming, `initial_state` is `None` — graph resumes from SQLite checkpoint.

## Dependencies

Core libraries (see `requirements.txt`):
- **langchain/langgraph**: Async workflow orchestration
- **python-pptx**: PowerPoint generation (SVG→DrawingML)
- **marker-pdf**: PDF parsing (layout, OCR, equations, tables)
- **langchain_openai**: LLM interface
- **pdf2image + Poppler**: PPTX→image for visual review
- **tenacity**: Retry logic for external tool calls
