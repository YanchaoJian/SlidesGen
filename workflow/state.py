import operator
from typing import TypedDict, List, Dict, Optional, Annotated, Any


# ==============================================================================
# 通用审查循环结构
# ==============================================================================

class ReviewCycle(TypedDict):
    """verified + retry_count + critique 三元组，用于所有需要重试的审查环节。"""
    verified: bool
    retry_count: int
    critique: Optional[str]


def _default_review_cycle() -> ReviewCycle:
    return {"verified": False, "retry_count": 0, "critique": None}


# ==============================================================================
# A. 全局主控状态 (State for the Main Graph)
# ==============================================================================

class OverallState(TypedDict):
    """
    定义主工作流的全局状态。
    使用 Annotated[List, operator.add] 处理并行列表合并。
    """
    # --- 感知层产物 ---
    content: Optional[Dict[str, Any]]

    # --- 风格层产物 ---
    style_protocol: Optional[str]
    style_review: ReviewCycle                      # 风格协议审查

    # --- 规划层产物 ---
    main_content: Optional[Dict[str, Any]]
    presentation_plan: Optional[List[Dict[str, Any]]]
    plan_review: ReviewCycle                       # 演示计划审查

    # --- 执行层产物 (Reducer) ---
    generated_slide_paths: Annotated[List[str], operator.add]

    # --- 交付层产物 ---
    final_pptx_path: Optional[str]
    pptx_review: ReviewCycle                       # 最终 PPTX 审查
    retry_slide_pages: Optional[List[int]]


# ==============================================================================
# B. 单页子任务状态 (State for the Slide Subgraph)
# ==============================================================================

class SlideState(TypedDict):
    """
    定义分发给并行"单页生成"节点的"任务数据包"。
    """
    # --- 任务标识 ---
    slide_page: int

    # --- 任务输入 (由主图在分发时提供) ---
    slide_plan: Dict[str, Any]
    slide_style_protocol: str

    # --- 运行状态 ---
    code_directive: Optional[str]
    code: Optional[str]
    code_path: Optional[str]
    error_log: Optional[str]

    # --- 审查循环 ---
    code_review: ReviewCycle                       # 代码执行验证
    design_review: ReviewCycle                     # 设计质量验证

    # --- 输出 ---
    generated_slide_paths: Optional[List[str]]


# ==============================================================================
# 辅助函数：提供默认初始化状态
# ==============================================================================

def initialize_overall_state() -> OverallState:
    return {
        "content": None,
        "style_protocol": None,
        "style_review": _default_review_cycle(),
        "main_content": None,
        "presentation_plan": None,
        "plan_review": _default_review_cycle(),
        "generated_slide_paths": [],
        "final_pptx_path": None,
        "pptx_review": _default_review_cycle(),
        "retry_slide_pages": None,
    }


def initialize_slide_state(
    slide_page: int,
    slide_plan: Dict[str, Any],
    slide_style_protocol: str,
) -> SlideState:
    return {
        "slide_page": slide_page,
        "slide_plan": slide_plan,
        "slide_style_protocol": slide_style_protocol,
        "code_directive": None,
        "code": None,
        "code_path": None,
        "error_log": None,
        "code_review": _default_review_cycle(),
        "design_review": _default_review_cycle(),
        "generated_slide_paths": [],
    }