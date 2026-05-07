"""
Fake-LLM runner: 在不消耗任何 API 调用的前提下跑通完整 SlidesGen pipeline。

原理：
  1. 启动时把 OPENAI_* 环境变量清空，让 pdf_parser 里的原生 openai.OpenAI 客户端
     （用于图片方向检测）自动跳过；
  2. 在 import main 之前 monkey-patch `utils.llm.create_llm`，让它返回一个
     FakeChatModel —— 该模型按 pipeline 各阶段的 system prompt 指纹分派响应，
     内容直接复用 `output/0408_1155_MS/` 里已有的真实 LLM 产物作为 stub；
  3. 设置 sys.argv 等价于 launch.json，跳过两个 HITL 节点，跑 asyncio.run(main.main())。

本脚本只新增文件，不修改 agents/utils/workflow/pipeline/main.py 的任何代码。
"""

import os
import sys
import re
import json
import time
import random
import asyncio
from pathlib import Path
from typing import Any, List, Optional

try:
    import tiktoken  # noqa: F401
    _TIKTOKEN_AVAILABLE = True
except ImportError:
    _TIKTOKEN_AVAILABLE = False

# ---------------------------------------------------------------------------
# 0. 工作目录与 path
# ---------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

REFERENCE_DIR = os.path.join(ROOT, "output", "0408_1155_MS")

# 清空 API 凭据，触发 extract_pdf 里 `if api_key:` 分支跳过 image_orientation。
# load_dotenv(override=False) 不会覆盖我们预先设置的空串。
os.environ["OPENAI_API_KEY"] = ""
os.environ["OPENAI_BASE_URL"] = ""

# ---------------------------------------------------------------------------
# 1. 预加载 utils.llm 并准备 monkey-patch —— 必须在任何 agent 模块导入之前
# ---------------------------------------------------------------------------
import utils.llm as _llm_mod  # noqa: E402

from langchain_core.language_models.chat_models import BaseChatModel  # noqa: E402
from langchain_core.messages import AIMessage, BaseMessage  # noqa: E402
from langchain_core.outputs import ChatGeneration, ChatResult  # noqa: E402
from langchain_core.runnables import RunnableLambda  # noqa: E402

# ---------------------------------------------------------------------------
# 2. 加载 reference session 的产物作为 stub 内容
# ---------------------------------------------------------------------------

def _read_text(path: str) -> Optional[str]:
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception:
        return None


def _read_json(path: str) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Master Chrome Contract (IV-bis) — the reference session 0408_1155_MS predates
# this pipeline feature, so its style_protocol_v0.md has no "## IV-bis." section.
# pipeline/svg_to_pptx/master_chrome.py requires this section to inject a master
# template into the PPTX slide master; without it the deck ships with an empty
# master. We hand-craft a minimal-but-valid chrome contract and append it to the
# loaded stub so the master injection path is actually exercised.
# ---------------------------------------------------------------------------
MASTER_CHROME_STUB_SECTION = """

---

## IV-bis. Master Chrome Contract (binding for ALL slides)

This section defines the single chrome template embedded into the PPTX slide master.
All slides inherit it automatically.

### Presence table

| Region       | Present? (yes/no) | What you actually see in the reference (or "n/a") |
| ------------ | ----------------- | -------------------------------------------------- |
| header       | yes               | Thin orange accent bar across the top              |
| footer       | yes               | Light divider line near the bottom                 |
| logo         | no                | n/a                                                |
| page_number  | yes               | Small page number at bottom-right                  |

### Master Chrome SVG

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <rect x="0" y="0" width="1280" height="720" fill="#ffffff"/>
  <rect x="0" y="0" width="1280" height="6" fill="#f59e0b"/>
  <rect x="80" y="680" width="1120" height="1" fill="#cccccc"/>
  <text x="1200" y="700" font-family="Arial" font-size="14" fill="#666666" text-anchor="end">PGNUM_PLACEHOLDER</text>
</svg>
```

### Safe content bbox

`x=80 y=40 width=1120 height=620`

---
"""

_loaded_style_protocol = _read_text(os.path.join(REFERENCE_DIR, "style", "style_protocol_v0.md")) or "# Fallback Style Protocol\n- Primary: #1a2b3c\n- Accent: #f59e0b\n"
STUB_STYLE_PROTOCOL = _loaded_style_protocol + MASTER_CHROME_STUB_SECTION
STUB_MAIN_CONTENT = _read_json(os.path.join(REFERENCE_DIR, "plan", "paper_main_content.json")) or {}
STUB_PLAN = _read_json(os.path.join(REFERENCE_DIR, "plan", "presentation_plan_v0.json")) or []


def _compute_final_versions() -> dict:
    """从 final_snapshot.json 里读出 slide_page -> 最终被采纳的 slide_v{N}.svg 版本号。"""
    snap = _read_json(os.path.join(REFERENCE_DIR, "final_snapshot.json")) or {}
    paths = snap.get("generated_slide_paths", [])
    final: dict = {}
    if isinstance(paths, list):
        for p in paths:
            pn = p.replace(os.sep, "/")
            m = re.search(r"slide_(\d+)/slide_v(\d+)\.svg", pn)
            if m:
                final[int(m.group(1))] = int(m.group(2))
    return final


FINAL_VERSIONS = _compute_final_versions()


def _normalize_svg_namespace(svg: Optional[str]) -> Optional[str]:
    """Some reference SVGs use the `svg:` namespace prefix (e.g.
    ``<svg:svg xmlns:svg=...><svg:rect .../></svg:svg>``). The downstream
    `extract_svg_content` in agents/execution/svg_generator.py expects the
    default-namespace form (``<svg ...><rect .../></svg>``) and its regex
    (`<svg\\b`) won't match the prefixed form. Rewrite to the default form.
    """
    if not svg:
        return svg
    if "<svg:" not in svg and "xmlns:svg" not in svg:
        return svg
    out = svg
    out = re.sub(r"<svg:", "<", out)
    out = re.sub(r"</svg:", "</", out)
    out = re.sub(r"xmlns:svg\s*=", "xmlns=", out)
    return out


def _get_slide_svg(page: int) -> Optional[str]:
    """取目标 slide_page 的 reference SVG 内容。"""
    version = FINAL_VERSIONS.get(page)
    slide_dir = os.path.join(REFERENCE_DIR, "slides", f"slide_{page:02d}")
    svg: Optional[str] = None
    if version is not None:
        svg = _read_text(os.path.join(slide_dir, f"slide_v{version}.svg"))
    # Fallback：目录存在但没 snapshot 记录，取版本号最大的那个
    if svg is None and os.path.isdir(slide_dir):
        svgs = sorted(
            [f for f in os.listdir(slide_dir) if re.match(r"slide_v\d+\.svg$", f)],
            key=lambda s: int(re.search(r"\d+", s).group(0)),
        )
        if svgs:
            svg = _read_text(os.path.join(slide_dir, svgs[-1]))
    return _normalize_svg_namespace(svg)


def _get_slide_detail(page: int) -> Optional[str]:
    return _read_text(os.path.join(REFERENCE_DIR, "slides", f"slide_{page:02d}", "slide_detail.md"))


GENERIC_SLIDE_DETAIL = """# Stub Slide Layout (fallback)

## Title
- Position: (80, 80), size 1120x80
- Font: Inter Bold 40pt, #1a2b3c

## Body
- Position: (80, 220), size 1120x400
- Bullet list, Inter Regular 22pt, #333333
"""

GENERIC_STUB_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <rect width="1280" height="720" fill="#ffffff"/>
  <rect x="80" y="170" width="400" height="4" fill="#f59e0b"/>
  <text x="80" y="130" font-family="Arial" font-size="40" font-weight="bold" fill="#1a2b3c">Fallback Stub Slide</text>
  <text x="80" y="260" font-family="Arial" font-size="22" fill="#333333">Reference content unavailable for this page.</text>
</svg>"""

VISUAL_CRITIQUE_JSON = '{"pass": true, "critique": "Fake auditor approved this stub slide."}'


# ---------------------------------------------------------------------------
# 3. Stage 指纹识别 + 响应分派
# ---------------------------------------------------------------------------

def _detect_stage(text: str) -> str:
    """按 system / user prompt 里的角色签名判断当前 pipeline 阶段。"""
    if "PPT Design System Architect" in text:
        return "style_analyze"
    if "Design Specification Auditor" in text:
        return "style_critic"
    if "distinguished academic content analysis" in text:
        return "main_content_extraction"
    if "world-class academic presentation designer" in text:
        return "slides_planning"
    if "layout architect" in text:
        return "expand_slide_plan"
    if "Senior SVG Slide Designer" in text:
        return "svg_generation"
    if "SVG Visual Optimizer" in text:
        return "crap_optimizer"
    if "Full-Stack Visual Auditor" in text:
        return "visual_critique"
    if "scope of the requested change" in text:
        return "feedback_analyzer"
    return "unknown"


def _messages_to_text(messages: List[Any]) -> str:
    """把 messages 扁平化为单个文本，便于关键字检测。

    messages 可能是：
      - list[BaseMessage]：标准 langchain 链路
      - list[dict]（OpenAI 原始格式 {"role": ..., "content": str | list[dict]}）：
        style_critic 里 structured_llm.invoke(messages) 直接传的原始格式
    两种都要处理，否则 dict 会被 getattr("content", m) 当成自身原样返回从而被丢掉。
    """
    parts: List[str] = []
    for m in messages:
        if isinstance(m, dict):
            c = m.get("content", "")
        else:
            c = getattr(m, "content", m)
        if isinstance(c, str):
            parts.append(c)
        elif isinstance(c, list):
            for item in c:
                if isinstance(item, dict) and "text" in item:
                    parts.append(item["text"])
                elif isinstance(item, str):
                    parts.append(item)
    return "\n".join(parts)


def _extract_slide_page(text: str) -> Optional[int]:
    """从 expand/svg_generation 的 user prompt 里抓 slide_page 数字。"""
    # expand_slide_plan embeds slide_plan as JSON → "slide_page": N
    m = re.search(r'"slide_page"\s*:\s*(\d+)', text)
    if m:
        return int(m.group(1))
    # svg_generator build_svg_slide_prompt: "## Slide {page} / {total_pages}"
    m = re.search(r"##\s*Slide\s+(\d+)\s*/\s*\d+", text)
    if m:
        return int(m.group(1))
    # Legacy fallbacks
    m = re.search(r"Slide\s+(\d+)\s+of\s+\d+", text, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r"Page:\s*(\d+)", text)
    if m:
        return int(m.group(1))
    return None


def _response_for(stage: str, full_text: str) -> str:
    if stage == "style_analyze":
        return STUB_STYLE_PROTOCOL
    if stage == "main_content_extraction":
        return "```json\n" + json.dumps(STUB_MAIN_CONTENT, ensure_ascii=False, indent=2) + "\n```"
    if stage == "slides_planning":
        return json.dumps(STUB_PLAN, ensure_ascii=False, indent=2)
    if stage == "expand_slide_plan":
        page = _extract_slide_page(full_text)
        if page is not None:
            detail = _get_slide_detail(page)
            if detail:
                return detail
        return GENERIC_SLIDE_DETAIL
    if stage == "svg_generation":
        page = _extract_slide_page(full_text)
        if page is not None:
            svg = _get_slide_svg(page)
            if svg:
                return "```svg\n" + svg + "\n```"
        return "```svg\n" + GENERIC_STUB_SVG + "\n```"
    if stage == "crap_optimizer":
        # 直接回显 user prompt 里嵌入的原始 SVG，等价于“不做任何修改”
        m = re.search(r"<svg[\s\S]*?</svg>", full_text)
        if m:
            return "```svg\n" + m.group(0) + "\n```"
        return "```svg\n" + GENERIC_STUB_SVG + "\n```"
    if stage == "visual_critique":
        return "```json\n" + VISUAL_CRITIQUE_JSON + "\n```"
    # 未识别阶段：返回风格协议作为无害默认值
    return STUB_STYLE_PROTOCOL


# ---------------------------------------------------------------------------
# 3.5 Token 计数 + 延迟模拟 —— 让 run_stats.json 接近真实 api 跑
# 手动调节下方常量切换行为。
# ---------------------------------------------------------------------------

# 假装成哪个真实模型。用于 tiktoken 编码 + pricing.py 成本计算。
# 必须是 utils/instrumentation/pricing.py 的 MODEL_PRICING 里有的 key，
# 否则 cost_usd 会是 0（会在 warnings 里记一行）。
SIMULATE_AS_MODEL = "gpt-4o"

# 延迟模拟模式：
#   "off"       —— 不 sleep，秒级跑完（改 workflow 拓扑时快速冒烟）
#   "fixed"     —— 按 stage 用下方 FAKE_LATENCY_FIXED 的常量
#   "realistic" —— TTFB + completion_tokens / throughput + 抖动（推荐）
FAKE_LATENCY_MODE = "realistic"

# 全局缩放。1.0 = 原速，0.3 = 3x 加速，0.0 = 等价于 "off"
FAKE_LATENCY_SCALE = 1.0

# fixed 模式下 stage → 秒数经验值
FAKE_LATENCY_FIXED = {
    "style_analyze":           6.0,
    "style_critic":            2.0,
    "main_content_extraction": 8.0,
    "slides_planning":         10.0,
    "expand_slide_plan":       4.0,
    "svg_generation":          18.0,
    "crap_optimizer":          15.0,
    "visual_critique":         3.0,
    "feedback_analyzer":       1.5,
}

# realistic 模式参数（贴近 gpt-4o 实测：TTFB ~0.8s，输出吞吐 ~80 tok/s）
FAKE_LATENCY_TTFB_SEC = 0.8
FAKE_LATENCY_THROUGHPUT_TOKS = 80
FAKE_LATENCY_JITTER = (0.85, 1.15)


def _get_encoder():
    if not _TIKTOKEN_AVAILABLE:
        return None
    try:
        return tiktoken.encoding_for_model(SIMULATE_AS_MODEL)
    except Exception:
        try:
            return tiktoken.get_encoding("cl100k_base")
        except Exception:
            return None


_ENCODER = _get_encoder()

# 参考目录里的 SVG 已经被 svg_finalize 嵌入了 base64 图片（每张 90+ KB），
# 但真实 LLM 响应里从来没有这些 blob（它们是后处理加进去的）。
# 如果按嵌入后的体量算 token，completion 会被灌到 20x，realistic 延迟彻底失真。
# 这里在进 tiktoken 之前先把 base64 主体换成短占位符。
_BASE64_BLOB_RE = re.compile(r"(data:[^\"'<>\s]*?;base64,)[A-Za-z0-9+/=\s]+")


def _strip_base64_blobs(text: str) -> str:
    if not text or "base64," not in text:
        return text
    return _BASE64_BLOB_RE.sub(r"\1<BLOB>", text)


def _count_tokens(text: str) -> int:
    """用 tiktoken 估算 token 数；tiktoken 不可用时回退到 len(text)//4 粗略估算。

    进编码器前先剥离 base64 图片 blob —— fake 模式特有的校准：参考目录里的
    SVG 包含已嵌入的图片数据，但真实 LLM 不会在响应里吐这些 blob。
    """
    if not text:
        return 0
    text = _strip_base64_blobs(text)
    if _ENCODER is not None:
        try:
            return len(_ENCODER.encode(text, disallowed_special=()))
        except Exception:
            pass
    return max(1, len(text) // 4)


def _pick_latency(stage: str, completion_tok: int) -> float:
    """根据 FAKE_LATENCY_MODE 挑一个要 sleep 的秒数。"""
    if FAKE_LATENCY_MODE == "off" or FAKE_LATENCY_SCALE <= 0:
        return 0.0
    if FAKE_LATENCY_MODE == "fixed":
        return FAKE_LATENCY_FIXED.get(stage, 2.0) * FAKE_LATENCY_SCALE
    # realistic
    base = FAKE_LATENCY_TTFB_SEC + completion_tok / max(1, FAKE_LATENCY_THROUGHPUT_TOKS)
    jitter = random.uniform(*FAKE_LATENCY_JITTER)
    return base * jitter * FAKE_LATENCY_SCALE


def _record_tokens(prompt_tok: int, completion_tok: int, stage: Optional[str]) -> None:
    """直接把 token 统计写进 MetricsStore，绕过 LangChain callback 管线。

    理由：with_structured_output 返回 RunnableLambda，这条路径天生不经过
    callback manager；而 _generate / _agenerate 路径虽然理论上能挂 callback，
    但额外引入 RunnableBinding 包装会破坏 FakeChatModel.with_structured_output
    的重写入口。手动写 MetricsStore 是最简单稳妥的方案。
    """
    try:
        from utils.instrumentation.metrics_store import MetricsStore
        MetricsStore.record_tokens(
            model=SIMULATE_AS_MODEL,
            prompt=prompt_tok,
            completion=completion_tok,
            stage=stage,
        )
    except Exception as e:
        print(f"[fake-llm] record_tokens failed: {e}", flush=True)


def _input_to_text(input_val: Any) -> str:
    """把 RunnableLambda 收到的任意输入扁平化为字符串，用于 stage 指纹匹配。"""
    try:
        from langchain_core.prompt_values import PromptValue
        if isinstance(input_val, PromptValue):
            return _messages_to_text(input_val.to_messages())
    except Exception:
        pass
    if isinstance(input_val, list):
        return _messages_to_text(input_val)
    if isinstance(input_val, BaseMessage):
        return _messages_to_text([input_val])
    if isinstance(input_val, str):
        return input_val
    return str(input_val)


# ---------------------------------------------------------------------------
# 4. FakeChatModel —— BaseChatModel 子类
# ---------------------------------------------------------------------------

class FakeChatModel(BaseChatModel):
    """按 pipeline 阶段返回预置 stub 响应的假 ChatModel，不会发起任何网络请求。

    三件事同时做：
      1. 按 _detect_stage / _response_for 回传参考目录里的 stub 内容（内容回放）
      2. 用 tiktoken 估算 prompt/completion token 数，写进 llm_output + MetricsStore
      3. 按 FAKE_LATENCY_MODE 策略 sleep，模拟真实 api 耗时
    """

    @property
    def _llm_type(self) -> str:
        return "fake-slides-gen"

    def _build_result_and_meta(self, messages):
        text = _messages_to_text(messages)
        stage = _detect_stage(text)
        content = _response_for(stage, text)

        prompt_tok = _count_tokens(text)
        completion_tok = _count_tokens(content)
        latency = _pick_latency(stage, completion_tok)

        result = ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=content))],
            llm_output={
                "model_name": SIMULATE_AS_MODEL,
                "token_usage": {
                    "prompt_tokens": prompt_tok,
                    "completion_tokens": completion_tok,
                    "total_tokens": prompt_tok + completion_tok,
                },
            },
        )
        return result, latency, prompt_tok, completion_tok, stage

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        result, latency, ptok, ctok, stage = self._build_result_and_meta(messages)
        if latency > 0:
            time.sleep(latency)
        _record_tokens(ptok, ctok, stage)
        return result

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        result, latency, ptok, ctok, stage = self._build_result_and_meta(messages)
        if latency > 0:
            # 关键：必须 await asyncio.sleep 而不是 time.sleep，
            # 否则会阻塞事件循环，让并行度=4 的 slide 子图退化成串行。
            await asyncio.sleep(latency)
        _record_tokens(ptok, ctok, stage)
        return result

    def with_structured_output(self, schema, *, include_raw: bool = False, **kwargs):
        """为 structured_output 路径返回 RunnableLambda，同时也做 token 计数 + sleep。

        这条路径天生不走 LangChain 的 callback manager，所以手动 emit 一次到
        MetricsStore。提供 sync + async 两个实现，保证在 async 上下文里走
        asyncio.sleep 而不是阻塞事件循环的 time.sleep。
        """
        schema_name = getattr(schema, "__name__", "")

        # schema 类名 → stage 的兜底映射。用途：万一 _detect_stage 从扁平化
        # 文本里没抓到关键词（比如 prompt 拼接方式变了），仍然能把这次调用
        # 归到正确的 stage，避免掉进 tokens_by_stage["unknown"]。
        schema_stage_fallback = {
            "StyleCritique": "style_critic",
            "FeedbackAnalysis": "feedback_analyzer",
        }

        def _fabricate_instance():
            if schema_name == "StyleCritique":
                return schema(is_approved=True, critique="Fake critic approved this style protocol.")
            if schema_name == "FeedbackAnalysis":
                return schema(scope="local", target_pages=[1])
            try:
                return schema()
            except Exception:
                return None

        def _simulate(input_val):
            text = _input_to_text(input_val)
            stage = _detect_stage(text)
            if stage == "unknown":
                stage = schema_stage_fallback.get(schema_name, "unknown")
            instance = _fabricate_instance()
            try:
                if hasattr(instance, "model_dump"):
                    payload = instance.model_dump()
                elif hasattr(instance, "dict"):
                    payload = instance.dict()
                else:
                    payload = {}
            except Exception:
                payload = {}
            completion_text = json.dumps(payload, ensure_ascii=False)
            prompt_tok = _count_tokens(text)
            completion_tok = _count_tokens(completion_text)
            latency = _pick_latency(stage, completion_tok)
            return instance, prompt_tok, completion_tok, stage, latency

        def _sync(input_val):
            instance, ptok, ctok, stage, latency = _simulate(input_val)
            if latency > 0:
                time.sleep(latency)
            _record_tokens(ptok, ctok, stage)
            return instance

        async def _async(input_val):
            instance, ptok, ctok, stage, latency = _simulate(input_val)
            if latency > 0:
                await asyncio.sleep(latency)
            _record_tokens(ptok, ctok, stage)
            return instance

        return RunnableLambda(_sync, afunc=_async)


def _fake_create_llm(llm_config, temperature: float = 0.1, timeout: float = 600.0, max_retries: int = 3):
    return FakeChatModel()


# 关键：在 agents 里 `from utils.llm import create_llm` 之前完成替换
_llm_mod.create_llm = _fake_create_llm

# ---------------------------------------------------------------------------
# 5. 设置 sys.argv 并运行 main
# ---------------------------------------------------------------------------
sys.argv = [
    "main.py",
    "--pdf_path", "assets/paper.pdf",
    "--style_image_path", "assets/ref-style-img.png",
    "--output_dir", "output/",
    "--model_name", "fake-stub",
    "--marker_path", "models/marker",
    "--llm_max_retries", "3",
    "--skip_plan_review",
    "--skip_pptx_review",
]


def _banner():
    print("=" * 72, flush=True)
    print("[fake-llm-runner] All LLM calls will be served from stub content under:", flush=True)
    print(f"  {REFERENCE_DIR}", flush=True)
    print(f"[fake-llm-runner] Stub plan slides: {len(STUB_PLAN)}", flush=True)
    print(f"[fake-llm-runner] Final SVG versions loaded: {len(FINAL_VERSIONS)}", flush=True)
    print(
        f"[fake-llm-runner] simulate_as={SIMULATE_AS_MODEL}  "
        f"latency_mode={FAKE_LATENCY_MODE}  scale={FAKE_LATENCY_SCALE}  "
        f"tiktoken={_TIKTOKEN_AVAILABLE}",
        flush=True,
    )
    print("=" * 72, flush=True)


_banner()

import main  # noqa: E402  — must be imported AFTER the monkey-patch above

asyncio.run(main.main())
