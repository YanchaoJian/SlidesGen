import logging
from typing import Literal

from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from langgraph.checkpoint.base import BaseCheckpointSaver

from workflow.state import OverallState, SlideState, initialize_slide_state
from workflow.nodes import (
    extract_content_from_pdf_node,
    analyze_image_style_node,
    check_style_protocol_node,
    generate_presentation_plan_node,
    merge_slides_to_deck_node,
    review_pptx_design_node,
    review_plan_node,
    expand_slide_plan_node,
    generate_slide_svg_node,
    optimize_svg_crap_node,
    check_slide_design_node,
)


logger = logging.getLogger(__name__)

# ==============================================================================
# 1. 路由逻辑 (Conditional Edges Logic)
# ==============================================================================

def route_style_protocol_check(state: OverallState) -> Literal["analyze_image_style", "dispatch_slide_tasks"]:
    """路由：风格协议自查"""
    if state.get("style_review", {}).get("verified"):
        logger.info("🔀 Style protocol verified. Proceeding to dispatch slide tasks.")
        return "dispatch_slide_tasks"
    logger.info("🔀 Style protocol not verified. Routing to style analysis.")
    return "analyze_image_style"

def route_presentation_plan_review(state: OverallState) -> Literal["generate_presentation_plan", "dispatch_slide_tasks"]:
    """路由：大纲审查"""
    if state.get("plan_review", {}).get("verified"):
        logger.info("🔀 Presentation plan approved. Proceeding to dispatch slide tasks.")
        return "dispatch_slide_tasks"
    logger.info("🔀 Routing: Presentation plan requires revisions. Returning to planning...")
    return "generate_presentation_plan"

def route_pptx_design_review(state: OverallState) -> Literal["analyze_image_style", "generate_presentation_plan", "dispatch_slide_tasks", "review_pptx_design", "END"]:
    """路由：根据用户反馈的范围决定下一步。"""
    pptx_review = state.get("pptx_review", {})
    if pptx_review.get("verified"):
        logger.info("🔀 PPTX design approved. Workflow will complete.")
        return "END"

    scope = state.get("pptx_feedback_scope")

    if scope == "global_style":
        logger.info("🎨 Rerouting to Style Analysis for global style changes.")
        return "analyze_image_style"
    elif scope == "global_plan":
        logger.info("📝 Rerouting to Plan Presentation for global plan changes.")
        return "generate_presentation_plan"
    elif scope == "local":
        logger.info("🔧 Rerouting to Dispatcher for local slide regeneration.")
        return "dispatch_slide_tasks"
    elif scope == "ambiguous":
        logger.info("🤔 User feedback was ambiguous. Re-prompting for clearer instructions.")
        return "review_pptx_design"
    else:
        logger.info("🤔 No actionable feedback scope. Ending review cycle.")
        return "END"

def route_svg_crap_check(state: SlideState, config: RunnableConfig):
    """路由：SVG 验证 + CRAP 优化检查"""
    slide_page = state.get('slide_page')
    svg_review = state.get("svg_review", {})
    if svg_review.get("verified"):
        logger.info(f"🔀 [Slide {slide_page}] SVG optimized successfully. Proceeding to design check.")
        return "check_slide_design"

    max_retries = int((config.get("configurable") or {}).get("llm_max_retries", 3))
    retry_count = svg_review.get("retry_count", 0)
    if retry_count >= max_retries:
        logger.warning(f"⚠️ [Slide {slide_page}] SVG failed after {retry_count}/{max_retries} retries. Aborting this slide.")
        return END

    logger.info(f"🔀 [Slide {slide_page}] SVG validation failed. Routing back to SVG generation (Attempt {retry_count + 1}/{max_retries}).")
    return "generate_slide_svg"

def route_slide_design_check(state: SlideState, config: RunnableConfig):
    """路由：设计质量检查"""
    slide_page = state.get('slide_page')
    design_review = state.get("design_review", {})
    if design_review.get("verified"):
        logger.info(f"🔀 [Slide {slide_page}] Design verified. Completing slide subgraph.")
        return END

    max_retries = int((config.get("configurable") or {}).get("llm_max_retries", 3))
    retry_count = design_review.get("retry_count", 0)
    if retry_count >= max_retries:
        logger.warning(f"⚠️ [Slide {slide_page}] Design check failed after {retry_count} retries (limit={max_retries}). Accepting the last generated version to ensure output.")
        return END

    logger.info(f"🔀 [Slide {slide_page}] Design not verified. Routing to SVG generation for refinements (Attempt {retry_count + 1}/{max_retries}).")
    return "generate_slide_svg"
# ==============================================================================
# 2. Map-Reduce 逻辑
# ==============================================================================

def map_slides_to_tasks(state: OverallState):
    """分发器：将大纲拆解为并行的 generate_single_slide 任务"""
    logger.info("🗺️ Mapping slides to parallel generation tasks...")
    slides_plan = state.get("presentation_plan")
    
    if not slides_plan:
        logger.warning("  - No slides found in the plan. Nothing to dispatch.")
        return []

    target_pages = state.get("retry_slide_pages")

    # None → 全量生成；非空列表 → 局部重生成；空列表 → 无有效目标，跳过
    if target_pages is not None and len(target_pages) == 0:
        logger.warning("  - target_pages is an empty list. No slides to regenerate.")
        return []

    tasks = []
    for slide_plan in slides_plan:
        slide_page = slide_plan.get("slide_page")

        if target_pages is not None and slide_page not in target_pages:
            continue
        
        task_input: SlideState = initialize_slide_state(
            slide_page=slide_page,
            slide_plan=slide_plan,
            slide_style_protocol=state["style_protocol"],
            total_pages=len(slides_plan),
        )
        tasks.append(Send("generate_single_slide", task_input))
    
    logger.info(f"  - Dispatching {len(tasks)} tasks.")
    return tasks

# ==============================================================================
# 3. 图构建函数 (Graph Builder)
# ==============================================================================
def build_slide_subgraph():
    """构建单个 slide 的生成子图（SVG 管线）"""
    slide_subgraph = StateGraph(SlideState)

    # 子图节点
    slide_subgraph.add_node("expand_slide_plan", expand_slide_plan_node)
    slide_subgraph.add_node("generate_slide_svg", generate_slide_svg_node)
    slide_subgraph.add_node("optimize_svg_crap", optimize_svg_crap_node)
    slide_subgraph.add_node("check_slide_design", check_slide_design_node)

    # 子图流程: START → expand_slide_plan → generate_slide_svg → optimize_svg_crap → (route)
    slide_subgraph.add_edge(START, "expand_slide_plan")
    slide_subgraph.add_edge("expand_slide_plan", "generate_slide_svg")
    slide_subgraph.add_edge("generate_slide_svg", "optimize_svg_crap")

    # CRAP 优化节点内含验证：成功 → 设计检查；失败 → 重试生成
    slide_subgraph.add_conditional_edges("optimize_svg_crap", route_svg_crap_check, {
            "check_slide_design": "check_slide_design",
            "generate_slide_svg": "generate_slide_svg",
            END: END,
        }
    )

    # 设计质量检查后的路由
    slide_subgraph.add_conditional_edges("check_slide_design", route_slide_design_check, {
            "generate_slide_svg": "generate_slide_svg",
            END: END,
        }
    )

    return slide_subgraph.compile()

def build_graph(checkpointer: BaseCheckpointSaver):
    """构建、定义和编译智能 PPT 生成工作流图"""
    workflow = StateGraph(OverallState)

    # --- 节点定义 ---
    workflow.add_node("extract_content_from_pdf", extract_content_from_pdf_node)

    workflow.add_node("analyze_image_style", analyze_image_style_node)
    workflow.add_node("check_style_protocol", check_style_protocol_node)

    workflow.add_node("generate_presentation_plan", generate_presentation_plan_node)
    workflow.add_node("review_plan", review_plan_node)

    # defer=True：确保 dispatch 等到两条前驱分支（check_style_protocol / review_plan）
    # 都收敛后再 fan-out 一次，避免 slide 子图被各分支触发两遍（token 成本×2）。
    workflow.add_node("dispatch_slide_tasks", lambda state: {}, defer=True)
    slide_subgraph = build_slide_subgraph() 
    workflow.add_node("generate_single_slide", slide_subgraph)
    workflow.add_node("merge_slides_to_deck", merge_slides_to_deck_node, defer=True)
    workflow.add_node("review_pptx_design", review_pptx_design_node)

    # --- 边与流程拓扑定义 ---
    workflow.add_edge(START, "extract_content_from_pdf")
    workflow.add_edge("extract_content_from_pdf", "generate_presentation_plan")
    workflow.add_edge("generate_presentation_plan", "review_plan")
    workflow.add_conditional_edges("review_plan", route_presentation_plan_review, {
        "generate_presentation_plan": "generate_presentation_plan",
        "dispatch_slide_tasks": "dispatch_slide_tasks",
    })

    workflow.add_edge(START, "analyze_image_style")
    workflow.add_edge("analyze_image_style", "check_style_protocol")
    workflow.add_conditional_edges("check_style_protocol", route_style_protocol_check, {
        "analyze_image_style": "analyze_image_style",
        "dispatch_slide_tasks": "dispatch_slide_tasks",
    })
    
    workflow.add_conditional_edges(
        "dispatch_slide_tasks",
        map_slides_to_tasks,
        {"generate_single_slide": "generate_single_slide"}
    )
    workflow.add_edge("generate_single_slide", "merge_slides_to_deck")
    workflow.add_edge("merge_slides_to_deck", "review_pptx_design")
    workflow.add_conditional_edges("review_pptx_design", route_pptx_design_review, {
        "analyze_image_style": "analyze_image_style",
        "generate_presentation_plan": "generate_presentation_plan",
        "dispatch_slide_tasks": "dispatch_slide_tasks",
        "review_pptx_design": "review_pptx_design",
        "END": END
    })

    # --- 编译图 ---
    return workflow.compile(checkpointer=checkpointer)