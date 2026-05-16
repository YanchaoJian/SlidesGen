<div align="center">

# 🎨 SlidesGen: Automatic PPT Generation Based on Multi-Agent Collaboration

**AI-Powered Academic Presentation Generator**

*Turn research papers into beautiful, editable PowerPoint slides — automatically.*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/Built%20with-LangGraph-1C3C3C)](https://github.com/langchain-ai/langgraph)
[![python-pptx](https://img.shields.io/badge/Output-PPTX-D24726?logo=microsoftpowerpoint&logoColor=white)](https://python-pptx.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#)

</div>

---

## ✨ Overview

**SlidesGen** is a multi-agent system that transforms academic PDF papers into polished, fully-editable PowerPoint presentations. It combines LLM reasoning, vision analysis, and a deterministic SVG → DrawingML pipeline to produce slides that look designed — not generated.

```
PDF  ─►  Content Extraction  ─►  Style Analysis  ─►  Plan  ─►  Expand
                                                                  │
                                                                  ▼
Editable PPTX  ◄─  SVG → DrawingML  ◄─  Design Review  ◄─  SVG Generation
```

## 🚀 Key Features

- 📄 **PDF understanding** — Layout, OCR, equations, and tables via Marker
- 🎨 **Style transfer** — Extracts a visual protocol from any reference image
- 🧠 **Multi-agent planning** — Outline → per-slide layout → SVG generation
- 🔁 **Self-correcting** — Unified retry budget (`--llm_max_retries`, default 3) covers style protocol, SVG validation, and CRAP design critique loops
- ⚡ **Parallel slide generation** — Each slide runs as an independent LangGraph subgraph
- 👤 **Human-in-the-loop** — Approve/revise the plan and the final deck
- 💾 **Resumable** — SQLite-checkpointed; resume any interrupted session
- 🎯 **Multi-model** — Different LLMs for vision, SVG, and text stages
- 📝 **Speaker notes** — Auto-generated presenter notes from paper content
- 📊 **Built-in evaluation** — LLM-as-Judge scoring (D1/D2/D3) + HSV histogram, runnable from CLI

## 📦 Installation

**Prerequisites:** Python 3.11+, Conda (recommended), Poppler (for PDF rendering), LibreOffice (for PPTX preview).

```bash
conda create -n slides-gen python=3.11
conda activate slides-gen
pip install -r requirements.txt
```

Create a `.env` in the project root:

```bash
OPENAI_BASE_URL=https://your-api-endpoint.com/v1
OPENAI_API_KEY=your-api-key
```

## 🏃 Usage

### Generate slides from a PDF

```bash
python main.py \
    --pdf_path path/to/paper.pdf \
    --style_image_path path/to/style.png
```

### With custom models per stage

```bash
python main.py \
    --pdf_path paper.pdf \
    --style_image_path style.png \
    --model_name gpt-5.4 \
    --vision_model gemini-3.1-pro-preview \
    --svg_model glm-5 \
    --text_model claude-sonnet-4-6 \
    --verbose
```

### Resume an interrupted session

```bash
python main.py \
    --pdf_path paper.pdf \
    --style_image_path style.png \
    --thread_id 0407_1126_gpt-5-4
```

> Session IDs are formatted as `MMDD_HHMM_{model_name}` (slashes in model names are sanitized to `_`).

## 🏛️ Architecture

SlidesGen is built on **LangGraph** with two parallel pipelines that converge on a fan-out slide generator:

```
                ┌─ analyze_image_style ─► check_style_protocol ─┐
   START ──────►│                                                ├─► dispatch ─► merge ─► review
                └─ extract_pdf ─► plan ─► review ────────────────┘   (parallel)    ▲
                                                                                   │
                                                                           Human-in-the-loop
```

Each slide runs as an independent **subgraph**:

```
expand_plan → generate_svg → optimize_svg_crap → check_design → ✓
                  ▲                 │                  │
                  └── retry ────────┘                  │
                  └────── retry ───────────────────────┘
       (both loops share the unified --llm_max_retries budget)
```

### Pipeline Phases

| Phase          | Module                     | Purpose                                          |
|----------------|----------------------------|--------------------------------------------------|
| 👁 Perception  | `agents/perception/`       | PDF parsing + visual style analysis              |
| 📋 Planning    | `agents/planning/`         | Outline + per-slide layout expansion             |
| 🎨 Execution   | `agents/execution/`        | SVG generation + CRAP optimization + critique    |
| 📤 Delivery    | `agents/delivery/`         | User feedback analysis & routing                 |
| 🔧 Pipeline    | `pipeline/`                | SVG validation, finalize, SVG → DrawingML        |

## 📁 Output Structure

```
output/0415_2157_GCM/
├── plan/                    # Presentation plan & paper content
├── raw/                     # Extracted PDF content (images/)
├── style/                   # Style protocols & critiques
├── slides/
│   ├── slide_01/            # slide_v*.svg, slide_detail.md, slide_critique.json
│   ├── slide_02/
│   └── Final_Presentation.pptx
├── checkpoints/             # LangGraph SQLite checkpoint
├── final_snapshot.json      # Final graph state snapshot
├── run_stats.json           # Timing, per-node stats, per-model tokens
└── log.txt                  # Session log
```

## 📊 Evaluation

SlidesGen includes a built-in LLM-as-Judge evaluation framework (`metrics/`) that scores generated presentations on three dimensions (0-5 each):

| Dimension | What it measures |
|-----------|-----------------|
| **D1 Content** | Information accuracy, completeness, logical coherence, density |
| **D2 Design** | Color/contrast, typography, layout/alignment, visual richness |
| **D3 Style Transfer** | Faithfulness to the reference style image (color, typography, layout, decorations) |

Plus an objective metric: **HSV color histogram similarity** (OpenCV, no LLM needed).

### CLI evaluation

```bash
# Evaluate a generated PPTX directly from the command line
python -m metrics.evaluate \
    --pptx_path output/.../slides/Final_Presentation.pptx \
    --style_image_path style.png \
    --model_name gpt-5.4-nano \
    --dpi 200
```

### Python API

```python
from metrics import evaluate_pptx
from utils.llm import LLMConfig

llm_config = LLMConfig(model_name="gpt-5.4-nano", api_key="...", base_url="...")
result = await evaluate_pptx(
    "output/.../slides/Final_Presentation.pptx",
    llm_config,
    style_image_path="style.png",
)
# result contains per-slide and aggregated scores for D1, D2, D3, and HSV similarity
```

## 🛠️ Utility Scripts

```bash
python scripts/visualize_workflow.py          # Render the LangGraph workflow as PNG/Mermaid/ASCII
python scripts/run_with_fake_llm.py           # Run full pipeline with stub LLM (no API calls)
python scripts/convert_svg_folder_to_pptx.py  # Batch convert SVG folder to PPTX (master chrome + notes)
```

## 📚 Tech Stack

| Library              | Role                                       |
|----------------------|--------------------------------------------|
| `langgraph`          | Async multi-agent workflow orchestration   |
| `langchain_openai`   | LLM interface                              |
| `marker-pdf`         | PDF parsing (layout, OCR, equations)       |
| `python-pptx`        | PowerPoint generation                      |
| `pdf2image` + Poppler| PPTX → image rendering for visual review   |
| `opencv-python-headless` | Color histogram similarity for evaluation |
| `numpy`              | HSV color histogram computation            |
| `pydantic`           | Data validation and structured output      |
| `tenacity`           | Retry logic for external tool calls        |
| `torch`              | Deep learning backend (marker-pdf / surya) |

## 📜 License

MIT © SlidesGen contributors

---

<div align="center">

*Built with LangGraph · Powered by LLMs · Designed for researchers*

</div>
