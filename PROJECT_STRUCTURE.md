# SlidesGen 项目结构与文件说明

本文档详细介绍 SlidesGen 项目的目录结构以及各程序文件的功能职责，帮助开发者快速理解代码组织。

## 项目简介

**SlidesGen** 是一个基于多智能体（multi-agent）工作流的 AI 演示文稿生成系统。它以学术 PDF 论文与参考样式图为输入，依次完成内容抽取 → 风格分析 → 大纲规划 → 单页扩写 → SVG 生成 → CRAP 优化 → 设计审查 → SVG→DrawingML 转换，最终输出可编辑的 PPTX 文件。整个流程基于 LangGraph 异步编排，并支持 SQLite 检查点恢复与人工干预（HITL）。

---

## 顶层目录结构

```
SlidesGen/
├── main.py                    # CLI 入口，组装并运行 LangGraph 工作流
├── requirements.txt           # Python 依赖清单
├── README.md                  # 项目说明
├── CLAUDE.md                  # Claude Code 协作指南
├── PROJECT_STRUCTURE.md       # 本文档
├── .env                       # OPENAI_BASE_URL / OPENAI_API_KEY 等密钥
│
├── agents/                    # 各阶段的 LLM 智能体（按 phase 分组）
├── pipeline/                  # 非 LLM 的 SVG 处理、PPTX 合并与渲染流水线
├── workflow/                  # LangGraph 状态机：节点、状态、图编排
├── utils/                     # 通用工具（LLM 封装、日志、运行时指标采集）
├── eval/                      # 运行后处理：slide 质量指标与日志聚合
├── scripts/                   # 辅助脚本
├── test/                      # 单元/集成测试
├── assets/                    # 示例 PDF、参考样式图、工作流图
├── models/                    # Marker PDF 解析模型权重
└── output/                    # 运行产物（每次会话一个子目录）
```

---

## 一、入口与配置

| 文件 | 功能 |
|------|------|
| `main.py` | CLI 入口。解析参数（`--pdf_path` / `--style_image_path` / `--model_name` / `--vision_model` / `--svg_model` / `--text_model` / `--thread_id` / `--output_dir` / `--verbose`），创建 session 目录（`MMDD_HHMM_{model}`），构建 `AsyncSqliteSaver` 检查点，调用 `workflow.graph.build_graph()` 编译图后通过 `astream()` 执行；支持 `--thread_id` 从断点恢复。 |
| `.env` | 存放 `OPENAI_BASE_URL` 与 `OPENAI_API_KEY`。 |
| `requirements.txt` | 核心依赖：langchain / langgraph、python-pptx、marker-pdf、langchain_openai、pdf2image、tenacity 等。 |

---

## 二、`workflow/` —— LangGraph 工作流编排

| 文件 | 功能 |
|------|------|
| `workflow/graph.py` | 构建主图与单页子图。`build_graph()` 装配两条并行管线（风格 / 内容）→ `dispatch_slide_tasks` 扇出 → 合并 → 审查；`build_slide_subgraph()` 构建单页 SVG 子图（`expand_slide_plan → generate_slide_svg → optimize_svg_crap → check_slide_design`）。包含条件边 `map_slides_to_tasks` 用于 `Send()` 并行分发。 |
| `workflow/nodes.py` | 全部节点函数实现：`extract_pdf_node`、`analyze_image_style_node`、`check_style_protocol_node`、`plan_node`、`review_plan_node`（`interrupt()`）、`expand_slide_plan_node`、`generate_slide_svg_node`、`optimize_svg_crap_node`、`check_slide_design_node`、`merge_slides_node`、`review_pptx_design_node`（`interrupt()`）等。每个节点接收 `RunnableConfig`，通过 `_get_llm_config(configurable, stage)` 读取对应阶段（vision/svg/text）的模型配置。 |
| `workflow/state.py` | 两个 `TypedDict` 状态：`OverallState`（主图，`generated_slide_paths` 用 `Annotated[Dict[int, str], _merge_slide_paths]`，按 `slide_page` 合并、后写覆盖先写）与 `SlideState`（单页子图）。包含 `ReviewCycle` 子结构（`verified` / `retry_count` / `critique`）。 |
| `workflow/__init__.py` | 包初始化。 |

---

## 三、`agents/` —— 多智能体（按工作流阶段组织）

> 约定：每个 phase 目录都有 `prompts.py`，**只存放字符串常量**；构建 prompt 的逻辑放在对应 agent 模块中。

### 3.1 Perception 感知层

| 文件 | 功能 |
|------|------|
| `agents/perception/pdf_parser/extractor.py` | 调用 marker-pdf 解析 PDF，输出文本、公式、表格、图片资产，写入 `output/{session}/raw/`。 |
| `agents/perception/pdf_parser/image_orientation.py` | 用视觉模型检测并修正抽取图像的方向（横/竖排）。 |
| `agents/perception/pdf_parser/prompts.py` | PDF 解析与方向判断的 prompt 常量。 |
| `agents/perception/style_analyst/analyzer.py` | 从参考样式图中提取「风格协议（Style Protocol）」：调色板、字体、留白、装饰元素等。 |
| `agents/perception/style_analyst/critic.py` | 对风格协议进行自检/补全，最多 2 轮重试。 |
| `agents/perception/style_analyst/prompts.py` | 风格分析与批评 prompt 常量。 |

### 3.2 Planning 规划层

| 文件 | 功能 |
|------|------|
| `agents/planning/ppt_planner.py` | 基于论文主体内容生成整套演示文稿的大纲（每页主题、要点、视觉建议）。 |
| `agents/planning/slide_expander.py` | 把单页大纲扩展为详细的版式级描述（位置、文字、图像引用），为 SVG 生成做准备。 |
| `agents/planning/prompts.py` | 规划阶段 prompt 常量。 |

### 3.3 Execution 执行层

| 文件 | 功能 |
|------|------|
| `agents/execution/svg_generator.py` | 由扩写后的页面计划 + 风格协议生成 SVG 代码；含 `build_svg_slide_prompt()` 等模板组装函数。 |
| `agents/execution/svg_optimizer.py` | 把几何/对齐检测结果与 SVG 一并交给 LLM，按 CRAP（对比/重复/对齐/亲密性）原则优化。 |
| `agents/execution/slide_critic.py` | 视觉评审：截图后调用视觉模型给出设计批评，触发最多 5 次重生成。 |
| `agents/execution/prompts.py` | 生成、优化、评审的 prompt 常量。 |

### 3.4 Delivery 交付层

| 文件 | 功能 |
|------|------|
| `agents/delivery/feedback_analyzer.py` | 分析最终 PPTX 审查阶段的用户反馈，返回 `FeedbackAnalysis` Pydantic 模型；`scope` 字段决定路由（`local` / `global_style` / `global_plan` / `ambiguous`）。 |
| `agents/delivery/prompts.py` | 反馈分析 prompt 常量。 |

---

## 四、`pipeline/` —— 非 LLM 处理流水线

| 文件 | 功能 |
|------|------|
| `pipeline/svg_validator.py` | XML 良构性校验 + 15 项禁用特性检查（`clipPath`、`mask`、`<style>`、`class`、`foreignObject` 等）+ 几何检测；提供 `validate_svg()` 与 `finalize_single_svg()` 入口。 |
| `pipeline/clean_svg.py` | 临时性 SVG 清理实验脚本（不在主流程中使用）。 |
| `pipeline/finalize_svg.py` | 将 `svg_finalize/` 收尾流程包装为可对整目录批量离线后处理的 CLI。 |
| `pipeline/pptx_merger.py` | 把多张已转换的 SVG 单页合并为一个 `Final_Presentation.pptx`。 |
| `pipeline/pptx_imaging.py` | 通过 LibreOffice (`soffice`) + pdf2image 把 PPTX 渲染为图像，供视觉评审使用。 |
| `pipeline/svg_to_pptx_runner.py` | SVG→PPTX 流程的 runner 包装，向后兼容的 CLI 入口。 |

### 4.1 `pipeline/svg_finalize/` —— SVG 收尾五步

| 文件 | 功能 |
|------|------|
| `fix_image_aspect.py` | 修正 `<image>` 宽高比，避免被压扁。 |
| `embed_images.py` | 把外部图片以 base64 内嵌到 SVG。 |
| `embed_icons.py` | 内嵌图标资源。 |
| `crop_images.py` | 按目标框对图像做智能裁切。 |
| `flatten_tspan.py` | 把多行 `<tspan>` 拍平为多个独立 `<text>`，规避 DrawingML 转换时的换行问题。 |
| `svg_rect_to_path.py` | 把 `<rect>`（含圆角）转为 `<path>`，统一后续转换。 |

### 4.2 `pipeline/svg_to_pptx/` —— SVG → DrawingML 转换引擎

| 文件 | 功能 |
|------|------|
| `pptx_builder.py` | 转换主流程：读取 SVG，遍历元素，调用各 helper，生成 PPTX。 |
| `pptx_cli.py` | 命令行入口（独立运行 SVG→PPTX）。 |
| `pptx_discovery.py` | 在源目录中发现待处理的 SVG 文件列表。 |
| `pptx_dimensions.py` | viewBox / EMU 单位换算。 |
| `pptx_slide_xml.py` | 生成 `slideN.xml` 的骨架与命名空间。 |
| `pptx_media.py` | 处理嵌入的图像 / 媒体资源关系（rels）。 |
| `pptx_notes.py` | 写入演讲者备注。 |
| `drawingml_converter.py` | 把 SVG 元素分发到具体的 DrawingML 生成函数。 |
| `drawingml_elements.py` | `<rect>` / `<circle>` / `<text>` / `<image>` 等元素到 DrawingML 形状的映射。 |
| `drawingml_paths.py` | SVG path d 属性解析与 DrawingML `<a:path>` 输出。 |
| `drawingml_styles.py` | 填充、描边、字体、颜色、透明度等样式翻译。 |
| `drawingml_context.py` | 转换上下文（id 计数、当前变换矩阵等）。 |
| `drawingml_utils.py` | 通用辅助函数（数值格式化、属性读取等）。 |

---

## 五、`utils/` —— 通用工具

| 文件 | 功能 |
|------|------|
| `utils/llm.py` | LLM 封装：`LLMConfig` 数据类与 `create_llm()` 工厂；统一处理 base_url / api_key / temperature / 重试；自动挂载 `TokenCountingCallback` 采集 token 计数。 |
| `utils/logging.py` | 日志基础设施：`_Tee` 双写流（控制台 + 会话日志文件，兼容 tqdm 的 `\r` 进度条）与 `setup_logging()` 会话级日志配置（含 `sys.excepthook` 兜底）。 |
| `utils/instrumentation/__init__.py` | 运行时指标采集包入口，导出 `MetricsStore` 与 `time_node` 装饰器。 |
| `utils/instrumentation/metrics_store.py` | 线程安全的单例累加器：记录每个节点耗时、分模型 token 用量、分 stage token 用量、未知模型警告等。 |
| `utils/instrumentation/node_timer.py` | `@time_node(name)` 装饰器，将节点函数耗时写入 `MetricsStore`。 |
| `utils/instrumentation/token_callback.py` | LangChain 异步回调：从 LLM 响应中提取 token 计数并写入 `MetricsStore`。 |
| `utils/instrumentation/pricing.py` | 模型单价表与 `calc_cost()` / `is_known()` 计算函数。 |

---

## 六、`eval/` —— 运行后处理

| 文件 | 功能 |
|------|------|
| `eval/slide_metrics.py` | `compute_slide_metrics()`：基于 `slide_reports` 与 plan 聚合单页质量指标，写入 `run_stats.json` 的 `slide_metrics` 字段。 |
| `eval/parse_logs.py` | 读取 `run_stats.json` 输出 Markdown 报告的 CLI 脚本，用于事后查看。 |

---

## 七、`scripts/` 与 `test/`

| 文件 | 功能 |
|------|------|
| `scripts/visualize_workflow.py` | 把 LangGraph 工作流导出为 PNG/Mermaid，便于查看节点拓扑。 |
| `test/test_llm_call.py` | LLM 调用连通性测试。 |
| `test/test_pdf_parser.py` | PDF 解析（marker）流程测试。 |
| `test/test_soffice.py` | LibreOffice 渲染依赖检查测试。 |

---

## 八、`assets/` 与 `models/`

| 路径 | 用途 |
|------|------|
| `assets/paper.pdf` | 示例输入论文。 |
| `assets/ref-style-img.png` | 示例参考样式图。 |
| `assets/ref-ppt.pptx` | 参考 PPTX。 |
| `assets/workflow_graph.{mmd,png}` | 工作流可视化图。 |
| `models/marker/...` | marker-pdf 所需的本地模型权重（layout、text_detection、text_recognition、table_recognition、texify、inline_math_detection、ocr_error_detection）。 |

---

## 九、`output/` 运行产物

每次运行生成 `output/{MMDD_HHMM_{model}}/`：

```
output/{session_id}/
├── plan/                       # paper_main_content.json、presentation_plan_v*.json
├── raw/                        # PDF 抽取的文本与图片资产
│   └── images/                 # 图像资源
├── style/                      # 风格协议与批评结果
├── result/
│   ├── slide_01/
│   │   ├── slide_detail.md     # 单页扩写
│   │   ├── slide_v0.svg        # 各版本 SVG
│   │   └── slide_v0_critique.json
│   ├── ...
│   └── Final_Presentation.pptx # 合并后的最终 PPTX
├── checkpoints/                # LangGraph SQLite 检查点（用于 --thread_id 恢复）
├── final_snapshot.json
├── run_stats.json              # 端到端耗时、分节点耗时、分模型 token、slide 质量指标
└── log.txt
```

---

## 十、关键约定速查

- **Prompt / 代码分离**：`prompts.py` 仅含字符串；模板拼装函数留在 agent 模块中。
- **多模型路由**：节点通过 `_get_llm_config(cfg, stage)` 选择 `vision` / `svg` / `text` 三类模型，未配置时回退到 `model_name`。
- **重试上限**：风格协议 / SVG 校验 / 设计审查等所有 LLM 相关重试循环共享同一个上限 `--llm_max_retries`（默认 3）。
- **HITL 中断点**：`review_plan_node`（大纲审查）与 `review_pptx_design_node`（最终 PPTX 审查）通过 `interrupt()` 暂停等待用户反馈。
- **会话恢复**：`--thread_id` 必须传完整目录名（含模型后缀），`initial_state` 传 `None`，由 SQLite 检查点续跑。
- **运行时指标 vs 后处理**：`utils/instrumentation/` 负责运行时采集（节点耗时 / token / cost），`eval/` 负责运行后聚合与报告。
