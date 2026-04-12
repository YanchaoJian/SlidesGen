import os
import logging
from typing import Any, Dict

from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt

from agents.perception.pdf_parser.extractor import extract_pdf

load_dotenv()


def _ablation(flag_name: str) -> bool:
    """读取 .env 中的消融开关，返回 True 表示该模块被禁用。"""
    return os.getenv(flag_name, "false").strip().lower() in ("true", "1", "yes")
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
from utils.instrumentation import time_node

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
        max_retries=int(configurable.get("llm_max_retries", 3)),
        stage=stage,
    )


# ==============================================================================
# Phase 1: 感知与反思 (Perception & Reflection)
# ==============================================================================

@time_node("extract_pdf")
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


@time_node("analyze_image_style")
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

@time_node("check_style_protocol")
def check_style_protocol_node(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] 风格自查 (StyleCritic),对比风格描述与原图,决定是否需要修正"""
    logger.info("--- NODE: CheckStyleProtocol ---")
    config = config["configurable"]
    review = state.get("style_review", {})
    retry_count = review.get("retry_count", 0)
    max_retries = int(config.get("llm_max_retries", 3))

    if retry_count >= max_retries:
        logger.warning(f"   -> ⚠️ Style check retry limit ({retry_count}/{max_retries}) reached. Forcing approval to avoid infinite loop.")
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
@time_node("generate_presentation_plan")
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

@time_node("review_plan")
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

@time_node("expand_slide_plan")
def expand_slide_plan_node(state: SlideState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] 将简要大纲扩展为详细的单页描述"""
    config = config["configurable"]
    slide_page = state["slide_page"]
    logger.info(f"--- SUBGRAPH NODE (Slide {slide_page}): ExpandSlidePlan ---")

    if _ablation("ABLATION_NO_SLIDE_EXPAND"):
        logger.info(f"   -> [Slide {slide_page}] Ablation: slide expansion disabled, using original plan.")
        return {"slide_detail": None}

    slide_detail = expand_slide_plan(
        slide_plan=state["slide_plan"],
        style_protocol=state["slide_style_protocol"],
        llm_config=_get_llm_config(config, stage="text"),
    )

    if not slide_detail:
        logger.warning(f"⚠️ [Slide {slide_page}] Slide plan expansion failed. SVG generator will use the original plan.")
    else:
        slide_dir = os.path.join(config["output_dir"], "result", f"slide_{slide_page:02d}")
        os.makedirs(slide_dir, exist_ok=True)
        detail_path = os.path.join(slide_dir, "slide_detail.md")
        try:
            with open(detail_path, "w", encoding="utf-8") as f:
                f.write(slide_detail)
            logger.info(f"   -> [Slide {slide_page}] Slide detail saved to {detail_path}")
        except Exception as e:
            logger.warning(f"   -> [Slide {slide_page}] Failed to save slide detail: {e}")

    return {"slide_detail": slide_detail}


@time_node("generate_slide_svg")
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
        # SVG 生成失败（LLM 调用异常 / 返回空 / 提取失败）。
        # 必须累加 svg_review.retry_count，否则下游 optimize_svg_crap_node 的
        # "No SVG code" 分支会一直返回 retry_count=0，导致 route_svg_crap_check
        # 永远走重试分支，形成死循环。
        prev_retry = svg_review.get("retry_count", 0)
        logger.error(f"❌ [Slide {slide_page}] SVG generation failed (Attempt {prev_retry + 1}).")
        return {
            "svg_code": None,
            "error_log": "SVG generation returned empty result",
            "svg_review": {
                "verified": False,
                "retry_count": prev_retry + 1,
                "critique": "SVG generation returned empty result",
            },
        }

    logger.info(f"   -> SVG generated for slide {slide_page} ({len(svg_code)} chars)")
    # 注意：不要在这里重置 svg_review.retry_count。
    # 验证重试路径需要 retry_count 累计，否则 route_svg_crap_check 永远到不了
    # 上限阈值，会造成死循环（直到撞 recursion_limit）。
    # design 重试路径下 svg_review 已经是 verified=True / retry_count=0，无需重置。
    return {
        "svg_code": svg_code,
        "error_log": None,
    }

@time_node("optimize_svg_crap")
def optimize_svg_crap_node(state: SlideState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] 验证 SVG → CRAP 优化 → 后处理 → 写入文件"""
    config = config["configurable"]
    slide_page = state["slide_page"]
    logger.info(f"--- SUBGRAPH NODE (Slide {slide_page}): OptimizeSVGCRAP ---")

    svg_code = state.get("svg_code")
    if not svg_code:
        # 上游 generate_slide_svg_node 已累加过 retry_count；这里只需透传，
        # 绝不能重置为 0（否则与上游配合形成死循环）。
        prev_retry = state.get("svg_review", {}).get("retry_count", 0)
        logger.error(f"❌ [Slide {slide_page}] No SVG code available (retry_count={prev_retry}).")
        return {
            "svg_review": {
                "verified": False,
                "retry_count": prev_retry,
                "critique": "No SVG code available",
            },
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
    final_svg = svg_code
    if _ablation("ABLATION_NO_CRAP"):
        logger.info(f"   -> [Slide {slide_page}] Ablation: CRAP optimization disabled, keeping validated SVG.")
    else:
        optimized_svg = optimize_svg_crap(
            svg_code=svg_code,
            llm_config=_get_llm_config(config, stage="svg"),
        )

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
    # 版本号按目录中已存在的 slide_v*.svg 数量单调递增，避免 design_review
    # 重试时（svg_review.retry_count 不变）覆盖之前的版本，从而保留完整历史。
    import glob
    existing_versions = glob.glob(os.path.join(slide_dir, "slide_v*.svg"))
    version = len(existing_versions)
    # 用 posix 风格统一斜杠，避免快照里出现 "output/xx\\result\\..." 这种混合路径。
    svg_path = os.path.join(slide_dir, f"slide_v{version}.svg").replace(os.sep, "/")

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
        "generated_slide_paths": {slide_page: svg_path},
    }


@time_node("check_slide_design")
def check_slide_design_node(state: SlideState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] 检查单张 slide 的视觉质量"""
    config = config["configurable"]
    slide_page = state["slide_page"]
    logger.info(f"--- SUBGRAPH NODE (Slide {slide_page}): CheckSlideDesign ---")

    if _ablation("ABLATION_NO_SVG_SELFHEAL"):
        logger.info(f"   -> [Slide {slide_page}] Ablation: visual self-heal disabled, auto-approving.")
        svg_review = state.get("svg_review", {})
        auto_design_review = {"verified": True, "retry_count": 0, "critique": None}
        return {
            "design_review": auto_design_review,
            "slide_reports": {
                slide_page: {
                    "slide_page": slide_page,
                    "svg_review": svg_review,
                    "design_review": auto_design_review,
                    "slide_detail": state.get("slide_detail"),
                    "svg_path": state.get("svg_path"),
                    "error_log": state.get("error_log"),
                }
            },
        }

    critique_feedback = evaluate_and_critique_slide(
        slide_code=state["svg_code"],
        svg_path=state.get("svg_path"),
        slide_style_protocol=state["slide_style_protocol"],
        llm_config=_get_llm_config(config, stage="vision"),
    )

    design_review = state.get("design_review", {})
    retry_count = design_review.get("retry_count", 0)

    svg_review = state.get("svg_review", {})

    if critique_feedback is None:
        logger.info(f"   -> ✅ [Success] Slide {slide_page:02d} passed visual critique.")
        logger.info(f"✅ SUBGRAPH NODE (Slide {slide_page}): CheckSlideDesign completed.")
        final_design_review = {"verified": True, "retry_count": retry_count, "critique": None}
        return {
            "design_review": final_design_review,
            # 子图终态冒泡到主图，供 final_snapshot.json / 实验后处理使用
            "slide_reports": {
                slide_page: {
                    "slide_page": slide_page,
                    "svg_review": svg_review,
                    "design_review": final_design_review,
                    "slide_detail": state.get("slide_detail"),
                    "svg_path": state.get("svg_path"),
                    "error_log": state.get("error_log"),
                }
            },
        }
    else:
        logger.warning(f"   -> ⚠️ Visual critique suggested revisions for slide {slide_page} (Attempt {retry_count + 1}).")
        logger.info(f"✅ SUBGRAPH NODE (Slide {slide_page}): CheckSlideDesign completed (with revisions needed).")
        failing_design_review = {"verified": False, "retry_count": retry_count + 1, "critique": critique_feedback}
        return {
            "design_review": failing_design_review,
            # 即便未通过也写一份报告；若后续重试成功，reducer 会用最新版本覆盖。
            "slide_reports": {
                slide_page: {
                    "slide_page": slide_page,
                    "svg_review": svg_review,
                    "design_review": failing_design_review,
                    "slide_detail": state.get("slide_detail"),
                    "svg_path": state.get("svg_path"),
                    "error_log": state.get("error_log"),
                }
            },
        }

# ==============================================================================
# Phase 4: 交付与修缮 (Delivery & Refinement)
# ==============================================================================

@time_node("merge_slides")
def merge_slides_to_deck_node(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] 合并所有成功生成的单页 PPTX 文件"""
    config = config["configurable"]
    logger.info("--- NODE: MergeSlidesToDeck ---")

    # generated_slide_paths 现在是 {slide_page: path}，由自定义 reducer 合并；
    # 局部重生成 / 恢复执行的最新版本会自动覆盖旧条目。
    paths_by_page: Dict[int, str] = state.get("generated_slide_paths") or {}
    svg_paths = [paths_by_page[k] for k in sorted(paths_by_page.keys())]

    # 缺页检测：对比计划页数与实际产出数，让静默失败的 slide 显形。
    plan = state.get("presentation_plan") or []
    if plan:
        expected_pages = {int(s.get("slide_page")) for s in plan if s.get("slide_page") is not None}
        produced_pages = set(paths_by_page.keys())
        missing = sorted(expected_pages - produced_pages)
        if missing:
            logger.error(
                f"   -> ❌ Missing slides in final deck (SVG validation or generation failed): {missing}. "
                f"These pages were silently dropped by the subgraph."
            )

    if not svg_paths:
        logger.warning("   -> No SVG slides were generated to merge.")
        return {"final_pptx_path": None}

    # 从 presentation_plan 中提取每页的演讲者备注，构建 {svg_stem: notes_text} 映射。
    # SVG 文件名格式为 slide_v{version}.svg，stem 为 slide_v{version}；
    # 按 slide_page 将 notes 关联到对应 SVG 的最新版本。
    notes_dict: Dict[str, str] = {}
    if plan:
        notes_by_page: Dict[int, str] = {}
        for slide_plan in plan:
            page = slide_plan.get("slide_page")
            pnotes = slide_plan.get("presenter_notes", "")
            if page is not None and pnotes:
                notes_by_page[int(page)] = pnotes

        for page_num in sorted(paths_by_page.keys()):
            svg_file = paths_by_page[page_num]
            stem = os.path.splitext(os.path.basename(svg_file))[0]
            if page_num in notes_by_page:
                notes_dict[stem] = notes_by_page[page_num]

    if notes_dict:
        logger.info(f"   -> Speaker notes prepared for {len(notes_dict)} slide(s).")

    final_path = os.path.join(config["output_dir"], "result", "Final_Presentation.pptx").replace(os.sep, "/")
    result = merge_svgs_to_pptx(svg_paths, final_path, style_protocol=state.get("style_protocol"), notes=notes_dict)

    if result:
        logger.info(f"   -> ✅ Merged {len(svg_paths)} SVG(s) into {final_path}")
        return {"final_pptx_path": final_path}
    else:
        logger.error("   -> ❌ SVG to PPTX merge failed.")
        return {"final_pptx_path": None}

@time_node("review_pptx_design")
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
        return {
            "pptx_review": {"verified": True, "retry_count": retry_count, "critique": None},
            "pptx_feedback_scope": None,
        }

    # 如果设置了跳过标志，自动批准
    if configurable.get("skip_pptx_review"):
        logger.info(f"   -> Auto-approved (--skip_pptx_review). PPTX at: {pptx_path}")
        return {
            "pptx_review": {"verified": True, "retry_count": retry_count, "critique": None},
            "pptx_feedback_scope": None,
        }

    # interrupt() 暂停整个图，控制权交还给外层 run_workflow
    user_input = interrupt({
        "type": "pptx_review",
        "prompt": "Enter feedback for refinements, or press Enter to accept:",
        "pptx_path": pptx_path,
    })

    user_input = (user_input or "").strip()

    if not user_input:
        logger.info("   -> ✅ User accepted the final presentation. Workflow will now complete.")
        return {
            "pptx_review": {"verified": True, "retry_count": retry_count, "critique": None},
            "pptx_feedback_scope": None,
        }

    logger.info("   -> User provided feedback for final revision. Analyzing feedback...")
    analysis_result = analyze_feedback(
        user_input=user_input,
        slide_count=len(slides_plan or []),
        llm_config=_get_llm_config(configurable, stage="text"),
    )

    logger.info(f"   -> Feedback analysis result: Scope='{analysis_result.scope}', Target Pages={analysis_result.target_pages}")

    if analysis_result.scope == "ambiguous":
        # 反馈无法解析：保持 verified=False 让路由把控制权交回本节点重新询问，
        # 不再伪装成审批通过而静默吞掉用户输入。
        logger.warning("   -> Feedback is ambiguous. Will re-prompt user for more specific instructions.")
        return {
            "pptx_review": {"verified": False, "retry_count": retry_count, "critique": user_input},
            "pptx_feedback_scope": "ambiguous",
            "retry_slide_pages": None,
        }

    return {
        "pptx_review": {"verified": False, "retry_count": retry_count + 1, "critique": user_input},
        "pptx_feedback_scope": analysis_result.scope,
        "retry_slide_pages": analysis_result.target_pages,
    }