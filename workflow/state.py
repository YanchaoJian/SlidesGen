from typing import TypedDict, List, Dict, Optional, Annotated, Any


def _merge_slide_paths(left: Dict[int, str], right: Dict[int, str]) -> Dict[int, str]:
    """Reducer：按 slide_page 合并路径，后写入覆盖先写入。

    用于 generated_slide_paths：并行子图各自返回 {page: path}，HITL 局部
    重生成时新版本自动覆盖旧版本，避免累加列表里残留过期条目。
    """
    merged = dict(left or {})
    merged.update(right or {})
    return merged


def _merge_slide_reports(
    left: Dict[int, "SlideReport"], right: Dict[int, "SlideReport"]
) -> Dict[int, "SlideReport"]:
    """Reducer：按 slide_page 合并子图审查报告，后写入覆盖先写入。

    用于 slide_reports：把每页子图的 svg_review / design_review 等关键字段
    冒泡到主图，便于 final_snapshot.json 一次性保存完整实验数据。
    """
    merged = dict(left or {})
    merged.update(right or {})
    return merged


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


class SlideReport(TypedDict):
    """单页子图的终态快照，用于从子图冒泡到主图 OverallState.slide_reports。

    仅包含实验评估/调试所需的关键字段，不存 svg_code 正文（避免快照文件爆炸）。
    """
    slide_page: int
    svg_review: ReviewCycle
    design_review: ReviewCycle
    slide_detail: Optional[str]
    svg_path: Optional[str]
    error_log: Optional[str]


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
    # 存储各 slide 的最终 SVG 路径，key 为 slide_page。后写覆盖先写，
    # 局部重生成 / 恢复执行时不会留下过期条目。
    generated_slide_paths: Annotated[Dict[int, str], _merge_slide_paths]

    # 每页子图的终态报告 {slide_page: SlideReport}，由 check_slide_design_node
    # 写入后通过 reducer 冒泡到主图，供 final_snapshot.json 和实验后处理脚本使用。
    slide_reports: Annotated[Dict[int, SlideReport], _merge_slide_reports]

    # --- 交付层产物 ---
    final_pptx_path: Optional[str]
    pptx_review: ReviewCycle                       # 最终 PPTX 审查（critique 字段保存原始用户反馈文本）
    pptx_feedback_scope: Optional[str]             # 反馈分类: local/global_style/global_plan/ambiguous
    retry_slide_pages: Optional[List[int]]


# ==============================================================================
# B. 单页子任务状态 (State for the Slide Subgraph)
# ==============================================================================

class SlideState(TypedDict):
    """
    定义分发给并行"单页生成"节点的"任务数据包"。
    SVG 管线：扩展大纲 → LLM 生成 SVG → 验证+后处理 → 设计质量检查。
    """
    # --- 任务标识 ---
    slide_page: int
    total_pages: int

    # --- 任务输入 (由主图在分发时提供) ---
    slide_plan: Dict[str, Any]
    slide_style_protocol: str

    # --- 大纲扩展产物 ---
    slide_detail: Optional[str]                    # 由 expand_slide_plan 生成的详细描述

    # --- 运行状态 ---
    svg_code: Optional[str]                        # LLM 生成的 SVG 源码
    svg_path: Optional[str]                        # 保存到磁盘的 SVG 文件路径
    error_log: Optional[str]

    # --- 审查循环 ---
    svg_review: ReviewCycle                        # SVG 验证+后处理
    design_review: ReviewCycle                     # 设计质量验证

    # --- 输出 ---
    generated_slide_paths: Dict[int, str]
    # 子图冒泡到主图的审查报告；键是 slide_page，reducer 在 OverallState 定义。
    slide_reports: Dict[int, SlideReport]


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
        "generated_slide_paths": {},
        "slide_reports": {},
        "final_pptx_path": None,
        "pptx_review": _default_review_cycle(),
        "pptx_feedback_scope": None,
        "retry_slide_pages": None,
    }


def initialize_slide_state(
    slide_page: int,
    slide_plan: Dict[str, Any],
    slide_style_protocol: str,
    total_pages: int = 10,
) -> SlideState:
    return {
        "slide_page": slide_page,
        "total_pages": total_pages,
        "slide_plan": slide_plan,
        "slide_style_protocol": slide_style_protocol,
        "slide_detail": None,
        "svg_code": None,
        "svg_path": None,
        "error_log": None,
        "svg_review": _default_review_cycle(),
        "design_review": _default_review_cycle(),
        "generated_slide_paths": {},
        "slide_reports": {},
    }