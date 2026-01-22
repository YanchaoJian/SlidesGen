import operator
from typing import TypedDict, List, Dict, Optional, Annotated, Any


# ==============================================================================
# A. 全局主控状态 (State for the Main Graph)
# ==============================================================================

class OverallState(TypedDict):
    """
    定义主工作流的全局状态。
    使用 Annotated[List, operator.add] 处理并行列表合并。
    """    
    # --- 感知层产物 ---
    content: Optional[Dict[str, Any]]     # PDF 解析数据
    
    # --- 风格层产物 ---
    style_protocol: Optional[Dict[str, Any]] 
    style_protocol_verified: Optional[bool]        # 风格协议是否验证通过
    style_protocol_critique: Optional[str]         # 风格协议反馈
    style_protocol_retry_count: Optional[int]      # 风格自查重试次数，默认 0

    # --- 规划层产物 ---
    main_content: Optional[Dict[str, Any]]   # 提取的主要内容
    presentation_plan: Optional[List[Dict[str, Any]]]
    presentation_plan_verified: Optional[bool]     # 演示计划是否验证通过
    user_feedback_plan: Optional[str]              # 用户对计划的反馈
    presentation_plan_retry_count: Optional[int]   # 规划重试次数，默认 0

    # --- 执行层产物 (Reducer) ---
    # operator.add 会自动将并行节点返回的路径追加到列表
    generated_slide_paths: Annotated[List[str], operator.add]

    # --- 交付层产物 ---
    final_pptx_path: Optional[str]                 # 最终合并的PPTX路径
    user_feedback_pptx_design: Optional[str]       # 用户对最终PPTX的反馈
    pptx_verified: Optional[bool]           # PPTX设计是否验证通过
    retry_slide_pages: Optional[List[int]]         # 需要重新生成的幻灯片页码列表


# ==============================================================================
# B. 单页子任务状态 (State for the Slide Subgraph)
# ==============================================================================

class SlideState(TypedDict):
    """
    定义分发给并行"单页生成"节点的"任务数据包"。
    """
    # --- 任务标识 ---
    slide_page: int              # [必填] 页码

    # --- 任务输入 (由主图在分发时提供) ---
    slide_plan: Dict[str, Any]    # [必填] 本页的大纲内容
    slide_style_protocol: Dict[str, Any] 
    
    # --- 运行状态/局部修正 (全部可选，默认应为 None) ---
    code_directive: Optional[str]      # 布局指令
    code: Optional[str]    # 生成的代码
    code_path: Optional[str]      # 代码文件路径
    error_log: Optional[str]      # 报错日志
    
    # 代码执行验证相关
    slide_code_verified: Optional[bool]   # 代码是否通过执行验证
    slide_code_retry_count: Optional[int]  # 代码执行重试次数，默认 0
    
    # 设计质量验证相关
    slide_design_verified: Optional[bool]  # 设计是否通过验证
    slide_design_critique: Optional[str]   # 设计反馈
    slide_design_retry_count: Optional[int]  # 设计检查重试次数，默认 0
    
    # 输出
    generated_slide_paths: Optional[List[str]]  # 生成的单张幻灯片路径

# ==============================================================================
# 💡 辅助函数：提供默认初始化状态
# ==============================================================================
def initialize_overall_state() -> OverallState:
    """
    由于 TypedDict 不支持行内默认值，请在图开始运行时使用此函数初始化
    """
    return {
        "content": None,
        "style_protocol": None,
        "style_protocol_verified": False,
        "style_protocol_critique": None,
        "style_protocol_retry_count": 0,
        "presentation_plan": None,
        "presentation_plan_verified": False,
        "user_feedback_plan": None,
        "presentation_plan_retry_count": 0,
        "generated_slide_paths": [],  
        "user_feedback_pptx_design": None,
        "pptx_design_verified": False,
        "retry_slide_pages": None
    }

def initialize_slide_state(slide_page: int, slide_plan: Dict[str, Any], slide_style_protocol: Dict[str, Any]) -> SlideState:
    """
    初始化单页子任务状态
    """
    return {
        "slide_page": slide_page,
        "slide_plan": slide_plan,
        "slide_style_protocol": slide_style_protocol,
        "code_directive": None,
        "code": None,
        "code_path": None,
        "error_log": None,
        "slide_code_verified": False,
        "slide_code_retry_count": 0,
        "slide_design_verified": False,
        "slide_design_critique": None,
        "slide_design_retry_count": 0,
        "generated_slide_paths": []
    }