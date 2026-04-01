# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SlidesGen** - AI-powered PowerPoint presentation generator from academic PDF papers using multi-agent workflows.

Pipeline: PDF → Content Extraction → Plan → LLM generates SVG → SVG validation & finalize → SVG→DrawingML → editable PPTX.

## Quick Start

### Environment Setup

- **Python**: 3.11+ required
- **Conda env**: `slides-gen` (`conda activate slides-gen`)

```bash
# Install dependencies
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
# Run all tests
python -m pytest test/

# Run specific test
python test/test_planner.py
```

### Utility Scripts

```bash
# Visualize the LangGraph workflow as a PNG
python scripts/visualize_workflow.py

# Manually merge individual slide SVG files into one PPTX deck
python scripts/merge_slides.py
```

## Architecture

### Core Workflow (LangGraph-based)

The system uses a state-machine workflow with two parallel pipelines that converge:

```
Pipeline A (Style): analyze_image_style → check_style_protocol ─┐
                                                                 ├→ dispatch_slide_tasks → merge → review
Pipeline B (Content): extract_pdf → plan → review ──────────────┘                              |
                                                                                    Human-in-the-loop checkpoints
```

`dispatch_slide_tasks` is a no-op fan-out node (`lambda state: {}`). Its outgoing conditional edge (`map_slides_to_tasks`) dispatches parallel `Send("generate_single_slide", ...)` tasks. Max concurrency is 4 (hardcoded in `main.py`).

The entire workflow is **async** — entry point uses `asyncio.run()`, checkpointing uses `AsyncSqliteSaver`, and streaming uses `astream()`.

### Slide Subgraph (per slide, runs in parallel)

```
generate_slide_svg → check_svg_execution ─┐
        ^                                  ├→ check_slide_design → END
        └──────────── retry (max 3) ──────┘        |
                                                    └── retry (max 3)
```

Each slide runs as an independent `SlideState` subgraph compiled by `build_slide_subgraph()` in `workflow/graph.py`.

### State Management

Two TypedDict state classes control data flow:

- **OverallState** (`workflow/state.py`): Main graph state with reducers for parallel slide generation
- **SlideState**: Subgraph state for individual slide generation tasks

`generated_slide_paths` uses `Annotated[List, operator.add]` so parallel subgraph results are accumulated automatically.

`retry_slide_pages` controls partial regeneration: `None` = regenerate all slides; non-empty list = regenerate only those pages; empty list = skip all.

### Agent Modules

| Module | Purpose | Key Files |
|--------|---------|-----------|
| `agents/pdf_parser` | PDF content extraction via Marker model + multimodal image orientation fix | `extractor.py`, `image_orientation.py` |
| `agents/style_analyst` | Visual style analysis and critique from reference image | `analyzer.py`, `critic.py` |
| `agents/planner` | Presentation outline generation | `planner.py` |
| `agents/composer` | SVG generation, validation, finalization, and PPTX assembly | `svg_generator.py`, `svg_runner.py`, `svg_converter/` |
| `agents/slide_critic` | Visual quality critique (SVG→PPTX→screenshot→multimodal LLM review) | `critic.py` |

### SVG Pipeline Details

The composer module uses a multi-stage SVG pipeline:

1. **SVG Generation** (`svg_generator.py`): LLM generates SVG source code from slide plan + style protocol
2. **SVG Validation** (`svg_runner.py:validate_svg`): Checks for 15 banned SVG features (clipPath, mask, `<style>`, class, foreignObject, etc.)
3. **SVG Finalize** (`svg_converter/svg_finalize/`): 4-step post-processing — `fix_image_aspect` → `embed_images` → `flatten_tspan` → `svg_rect_to_path`
4. **SVG→PPTX** (`svg_converter/svg_to_pptx/`): Converts SVG elements to native DrawingML XML, producing editable PowerPoint shapes

### Node Configuration Injection

All nodes receive a `RunnableConfig` and extract settings via `config["configurable"]`, which carries: `pdf_path`, `style_image_path`, `output_dir`, `model_name`, `api_key`, `base_url`, `marker_path`, `verbose`. Helper `_get_llm_config(configurable)` builds `LLMConfig` from this dict.

### Review Cycles

All critical nodes use a `ReviewCycle` pattern with retry logic:

```python
class ReviewCycle(TypedDict):
    verified: bool
    retry_count: int
    critique: Optional[str]
```

Retry limits (0-based counter, fails when `retry_count >= N`):
- Style protocol: 2 (up to 3 attempts)
- SVG execution: 3 (up to 4 attempts)
- Design check: 3 (up to 4 attempts)

### Human-in-the-Loop (HITL)

Two interactive checkpoints require user input:

1. **Plan Review** (`review_plan_node`): User approves/revises presentation outline
2. **Final PPTX Review** (`review_pptx_design_node`): User approves final output or requests refinements

Feedback routing uses `analyze_feedback()` in `workflow/feedback_router.py`, which returns a `FeedbackAnalysis` Pydantic model with:
- `scope`: one of `"local"`, `"global_style"`, `"global_plan"`, `"ambiguous"`
- `target_pages`: list of slide page numbers (only populated when `scope == "local"`)

Routing based on scope:
- `global_style` → Re-analyze style image
- `global_plan` → Regenerate presentation plan
- `local` → Regenerate specific slides only
- `ambiguous` → Workflow ends (user prompted implicitly)

## Key Conventions

### LLM Configuration

All LLM calls use `LLMConfig` TypedDict for consistent configuration:

```python
from utils.llm import LLMConfig, create_llm

config = LLMConfig(model_name="gpt-4o", api_key="...", base_url="...")
llm = create_llm(config, temperature=0.0)
```

### Output Structure

```
output/
└── {session_id}/           # e.g., "0324_1557"
    ├── plan/               # Presentation plans, paper content JSON
    ├── raw/                # Extracted PDF content
    ├── style/              # Style protocols and critiques
    ├── result/             # Generated slides
    │   ├── slide_01/       # Per-slide outputs
    │   │   ├── slide_v*.svg
    │   │   └── slide_critique.json
    │   └── Final_Presentation.pptx
    ├── checkpoints/        # LangGraph checkpoint SQLite
    └── final_snapshot.json # Final workflow state
```

### Session Resumption

Use `--thread_id` to resume interrupted workflows. Checkpoints are stored in `checkpoints/checkpoints.sqlite`. The session ID format is `MMDD_HHMM` (auto-generated from run start time). When resuming, `initial_state` is `None` — the graph resumes from its SQLite checkpoint, not from a fresh state.

## Dependencies

See `requirements.txt` (no version pinning). Core libraries:
- **langchain/langgraph**: Workflow orchestration (async)
- **python-pptx**: PowerPoint generation (used by SVG→DrawingML converter)
- **marker-pdf**: PDF parsing (layout, OCR, equations, tables)
- **langchain_openai**: LLM interface

## Common Issues

### PDF Extraction Fails
- Check Marker model path (`--marker_path`, default: `models/marker`)
- Verify PDF is text-extractable (not scanned images only)

### Style Analysis Fails
- Ensure style image path is valid
- Check LLM API connectivity (supports multimodal input)

### Session Won't Resume
- Verify checkpoint database exists at `{output_dir}/checkpoints/checkpoints.sqlite`
- Use exact `--thread_id` from original run
