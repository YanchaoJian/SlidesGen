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
- 🔁 **Self-correcting** — CRAP design critique loop (≤5 retries) + SVG validation (≤3 retries)
- ⚡ **Parallel slide generation** — Each slide runs as an independent LangGraph subgraph
- 👤 **Human-in-the-loop** — Approve/revise the plan and the final deck
- 💾 **Resumable** — SQLite-checkpointed; resume any interrupted session
- 🎯 **Multi-model** — Different LLMs for vision, SVG, and text stages

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
    --model_name gpt-4o \
    --vision_model gpt-4o \
    --svg_model claude-opus-4-6 \
    --text_model gpt-4o \
    --verbose
```

### Resume an interrupted session

```bash
python main.py \
    --pdf_path paper.pdf \
    --style_image_path style.png \
    --thread_id 0407_1126_gpt-4o
```

> Session IDs are formatted as `MMDD_HHMM_{model_name}` (slashes in model names are sanitized to `_`).

## 🏛️ Architecture

SlidesGen is built on **LangGraph** with two parallel pipelines that converge on a fan-out slide generator:

```
                ┌─ analyze_image_style ─► check_style_protocol ─┐
   START ──────►│                                                ├─► dispatch ─► merge ─► review
                └─ extract_pdf ─► plan ─► review ────────────────┘    (parallel)     ▲
                                                                                     │
                                                                            Human-in-the-loop
```

Each slide runs as an independent **subgraph**:

```
expand_plan → generate_svg → optimize_svg_crap → check_design → ✓
                  ▲                  │                  │
                  └── retry ≤3 ──────┘                  │
                  └────── retry ≤5 ─────────────────────┘
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
output/0407_1126_gpt-4o/
├── plan/                    # Presentation plan & paper content
├── raw/                     # Extracted PDF content
├── style/                   # Style protocols & critiques
├── result/
│   ├── slide_01/            # slide.pptx, code_v*.py, slide_critique.json
│   ├── slide_02/
│   └── Final_Presentation.pptx
├── checkpoints/             # LangGraph SQLite checkpoint
└── final_snapshot.json
```

## 🧪 Testing

```bash
python -m pytest test/

# Or run individual probes
python test/test_llm_call.py
python test/test_pdf_parser.py
python test/test_soffice.py
```

## 🛠️ Utility Scripts

```bash
python scripts/visualize_workflow.py   # Render the LangGraph workflow as PNG
```

## 🧩 Key Conventions

- **Prompt/code separation** — `prompts.py` files contain only string constants. Logic that builds prompts lives in the agent module.
- **Stage-specific models** — `vision` / `svg` / `text` stages each pick from `--vision_model` / `--svg_model` / `--text_model`, falling back to `--model_name`.
- **Async-first** — `asyncio.run()` entry, `AsyncSqliteSaver` checkpointing, `astream()` for live updates.

## 📚 Tech Stack

| Library              | Role                                       |
|----------------------|--------------------------------------------|
| `langgraph`          | Async multi-agent workflow orchestration   |
| `langchain_openai`   | LLM interface                              |
| `marker-pdf`         | PDF parsing (layout, OCR, equations)       |
| `python-pptx`        | PowerPoint generation                      |
| `pdf2image` + Poppler| PPTX → image rendering for visual review   |
| `tenacity`           | Retry logic for external tool calls        |

## 📜 License

MIT © SlidesGen contributors

---

<div align="center">

*Built with LangGraph · Powered by LLMs · Designed for researchers*

</div>
