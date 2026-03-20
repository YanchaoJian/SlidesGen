import logging
from typing import Literal

from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from langgraph.checkpoint.base import BaseCheckpointSaver

from workflow.state import OverallState, SlideState, initialize_slide_state
from workflow.nodes import (
    enhance_content_node,
    extract_content_from_pdf_node,
    analyze_image_style_node,
    check_style_protocol_node,
    generate_presentation_plan_node,
    merge_slides_to_deck_node,
    review_pptx_design_node,
    review_plan_node,
    generate_code_directive_node, 
    generate_slide_code_node,
    check_code_execution_node,
    check_slide_design_node
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

def route_pptx_design_review(state: OverallState) -> Literal["analyze_image_style", "generate_presentation_plan", "dispatch_slide_tasks", "END"]:
    """路由：根据用户反馈的范围决定下一步。"""
    pptx_review = state.get("pptx_review", {})
    if pptx_review.get("verified"):
        logger.info("🔀 PPTX design approved. Workflow will complete.")
        return "END"

    scope = pptx_review.get("critique")

    if scope == "global_style":
        logger.info("🎨 Rerouting to Style Analysis for global style changes.")
        return "analyze_image_style"
    elif scope == "global_plan":
        logger.info("📝 Rerouting to Plan Presentation for global plan changes.")
        return "generate_presentation_plan"
    elif scope == "local":
        logger.info("🔧 Rerouting to Dispatcher for local slide regeneration.")
        return "dispatch_slide_tasks"
    else: # This now handles "ambiguous" or None
        logger.info("🤔 User feedback was ambiguous or empty. Ending review cycle.")
        return "END"

def route_code_execution_check(state: SlideState):
    """路由：代码执行检查"""
    slide_page = state.get('slide_page')
    code_review = state.get("code_review", {})
    if code_review.get("verified"):
        logger.info(f"🔀 [Slide {slide_page}] Code executed successfully. Proceeding to slide design check.")
        return "check_slide_design"

    retry_count = code_review.get("retry_count", 0)
    if retry_count >= 3:
        logger.warning(f"⚠️ [Slide {slide_page}] Code execution failed after {retry_count} retries. Aborting this slide.")
        return END

    logger.info(f"🔀 [Slide {slide_page}] Code execution failed. Routing back to code generation for fixes (Attempt {retry_count + 1}).")
    return "generate_slide_code"

def route_slide_design_check(state: SlideState):
    """路由：设计质量检查"""
    slide_page = state.get('slide_page')
    design_review = state.get("design_review", {})
    if design_review.get("verified"):
        logger.info(f"🔀 [Slide {slide_page}] Design verified. Completing slide subgraph.")
        return END

    retry_count = design_review.get("retry_count", 0)
    if retry_count >= 3:
        logger.warning(f"⚠️ [Slide {slide_page}] Design check failed after {retry_count} retries. Accepting the last generated version to ensure output.")
        return END

    logger.info(f"🔀 [Slide {slide_page}] Design not verified. Routing to code generation for refinements (Attempt {retry_count + 1}).")
    return "generate_slide_code"
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
    
    tasks = []
    for slide_plan in slides_plan:
        slide_page = slide_plan.get("slide_page")

        if target_pages and slide_page not in target_pages:
            continue
        
        task_input: SlideState = initialize_slide_state(
            slide_page=slide_page,
            slide_plan=slide_plan, 
            slide_style_protocol=state["style_protocol"]
        )
        tasks.append(Send("generate_single_slide", task_input))
    
    logger.info(f"  - Dispatching {len(tasks)} tasks.")
    return tasks

# ==============================================================================
# 3. 图构建函数 (Graph Builder)
# ==============================================================================
def build_slide_subgraph():
    """构建单个 slide 的生成子图"""
    slide_subgraph = StateGraph(SlideState)
    
    # 子图节点
    slide_subgraph.add_node("generate_code_directive", generate_code_directive_node)
    slide_subgraph.add_node("generate_slide_code", generate_slide_code_node)
    slide_subgraph.add_node("check_code_execution", check_code_execution_node)
    slide_subgraph.add_node("check_slide_design", check_slide_design_node) 

    # 子图流程
    slide_subgraph.add_edge(START, "generate_code_directive")
    slide_subgraph.add_edge("generate_code_directive", "generate_slide_code")
    slide_subgraph.add_edge("generate_slide_code", "check_code_execution")
    
    # 代码执行检查后的路由
    slide_subgraph.add_conditional_edges("check_code_execution", route_code_execution_check, {
            "check_slide_design": "check_slide_design",
            "generate_slide_code": "generate_slide_code",
            END: END
        }
    )
    
    # 设计质量检查后的路由
    slide_subgraph.add_conditional_edges("check_slide_design", route_slide_design_check, {
            "generate_slide_code": "generate_slide_code",
            END: END
        }
    )

    return slide_subgraph.compile()

def build_graph(checkpointer: BaseCheckpointSaver):
    """构建、定义和编译智能 PPT 生成工作流图"""
    workflow = StateGraph(OverallState)

    # --- 节点定义 ---
    workflow.add_node("extract_content_from_pdf", extract_content_from_pdf_node)
    workflow.add_node("enhance_content", enhance_content_node)

    workflow.add_node("analyze_image_style", analyze_image_style_node)
    workflow.add_node("check_style_protocol", check_style_protocol_node)

    workflow.add_node("generate_presentation_plan", generate_presentation_plan_node)
    workflow.add_node("review_plan", review_plan_node)

    workflow.add_node("dispatch_slide_tasks", lambda state: {})
    slide_subgraph = build_slide_subgraph() 
    workflow.add_node("generate_single_slide", slide_subgraph)
    workflow.add_node("merge_slides_to_deck", merge_slides_to_deck_node)
    workflow.add_node("review_pptx_design", review_pptx_design_node)

    # --- 边与流程拓扑定义 ---
    workflow.add_edge(START, "extract_content_from_pdf")
    workflow.add_edge("extract_content_from_pdf", "enhance_content")
    workflow.add_edge("enhance_content", "generate_presentation_plan")
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
        "END": END
    })

    # --- 编译图 ---
    return workflow.compile(checkpointer=checkpointer)