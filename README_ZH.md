<div align="center">

# 🎨 SlidesGen: 基于多智能体协作的自动PPT生成

**AI驱动的学术演示文稿生成器**

*将研究论文自动转换为精美、可编辑的PowerPoint幻灯片。*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/Built%20with-LangGraph-1C3C3C)](https://github.com/langchain-ai/langgraph)
[![python-pptx](https://img.shields.io/badge/Output-PPTX-D24726?logo=microsoftpowerpoint&logoColor=white)](https://python-pptx.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#)

</div>

---

## ✨ 概述

**SlidesGen** 是一个多智能体系统，能将学术PDF论文转换为精美、完全可编辑的PowerPoint演示文稿。它结合了LLM推理、视觉分析和确定性的SVG → DrawingML流程，生成看起来经过设计而非生成的幻灯片。

```
PDF  ─►  内容提取  ─►  风格分析  ─►  规划  ─►  展开
                                              │
                                              ▼
可编辑PPTX  ◄─  SVG → DrawingML  ◄─  设计审核  ◄─  SVG生成
```

## 🚀 核心功能

- 📄 **PDF理解** — 通过Marker支持布局、OCR、公式和表格识别
- 🎨 **风格转移** — 从任何参考图像提取视觉协议
- 🧠 **多智能体规划** — 大纲 → 逐页布局 → SVG生成
- 🔁 **自我修正** — 统一重试预算（`--llm_max_retries`，默认3次）覆盖风格协议、SVG验证和CRAP设计评论循环
- ⚡ **并行幻灯片生成** — 每张幻灯片作为独立的LangGraph子图运行
- 👤 **人在循环中** — 批准/修订计划和最终演示文稿
- 💾 **可恢复** — SQLite检查点支持；可恢复任何中断的会话
- 🎯 **多模型支持** — 为视觉、SVG和文本阶段使用不同的LLM
- 📝 **演讲稿** — 从论文内容自动生成演讲者备注
- 📊 **内置评估** — LLM裁判评分（D1/D2/D3）+ HSV直方图，可从CLI运行

## 📦 安装

**前置条件：** Python 3.11+、Conda（推荐）、Poppler（用于PDF渲染）、LibreOffice（用于PPTX预览）。

```bash
conda create -n slides-gen python=3.11
conda activate slides-gen
pip install -r requirements.txt
```

在项目根目录创建 `.env` 文件：

```bash
OPENAI_BASE_URL=https://your-api-endpoint.com/v1
OPENAI_API_KEY=your-api-key
```

## 🏃 使用方法

### 从PDF生成幻灯片

```bash
python main.py \
    --pdf_path path/to/paper.pdf \
    --style_image_path path/to/style.png
```

### 使用自定义模型

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

### 恢复中断的会话

```bash
python main.py \
    --pdf_path paper.pdf \
    --style_image_path style.png \
    --thread_id 0407_1126_gpt-5-4
```

> 会话ID格式为 `MMDD_HHMM_{model_name}`（模型名称中的斜杠被转换为 `_`）。

## 🏛️ 架构

SlidesGen 基于 **LangGraph** 构建，具有两条并行管道，在扇出幻灯片生成器处汇聚：

```
                ┌─ analyze_image_style ─► check_style_protocol ─┐
   START ──────►│                                                ├─► dispatch ─► merge ─► review
                └─ extract_pdf ─► plan ─► review ────────────────┘   (并行)    ▲
                                                                              │
                                                                      人在循环中
```

每张幻灯片作为独立**子图**运行：

```
expand_plan → generate_svg → optimize_svg_crap → check_design → ✓
                  ▲                 │                  │
                  └── 重试 ────────┘                  │
                  └────── 重试 ───────────────────────┘
       (两个循环共享统一的 --llm_max_retries 预算)
```

### 管道阶段

| 阶段          | 模块                       | 目的                                          |
|----------------|----------------------------|--------------------------------------------------|
| 👁 感知       | `agents/perception/`       | PDF解析 + 视觉风格分析              |
| 📋 规划       | `agents/planning/`         | 大纲 + 逐页布局展开             |
| 🎨 执行       | `agents/execution/`        | SVG生成 + CRAP优化 + 评论    |
| 📤 交付       | `agents/delivery/`         | 用户反馈分析 & 路由                 |
| 🔧 流程       | `pipeline/`                | SVG验证、最终化、SVG → DrawingML        |

## 📁 输出结构

```
output/0415_2157_GCM/
├── plan/                    # 演示文稿计划和论文内容
├── raw/                     # 提取的PDF内容（images/）
├── style/                   # 风格协议和评论
├── slides/
│   ├── slide_01/            # slide_v*.svg、slide_detail.md、slide_critique.json
│   ├── slide_02/
│   └── Final_Presentation.pptx
├── checkpoints/             # LangGraph SQLite检查点
├── final_snapshot.json      # 最终图状态快照
├── run_stats.json           # 时序、逐节点统计、逐模型token
└── log.txt                  # 会话日志
```

## 📊 评估

SlidesGen包含内置的LLM裁判评估框架（`metrics/`），在三个维度上对生成的演示文稿评分（每个0-5分）：

| 维度 | 衡量内容 |
|-----------|-----------------|
| **D1 内容** | 信息准确性、完整性、逻辑连贯性、密度 |
| **D2 设计** | 色彩/对比度、排版、布局/对齐、视觉丰富度 |
| **D3 风格转移** | 对参考风格图像的忠实度（色彩、排版、布局、装饰） |

加上一个客观指标：**HSV色彩直方图相似度**（OpenCV，无需LLM）。

### CLI评估

```bash
# 直接从命令行评估生成的PPTX
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
# result 包含每张幻灯片和聚合的 D1、D2、D3 和 HSV 相似度评分
```

## 🛠️ 实用脚本

```bash
python scripts/visualize_workflow.py          # 将LangGraph工作流渲染为PNG/Mermaid/ASCII
python scripts/run_with_fake_llm.py           # 使用存根LLM运行完整流程（无API调用）
python scripts/convert_svg_folder_to_pptx.py  # 批量转换SVG文件夹为PPTX（主Chrome + 备注）
```

## 📚 技术栈

| 库                   | 角色                                       |
|----------------------|--------------------------------------------|
| `langgraph`          | 异步多智能体工作流编排   |
| `langchain_openai`   | LLM接口                              |
| `marker-pdf`         | PDF解析（布局、OCR、公式）       |
| `python-pptx`        | PowerPoint生成                      |
| `pdf2image` + Poppler| PPTX → 图像渲染用于视觉审查   |
| `opencv-python-headless` | 色彩直方图相似度评估 |
| `numpy`              | HSV色彩直方图计算            |
| `pydantic`           | 数据验证和结构化输出      |
| `tenacity`           | 外部工具调用重试逻辑        |
| `torch`              | 深度学习后端（marker-pdf / surya） |

## 📜 许可证

MIT © SlidesGen 贡献者

---

<div align="center">

*基于LangGraph构建 · 由LLM驱动 · 为研究人员设计*

</div>
