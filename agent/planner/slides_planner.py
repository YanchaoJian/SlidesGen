import json
import logging
import os
import re
from typing import Dict, Any, Optional

# LangChain / OpenAI 依赖
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 导入 Prompt 定义
# 确保你的 prompts.py 路径正确
from agent.planner.prompts import (
    MAIN_CONTENT_EXTRACTION,
    SLIDES_PLANNING,
    INITIAL_GENERATION_INSTRUCTION, 
    REFINEMENT_BLOCK_TEMPLATE
)


logger = logging.getLogger(__name__)


def _extract_json_from_response(response_text: str) -> Optional[Dict]:
    """从 LLM 的文本响应中提取 JSON 对象。"""
    match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
    json_str = match.group(1).strip() if match else response_text.strip()
    try:
        # 移除可能的BOM字符
        json_str = json_str.lstrip('\ufeff')
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        logger.debug(f"Invalid JSON string: {json_str[:500]}...")
        return None


def _extract_main_content(llm: ChatOpenAI, enhanced_content: Dict[str, Any]) -> Dict[str, Any]:
    """[第二步] 提取关键内容，如图表、公式和核心论点。"""
    logger.info("   Planner Step 1/2: Extracting main content...")
    try:
        full_text = enhanced_content.get("full_text")
        prompt = ChatPromptTemplate.from_template(MAIN_CONTENT_EXTRACTION)
        chain = prompt | llm
        response = chain.invoke({
            "text": full_text,
            "figures_info": json.dumps(enhanced_content.get("images"), ensure_ascii=False),
            "tables_info": json.dumps(enhanced_content.get("tables"), ensure_ascii=False),
            "equations_info": json.dumps(enhanced_content.get("equations"), ensure_ascii=False),
        })
        response_text = response.content
        return _extract_json_from_response(response_text) or {}
    except Exception as e:
        logger.warning(f"Could not extract key content: {e}")
        return {}

def _plan_slides(
    llm: ChatOpenAI, 
    main_content: Dict[str, Any],
    previous_plan: Optional[Dict[str, Any]] = None,
    plan_critique: Optional[str] = None,
    presentation_plan_verified: bool = False
) -> Optional[list]:
    """
    [第三步] 根据前两步的结果，规划每一页幻灯片的内容。
    支持基于之前的计划和评论进行迭代修改。
    """
    logger.info("   Planner Step 2/2: Planning slides...")
    try:
        # 1. 提取基础信息
        presentation_flow = main_content.get("presentation_flow")
        enhanced_tables = main_content.get("tables")
        enhanced_equations = main_content.get("equations")
        enhanced_figures = main_content.get("figures")
        paper_info = main_content.get("paper_info")

        # 2. 处理“人机交互/自反思”的历史信息
        is_refinement = previous_plan and not presentation_plan_verified

        if is_refinement:
            logger.info("🔄 Refinement Mode: Incorporating previous plan and critique.")
            
            # 序列化之前的计划
            previous_slides_plan_str = json.dumps(previous_plan, ensure_ascii=False, indent=2)
            
            # 将旧计划和批评意见填入修复模板
            refinement_instructions = REFINEMENT_BLOCK_TEMPLATE.format(
                previous_plan_json=previous_slides_plan_str,
                plan_critique=plan_critique
            )
        else:
            logger.info("✨ Creation Mode: Generating initial plan.")
            refinement_instructions = INITIAL_GENERATION_INSTRUCTION
        
         # 构建 Chain
        prompt_template = ChatPromptTemplate.from_template(SLIDES_PLANNING)
        chain = prompt_template | llm

        # 4. 执行调用
        # 注意：这里假设 SLIDES_PLANNING 模板中包含了对应的占位符
        # 如果模板中没有 {previous_slides_plan} 等占位符，LangChain 通常会忽略多余的参数，不会报错
        response = chain.invoke({
            # --- 论文核心内容 ---
            "title": paper_info.get("title", ""),
            "authors": ", ".join(paper_info.get("authors", [])),
            "abstract": paper_info.get("abstract", ""),
            "background_context": presentation_flow.get("background_context", ""),
            "problem_motivation": presentation_flow.get("problem_motivation", ""),
            "solution_overview": presentation_flow.get("solution_overview", ""),
            "technical_approach": presentation_flow.get("technical_approach", ""),
            "evidence_proof": presentation_flow.get("evidence_proof", ""),
            "impact_significance": presentation_flow.get("impact_significance", ""),
            
            # --- 多模态素材 ---
            "figures_info": json.dumps(enhanced_figures, ensure_ascii=False),
            "tables_info": json.dumps(enhanced_tables, ensure_ascii=False),
            "equations_info": json.dumps(enhanced_equations, ensure_ascii=False),
            
            # --- 历史与反思 (新增部分) ---
            "refinement_instructions": refinement_instructions,
        })

        response_text = response.content
        return _extract_json_from_response(response_text)

    except Exception as e:
        logger.error(f"Could not plan slides: {e}", exc_info=True)
        return None

def generate_presentation_plan(
    previous_main_content: Optional[Dict[str, Any]],
    previous_plan: Optional[Dict[str, Any]],
    user_feedback_plan: Optional[str],
    presentation_plan_verified: bool,
    content: Dict[str, Any],
    presentation_plan_retry_count: Optional[int],
    output_dir: str,
    model_name: str,
    api_key: str,
    base_url: Optional[str] = None,
    
) -> Optional[Dict[str, Any]]:
    """
    [核心工具函数] 通过三步法，根据解析后的 PDF 内容字典生成演示大纲。

    Args:
        raw_content: 包含 'full_text', 'images' 等键的字典。
        model_name: 使用的 LLM 名称。
        api_key: OpenAI API key。
        base_url: OpenAI API base URL。

    Returns:
        包含完整规划信息的字典，如果失败则返回 None。
    """

    try:
        # 初始化一个可复用的 LLM 实例
        llm = ChatOpenAI(
            model=model_name,
            temperature=0.15,
            api_key=api_key,
            base_url=base_url
        )
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        return None

    # 依次执行两个步骤
    if previous_main_content:
        logger.info("Using previous main content for slide planning.")
        paper_main_content = previous_main_content
    else:
        logger.info("Extracting main content from enhanced content.")
        paper_main_content = _extract_main_content(llm, content)
        plan_dir = os.path.join(output_dir, "plan")
        os.makedirs(plan_dir, exist_ok=True)
        paper_main_content_path = os.path.join(plan_dir, f"paper_main_content.json")
        with open(paper_main_content_path, "w", encoding='utf-8') as f:
            json.dump(paper_main_content, f, indent=2, ensure_ascii=False)
        logger.info(f"   Paper main content saved to {paper_main_content_path}")

    presentation_plan = _plan_slides(
        llm=llm, 
        main_content=paper_main_content, 
        previous_plan=previous_plan, 
        plan_critique=user_feedback_plan, 
        presentation_plan_verified=presentation_plan_verified
    )

    if presentation_plan and isinstance(presentation_plan, list):
        logger.info(f"Successfully generated a 2-step plan with {len(presentation_plan)} slides.")
        
        plan_path = os.path.join(plan_dir, f"presentation_plan_v{presentation_plan_retry_count}.json")
        with open(plan_path, "w", encoding='utf-8') as f:
            json.dump(presentation_plan, f, indent=2, ensure_ascii=False)
        logger.info(f"Presentation plan saved to {plan_path}")

        return paper_main_content,presentation_plan
    elif paper_main_content:
        logger.error("The final step of planning slides failed to return a valid list.")
        return paper_main_content, None
    else:
        logger.error("Failed to generate presentation plan.")
        return None, None