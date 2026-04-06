import os
import logging
from typing import Any, Dict

from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt

from agents.perception.pdf_parser.extractor import extract_pdf
from agents.perception.style_analyst.analyzer import analyze_style
from agents.perception.style_analyst.critic import critique_style_protocol
from agents.planning.ppt_planner import plan_presentation
from agents.planning.slide_expander import expand_slide_plan
from agents.execution.svg_generator import generate_slide_svg
from agents.execution.slide_critic import evaluate_and_critique_slide
from agents.execution.svg_optimizer import optimize_svg_crap
from agents.delivery.feedback_analyzer import analyze_feedback
from pipeline.pptx_merger import merge_svgs_to_pptx
from utils.llm import LLMConfig, create_llm
from workflow.state import OverallState, SlideState

logger = logging.getLogger(__name__)


def _get_llm_config(configurable: Dict[str, Any], stage: str = "text") -> LLMConfig:
    """
    从 configurable 字典中提取 LLM 连接配置。

    Args:
        configurable: RunnableConfig["configurable"] 字典。
        stage: 阶段标识，决定使用哪个模型。
            - "vision": 风格提取、图片方向检测等视觉任务
            - "svg": SVG 代码生成
            - "text": 大纲规划、内容扩展、文本审查等（默认）
    """
    model_key = {
        "vision": "vision_model",
        "svg": "svg_model",
        "text": "text_model",
    }.get(stage, "text_model")

    model_name = configurable.get(model_key) or configurable["model_name"]
    return LLMConfig(
        model_name=model_name,
        api_key=configurable["api_key"],
        base_url=configurable["base_url"],
    )


# ==============================================================================
# Phase 1: 感知与反思 (Perception & Reflection)
# ==============================================================================

def extract_content_from_pdf_node(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] 提取 PDF 基础内容"""
    logger.info("--- NODE: ExtractContentFromPDF ---")
    config = config["configurable"]
    
    vision_config = _get_llm_config(config, stage="vision")
    base_content, _, _ = extract_pdf(
        pdf_path=config["pdf_path"],
        marker_path=config["marker_path"],
        output_dir=config["output_dir"],
        api_key=config.get("api_key"),
        base_url=config.get("base_url"),
        model_name=vision_config["model_name"],
    )
    
    if not base_content:
        logger.error("❌ Fatal: PDF content extraction with Marker failed.")
        raise ValueError("Fatal: PDF content extraction with Marker failed.")
        
    return {"content": base_content}


def analyze_image_style_node(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] 分析参考图,提取自然语言形式的主题风格描述"""
    logger.info("--- NODE: AnalyzeImageStyle ---")
    config = config["configurable"]
    review = state.get("style_review", {})

    style_data = analyze_style(
        previous_protocol=state.get("style_protocol"),
        previous_protocol_critique=review.get("critique"),
        style_protocol_retry_count=review.get("retry_count", 0),
        style_protocol_verified=review.get("verified", False),
        style_image_path=config["style_image_path"],
        output_dir=config['output_dir'],
        llm_config=_get_llm_config(config, stage="vision"),
    )

    if not style_data:
        logger.warning("   -> ⚠️ Style analysis failed. This may impact slide generation quality.")
        return {"style_review": {**review, "verified": False}}

    return {"style_protocol": style_data, "style_review": {**review, "verified": False}}

def check_style_protocol_node(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] 风格自查 (StyleCritic),对比风格描述与原图,决定是否需要修正"""
    logger.info("--- NODE: CheckStyleProtocol ---")
    config = config["configurable"]
    review = state.get("style_review", {})
    retry_count = review.get("retry_count", 0)

    if retry_count >= 2:
        logger.warning(f"   -> ⚠️ Style check retry limit ({retry_count}) reached. Forcing approval to avoid infinite loop.")
        return {"style_review": {"verified": True, "retry_count": retry_count, "critique": "Exceeded retry limit, auto-approved."}}

    verified, critique = critique_style_protocol(
        style_protocol=state["style_protocol"],
        output_dir=config["output_dir"],
        image_path=config["style_image_path"],
        llm_config=_get_llm_config(config, stage="vision"),
    )

    if verified:
        logger.info(f"   -> ✅ Style protocol APPROVED.")
    else:
        logger.warning(f"   -> ❌ Style protocol REJECTED. Critique: {critique[:20]}...")

    return {"style_review": {"verified": verified, "critique": critique, "retry_count": retry_count + 1}}

# ==============================================================================
# Phase 2: 规划与交互 (Planning & HITL 1)
# ==============================================================================
def generate_presentation_plan_node(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] 根据解析后的 PDF 内容,生成演示大纲"""
    logger.info("--- NODE: GeneratePresentationPlan ---")
    config = config["configurable"]
    review = state.get("plan_review", {})

    paper_main_content, presentation_plan = plan_presentation(
        previous_main_content=state.get("main_content"),
        previous_plan=state.get("presentation_plan"),
        user_feedback_plan=review.get("critique"),
        presentation_plan_verified=review.get("verified", False),
        content=state["content"],
        presentation_plan_retry_count=review.get("retry_count", 0),
        output_dir=config["output_dir"],
        llm_config=_get_llm_config(config, stage="text"),
    )

    if not presentation_plan:
        logger.error("❌ Fatal: Presentation plan generation failed.")
        raise ValueError("Fatal: Presentation plan generation failed.")

    return {
        "main_content": paper_main_content,
        "presentation_plan": presentation_plan,
        "plan_review": {**review, "verified": False},
    }

def review_plan_node(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] HITL 1: Plan Review - 使用 interrupt() 暂停图执行，等待用户反馈"""
    logger.info("--- NODE: ReviewPlan (HITL) ---")
    configurable = config["configurable"]
    review = state.get("plan_review", {})
    retry_count = review.get("retry_count", 0)

    # 如果设置了跳过标志，自动批准
    if configurable.get("skip_plan_review"):
        logger.info("   -> Auto-approved (--skip_plan_review).")
        return {"plan_review": {"verified": True, "critique": None, "retry_count": retry_count}}

    # interrupt() 暂停整个图（包括并行路径），控制权交还给外层 run_workflow
    user_input = interrupt({
        "type": "plan_review",
        "prompt": "Enter feedback to revise the plan, or press Enter to approve:",
    })

    user_input = (user_input or "").strip()

    if user_input:
        logger.info(f"   -> User provided feedback for plan revision.")
        return {"plan_review": {"verified": False, "critique": user_input, "retry_count": retry_count + 1}}
    else:
        logger.info(f"   -> User approved the plan.")
        return {"plan_review": {"verified": True, "critique": None, "retry_count": retry_count}}

# ==============================================================================
# Phase 3: 执行 (Execution - Single Slide Generation)
# ==============================================================================

def expand_slide_plan_node(state: SlideState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] 将简要大纲扩展为详细的单页描述"""
    config = config["configurable"]
    slide_page = state["slide_page"]
    logger.info(f"--- SUBGRAPH NODE (Slide {slide_page}): ExpandSlidePlan ---")

    slide_detail = expand_slide_plan(
        slide_plan=state["slide_plan"],
        style_protocol=state["slide_style_protocol"],
        llm_config=_get_llm_config(config, stage="text"),
    )

    if not slide_detail:
        logger.warning(f"⚠️ [Slide {slide_page}] Slide plan expansion failed. SVG generator will use the original plan.")

    return {"slide_detail": slide_detail}


def generate_slide_svg_node(state: SlideState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] 调用 LLM 生成单张 slide 的 SVG 源码"""
    config = config["configurable"]
    slide_page = state["slide_page"]
    logger.info(f"--- SUBGRAPH NODE (Slide {slide_page}): GenerateSlideSVG ---")

    svg_review = state.get("svg_review", {})
    design_review = state.get("design_review", {})

    svg_code = generate_slide_svg(
        slide_plan=state["slide_plan"],
        style_protocol=state["slide_style_protocol"],
        llm_config=_get_llm_config(config, stage="svg"),
        total_pages=state.get("total_pages", 10),
        slide_detail=state.get("slide_detail"),
        failed_svg=state.get("svg_code"),
        error_context=state.get("error_log"),
        svg_verified=svg_review.get("verified"),
        design_critique=design_review.get("critique"),
    )

    if not svg_code:
        logger.error(f"❌ [Slide {slide_page}] SVG generation failed.")
        return {"svg_code": None, "error_log": "SVG generation returned empty result"}

    logger.info(f"   -> SVG generated for slide {slide_page} ({len(svg_code)} chars)")
    # 注意：不要在这里重置 svg_review.retry_count。
    # 验证重试路径需要 retry_count 累计，否则 route_svg_crap_check 永远到不了
    # 上限阈值，会造成死循环（直到撞 recursion_limit）。
    # design 重试路径下 svg_review 已经是 verified=True / retry_count=0，无需重置。
    return {
        "svg_code": svg_code,
        "error_log": None,
    }

def optimize_svg_crap_node(state: SlideState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] 验证 SVG → CRAP 优化 → 后处理 → 写入文件"""
    config = config["configurable"]
    slide_page = state["slide_page"]
    logger.info(f"--- SUBGRAPH NODE (Slide {slide_page}): OptimizeSVGCRAP ---")

    svg_code = state.get("svg_code")
    if not svg_code:
        logger.error(f"❌ [Slide {slide_page}] No SVG code available.")
        return {
            "svg_review": {"verified": False, "retry_count": 0, "critique": "No SVG code available"},
            "error_log": "No SVG code available",
        }

    # 1. 基础验证（XML 合法性 + 禁用特性）
    from pipeline.svg_validator import validate_svg, finalize_single_svg

    is_valid, error = validate_svg(svg_code)
    svg_review = state.get("svg_review", {})
    retry_count = svg_review.get("retry_count", 0)

    if not is_valid:
        logger.warning(f"   -> ❌ [Slide {slide_page}] SVG validation failed (Attempt {retry_count + 1}): {error}")
        return {
            "svg_review": {"verified": False, "retry_count": retry_count + 1, "critique": error},
            "error_log": error,
        }

    # 2. CRAP 优化
    optimized_svg = optimize_svg_crap(
        svg_code=svg_code,
        llm_config=_get_llm_config(config, stage="svg"),
    )

    final_svg = svg_code
    if optimized_svg:
        # 验证优化后的 SVG
        opt_valid, opt_error = validate_svg(optimized_svg)
        if opt_valid:
            final_svg = optimized_svg
            logger.info(f"   -> [Slide {slide_page}] CRAP optimization applied.")
        else:
            logger.warning(f"   -> [Slide {slide_page}] CRAP-optimized SVG failed validation: {opt_error}. Keeping original.")
    else:
        logger.info(f"   -> [Slide {slide_page}] CRAP optimization returned no result. Keeping original.")

    # 3. 写入文件 + 后处理
    slide_dir = os.path.join(config["output_dir"], "result", f"slide_{slide_page:02d}")
    os.makedirs(slide_dir, exist_ok=True)
    svg_path = os.path.join(slide_dir, f"slide_v{retry_count}.svg")

    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(final_svg)

    success, finalize_error = finalize_single_svg(svg_path)
    if not success:
        logger.warning(f"   -> [Slide {slide_page}] Finalize failed: {finalize_error}")
        return {
            "svg_review": {"verified": False, "retry_count": retry_count + 1, "critique": finalize_error},
            "error_log": finalize_error,
        }

    logger.info(f"   -> ✅ [Slide {slide_page}] SVG optimized and finalized: {svg_path}")
    return {
        "svg_review": {"verified": True, "retry_count": retry_count, "critique": None},
        "svg_code": final_svg,
        "svg_path": svg_path,
        "error_log": None,
        "generated_slide_paths": [svg_path],
    }


def check_slide_design_node(state: SlideState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] 检查单张 slide 的视觉质量"""
    config = config["configurable"]
    slide_page = state["slide_page"]
    logger.info(f"--- SUBGRAPH NODE (Slide {slide_page}): CheckSlideDesign ---")

    critique_feedback = evaluate_and_critique_slide(
        slide_code=state["svg_code"],
        svg_path=state.get("svg_path"),
        slide_style_protocol=state["slide_style_protocol"],
        llm_config=_get_llm_config(config, stage="vision"),
    )

    design_review = state.get("design_review", {})
    retry_count = design_review.get("retry_count", 0)

    if critique_feedback is None:
        logger.info(f"   -> ✅ [Success] Slide {slide_page:02d} passed visual critique.")
        logger.info(f"✅ SUBGRAPH NODE (Slide {slide_page}): CheckSlideDesign completed.")
        return {
            "design_review": {"verified": True, "retry_count": retry_count, "critique": None},
        }
    else:
        logger.warning(f"   -> ⚠️ Visual critique suggested revisions for slide {slide_page} (Attempt {retry_count + 1}).")
        logger.info(f"✅ SUBGRAPH NODE (Slide {slide_page}): CheckSlideDesign completed (with revisions needed).")
        return {
            "design_review": {"verified": False, "retry_count": retry_count + 1, "critique": critique_feedback},
        }

# ==============================================================================
# Phase 4: 交付与修缮 (Delivery & Refinement)
# ==============================================================================

def merge_slides_to_deck_node(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] 合并所有成功生成的单页 PPTX 文件"""
    config = config["configurable"]
    logger.info("--- NODE: MergeSlidesToDeck ---")

    raw_paths = state.get("generated_slide_paths", [])

    # 去重：generated_slide_paths 是 operator.add 累加器，HITL 2 局部重生成
    # 时旧条目会残留。按 slide 目录名（slide_03 等）作为 key，后写入的路径覆盖
    # 先前的，从而只保留每张 slide 的最新版本。
    by_page: Dict[str, str] = {}
    for p in raw_paths:
        key = os.path.basename(os.path.dirname(p))  # e.g. "slide_03"
        by_page[key] = p
    svg_paths = sorted(by_page.values())

    if len(raw_paths) != len(svg_paths):
        logger.info(
            f"   -> Deduplicated generated_slide_paths: "
            f"{len(raw_paths)} entries -> {len(svg_paths)} unique slides."
        )

    # 缺页检测：对比计划页数与实际产出数，让静默失败的 slide 显形。
    plan = state.get("presentation_plan") or []
    if plan:
        expected_pages = {int(s.get("slide_page")) for s in plan if s.get("slide_page") is not None}
        produced_pages = set()
        for key in by_page.keys():
            # key like "slide_03" -> 3
            try:
                produced_pages.add(int(key.split("_")[-1]))
            except ValueError:
                continue
        missing = sorted(expected_pages - produced_pages)
        if missing:
            logger.error(
                f"   -> ❌ Missing slides in final deck (SVG validation or generation failed): {missing}. "
                f"These pages were silently dropped by the subgraph."
            )

    if not svg_paths:
        logger.warning("   -> No SVG slides were generated to merge.")
        return {"final_pptx_path": None}

    final_path = os.path.join(config["output_dir"], "result", "Final_Presentation.pptx")
    result = merge_svgs_to_pptx(svg_paths, final_path)

    if result:
        logger.info(f"   -> ✅ Merged {len(svg_paths)} SVG(s) into {final_path}")
        return {"final_pptx_path": final_path}
    else:
        logger.error("   -> ❌ SVG to PPTX merge failed.")
        return {"final_pptx_path": None}

def review_pptx_design_node(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] HITL 2: Final Inspection - 使用 interrupt() 暂停图执行，等待用户反馈"""
    logger.info("--- NODE: ReviewPPTXDesign (HITL) ---")
    configurable = config["configurable"]

    pptx_path = state.get("final_pptx_path")
    slides_plan = state.get("presentation_plan")

    review = state.get("pptx_review", {})
    retry_count = review.get("retry_count", 0)

    if not pptx_path or not os.path.exists(pptx_path):
        logger.warning("   -> Final PPTX file not found. Skipping user review.")
        return {"pptx_review": {"verified": True, "retry_count": retry_count, "critique": None}}

    # 如果设置了跳过标志，自动批准
    if configurable.get("skip_pptx_review"):
        logger.info(f"   -> Auto-approved (--skip_pptx_review). PPTX at: {pptx_path}")
        return {"pptx_review": {"verified": True, "retry_count": retry_count, "critique": None}}

    # interrupt() 暂停整个图，控制权交还给外层 run_workflow
    user_input = interrupt({
        "type": "pptx_review",
        "prompt": "Enter feedback for refinements, or press Enter to accept:",
        "pptx_path": pptx_path,
    })

    user_input = (user_input or "").strip()

    if not user_input:
        logger.info("   -> ✅ User accepted the final presentation. Workflow will now complete.")
        return {"pptx_review": {"verified": True, "retry_count": retry_count, "critique": None}}

    logger.info("   -> User provided feedback for final revision. Analyzing feedback...")
    analysis_result = analyze_feedback(
        user_input=user_input,
        slide_count=len(slides_plan or []),
        llm_config=_get_llm_config(configurable, stage="text"),
    )

    logger.info(f"   -> Feedback analysis result: Scope='{analysis_result.scope}', Target Pages={analysis_result.target_pages}")

    if analysis_result.scope == "ambiguous":
        logger.warning("   -> Feedback is ambiguous. Prompting user to provide more specific instructions.")
        return {"pptx_review": {"verified": True, "retry_count": retry_count, "critique": "ambiguous"}}

    return {
        "pptx_review": {"verified": False, "retry_count": retry_count + 1, "critique": analysis_result.scope},
        "retry_slide_pages": analysis_result.target_pages,
    }