import os
import logging
from typing import Any, Dict

from langchain_core.runnables import RunnableConfig

from workflow.feedback_router import analyze_feedback_with_llm
from agent.parser.pdf_extractor import extract_content
from agent.parser.content_enhancer import enhance_content_with_llm
from agent.designer.style_analyzer import analyze_style
from agent.designer.style_critic import review_visual_protocol
from agent.planner.slides_planner import generate_presentation_plan
from agent.composer.layout_engine import generate_layout_directive
from agent.composer.code_generator import generate_slide_code
from agent.composer.pptx_renderer import merge_deck, run_script
from agent.evaluator.visual_critic import evaluate_and_critique_slide
from utils.llm_helpers import LLMConfig
from workflow.state import OverallState, SlideState

logger = logging.getLogger(__name__)


def _get_llm_config(configurable: Dict[str, Any]) -> LLMConfig:
    """从 configurable 字典中提取 LLM 连接配置。"""
    return LLMConfig(
        model_name=configurable["model_name"],
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
    
    base_content, _, _ = extract_content(
        pdf_path=config["pdf_path"], 
        marker_path=config["marker_path"],
        output_dir=config["output_dir"]
    )
    
    if not base_content:
        logger.error("❌ Fatal: PDF content extraction with Marker failed.")
        raise ValueError("Fatal: PDF content extraction with Marker failed.")
        
    return {"content": base_content}

def enhance_content_node(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] 内容增强（表格和公式已由 Marker 直接提取，此步骤可跳过）"""
    logger.info("--- NODE: EnhanceContent ---")
    config = config["configurable"]

    content = state["content"]
    has_tables = bool(content.get("tables"))
    has_equations = bool(content.get("equations"))

    if has_tables or has_equations:
        logger.info(f"   -> Marker already extracted {len(content.get('tables', []))} tables "
                    f"and {len(content.get('equations', []))} equations. Skipping LLM enhancement.")
        return {}

    # 仅当 Marker 未提取到表格/公式且配置了增强时，才使用 LLM 补充
    if config.get("enhance_marker"):
        logger.info("   -> No tables/equations from Marker, falling back to LLM enhancement...")
        enhanced_content = enhance_content_with_llm(
            base_content=content,
            output_dir=config["output_dir"],
            llm_config=_get_llm_config(config),
        )
        return {"content": enhanced_content}
    else:
        logger.info("   -> Skipping LLM enhancement step as per configuration.")
        return {}

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
        llm_config=_get_llm_config(config),
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

    verified, critique = review_visual_protocol(
        style_protocol=state["style_protocol"],
        output_dir=config["output_dir"],
        image_path=config["style_image_path"],
        llm_config=_get_llm_config(config),
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

    paper_main_content, presentation_plan = generate_presentation_plan(
        previous_main_content=state.get("main_content"),
        previous_plan=state.get("presentation_plan"),
        user_feedback_plan=review.get("critique"),
        presentation_plan_verified=review.get("verified", False),
        content=state["content"],
        presentation_plan_retry_count=review.get("retry_count", 0),
        output_dir=config["output_dir"],
        llm_config=_get_llm_config(config),
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
    """[Node] HITL 1: Plan Review - 集成人工交互逻辑"""
    logger.info("--- NODE: ReviewPlan (HITL) ---")
    review = state.get("plan_review", {})
    retry_count = review.get("retry_count", 0)

    logger.info("🛑 HITL [1/2]: Plan Review - Waiting for user input.")
    user_input = input(">> Enter feedback to revise the plan, or press Enter to approve: ").strip()

    if user_input:
        logger.info(f"   -> User provided feedback for plan revision.")
        return {"plan_review": {"verified": False, "critique": user_input, "retry_count": retry_count + 1}}
    else:
        logger.info(f"   -> User approved the plan.")
        return {"plan_review": {"verified": True, "critique": None, "retry_count": retry_count}}

# ==============================================================================
# Phase 3: 执行 (Execution - Single Slide Generation)
# ==============================================================================

def generate_code_directive_node(state: SlideState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] 生成单张 slide 的布局指令"""
    config = config["configurable"]
    slide_page = state["slide_page"]
    logger.info(f"--- SUBGRAPH NODE (Slide {slide_page}): GenerateCodeDirective ---")
    
    slide_dir = os.path.join(config["output_dir"], "result", f"slide_{slide_page:02d}")
    os.makedirs(slide_dir, exist_ok=True)

    directive = generate_layout_directive(
        slide_style_protocol=state["slide_style_protocol"],
        slide_content=state["slide_plan"],
        llm_config=_get_llm_config(config),
        output_dir=slide_dir,
    )
    
    if not directive:
        logger.error(f"❌ [Slide {slide_page}] Failed to generate layout directive. Aborting slide.")
        # Propagate error state
        return {"code_directive": None, "error_log": "Layout directive generation failed."}

    logger.info(f"✅ SUBGRAPH NODE (Slide {slide_page}): GenerateCodeDirective completed.")
    return {"code_directive": directive}

def generate_slide_code_node(state: SlideState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] 生成单张 slide 的 Python 代码"""
    config = config["configurable"]
    slide_page = state["slide_page"]
    logger.info(f"--- SUBGRAPH NODE (Slide {slide_page}): GenerateSlideCode ---")
    
    slide_dir = os.path.join(config["output_dir"], "result", f"slide_{slide_page:02d}")
    os.makedirs(slide_dir, exist_ok=True)
    output_pptx_path = os.path.join(slide_dir, f"slide.pptx")

    code_review = state.get("code_review", {})

    code = generate_slide_code(
        code_directive=state["code_directive"],
        failed_code=state.get('code'),
        error_context=state.get("error_log"),
        slide_code_verified=code_review.get("verified"),
        output_pptx_path=output_pptx_path,
        llm_config=_get_llm_config(config),
    )

    if not code:
        logger.error(f"❌ [Slide {slide_page}] Code generation failed. Aborting slide.")
        return {"code": None, "error_log": "Code generation returned empty result"}

    # 保存代码
    code_attempt = code_review.get("retry_count", 0)
    code_path = os.path.join(slide_dir, f"code_v{code_attempt}.py")
    with open(code_path, "w", encoding='utf-8') as f: 
        f.write(code)
    
    logger.info(f"   -> Python code generated and saved to {code_path}")
    logger.info(f"✅ SUBGRAPH NODE (Slide {slide_page}): GenerateSlideCode completed.")
    return {"code": code, "code_path": code_path, "error_log": None}

def check_code_execution_node(state: SlideState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] 检查代码能否正常执行"""
    config = config["configurable"]
    slide_page = state["slide_page"]
    logger.info(f"--- SUBGRAPH NODE (Slide {slide_page}): CheckCodeExecution ---")
    
    if not state.get("code"):
        logger.error(f"❌ [Slide {slide_page}] No code to execute.")
        return {"code_review": {"verified": False, "retry_count": 0, "critique": "No code available to execute"}, "error_log": "No code available to execute"}

    code_path = state.get("code_path")
    if not code_path or not os.path.exists(code_path):
        logger.error(f"❌ [Slide {slide_page}] Code file not found: {code_path}")
        return {"code_review": {"verified": False, "retry_count": 0, "critique": f"Code file not found: {code_path}"}, "error_log": f"Code file not found: {code_path}"}

    logger.info(f"   -> Executing Python script: {code_path}")
    success, exec_error = run_script(code_path)

    code_review = state.get("code_review", {})
    retry_count = code_review.get("retry_count", 0)

    if success:
        logger.info(f"   -> ✅ Code executed successfully for slide {slide_page}.")
        logger.info(f"✅ SUBGRAPH NODE (Slide {slide_page}): CheckCodeExecution completed.")
        return {
            "code_review": {"verified": True, "retry_count": retry_count, "critique": None},
            "error_log": None,
            "generated_slide_paths": [state["code_path"]]  # 收集代码路径，用于最终合并
        }
    else:
        logger.warning(f"   -> ❌ Code execution failed for slide {slide_page} (Attempt {retry_count + 1}). Error: {exec_error}")
        logger.info(f"✅ SUBGRAPH NODE (Slide {slide_page}): CheckCodeExecution completed (with failure).")
        return {
            "code_review": {"verified": False, "retry_count": retry_count + 1, "critique": exec_error},
            "error_log": exec_error,
        }

def check_slide_design_node(state: SlideState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] 检查单张 slide 的视觉质量"""
    config = config["configurable"]
    slide_page = state["slide_page"]
    logger.info(f"--- SUBGRAPH NODE (Slide {slide_page}): CheckSlideDesign ---")

    slide_dir = os.path.join(config["output_dir"], "result", f"slide_{slide_page:02d}")
    output_pptx_path = os.path.join(slide_dir, f"slide.pptx")
  
    critique_feedback = evaluate_and_critique_slide(
        slide_code=state["code"],
        slide_style_protocol=state["slide_style_protocol"],
        pptx_path=output_pptx_path,
        llm_config=_get_llm_config(config),
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
    
    slide_paths = sorted(state.get("generated_slide_paths", []))
    
    if not slide_paths:
        logger.warning("   -> No slides were generated to merge.")
        return {"final_pptx_path": None}
    
    final_path = os.path.join(config["output_dir"], "result", "Final_Presentation.pptx")
    merge_deck(slide_paths, final_path)
    
    logger.info(f"   -> ✅ Merged {len(slide_paths)} slides into {final_path}")
    return {"final_pptx_path": final_path}

def review_pptx_design_node(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """[Node] HITL 2: Final Inspection - 集成人工交互逻辑"""
    logger.info("--- NODE: ReviewPPTXDesign (HITL) ---")
    config = config["configurable"]

    pptx_path = state.get("final_pptx_path")
    slides_plan = state.get("presentation_plan")

    review = state.get("pptx_review", {})
    retry_count = review.get("retry_count", 0)

    if not pptx_path or not os.path.exists(pptx_path):
        logger.warning("   -> Final PPTX file not found. Skipping user review.")
        return {"pptx_review": {"verified": True, "retry_count": retry_count, "critique": None}}

    logger.info(f"\n✨ Preview Ready: Your presentation has been generated at '{pptx_path}'")
    logger.info("🛑 HITL [2/2]: Final Inspection - Waiting for user input.")

    user_input = input(">> Enter feedback for refinements, or press Enter to accept: ").strip()

    if not user_input:
        logger.info("   -> ✅ User accepted the final presentation. Workflow will now complete.")
        return {"pptx_review": {"verified": True, "retry_count": retry_count, "critique": None}}

    logger.info("   -> User provided feedback for final revision. Analyzing feedback...")
    analysis_result = analyze_feedback_with_llm(
        user_input=user_input,
        slide_count=len(slides_plan or []),
        llm_config=_get_llm_config(config),
    )

    logger.info(f"   -> Feedback analysis result: Scope='{analysis_result.scope}', Target Pages={analysis_result.target_pages}")

    if analysis_result.scope == "ambiguous":
        logger.warning("   -> Feedback is ambiguous. Prompting user to provide more specific instructions.")
        return {"pptx_review": {"verified": True, "retry_count": retry_count, "critique": "ambiguous"}}

    return {
        "pptx_review": {"verified": False, "retry_count": retry_count + 1, "critique": analysis_result.scope},
        "retry_slide_pages": analysis_result.target_pages,
    }