import json
import logging
import os
import re
from typing import Any, Dict, Optional

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


logger = logging.getLogger(__name__)


def _fix_json_escaping(json_str: str) -> str:
    """
    修复 JSON 字符串中未正确转义的反斜杠
    将所有 \X (X 不是有效的 JSON 转义字符) 替换为 \\X
    
    有效的 JSON 转义序列: \\ \" \/ \b \f \n \r \t \uXXXX
    """
    # 使用正则表达式匹配未正确转义的反斜杠
    # 匹配: \ 后面不是有效的转义字符或 Unicode 转义
    fixed = re.sub(
        r'\\(?!["\\/bfnrtu]|u[0-9a-fA-F]{4})',  # 负向前瞻：后面不是有效转义字符
        r'\\\\',                                 # 替换为双反斜杠
        json_str
    )
    
    changes = len(fixed) - len(json_str)
    if changes > 0:
        logger.info(f"✅ 修复了 {changes // 2} 处未转义的反斜杠")
        logger.debug(f"修复前长度: {len(json_str)}, 修复后长度: {len(fixed)}")
    else:
        logger.debug("✅ JSON 转义正确，无需修复")
    
    return fixed


def enhance_content_with_llm(base_content, output_dir, model_name, base_url, api_key):
    logger = logging.getLogger(__name__)
    
    if not OPENAI_AVAILABLE:
        logger.warning("Cannot import OpenAI packages, skipping LLM enhancement")
        return base_content
    
    if not api_key:
        logger.warning("OpenAI API key not provided, skipping LLM enhancement")
        return base_content
    
    try:
        # Initialize LLM
        llm = ChatOpenAI(
            model=model_name,
            temperature=0.2,
            api_key=api_key,
            base_url=base_url
        )
        
        # Get full text
        full_text = base_content.get("full_text")
        if not full_text:
            logger.warning("No full_text found, skipping LLM enhancement")
            return base_content
        
        logger.info("Starting LLM content enhancement...")
        
        # Step 1: Extract tables and formulas
        logger.info("Extracting tables and formulas...")
        tables_equations_result = _extract_tables_and_equations(llm, full_text, output_dir)

        enhanced_content = base_content.copy()

        # If tables and formulas were successfully extracted, add to results
        if tables_equations_result:
            if "tables" in tables_equations_result:
                enhanced_content["tables"] = tables_equations_result["tables"]
                logger.info(f"   -> 添加 {len(enhanced_content['tables'])} 个表格")
            if "equations" in tables_equations_result:
                enhanced_content["equations"] = tables_equations_result["equations"]
                logger.info(f"   -> 添加 {len(enhanced_content['equations'])} 个公式")
                
        enhanced_content_file = os.path.join(output_dir, "raw", "enhanced_content.json")        
        os.makedirs(os.path.dirname(enhanced_content_file), exist_ok=True)

        with open(enhanced_content_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_content, f, ensure_ascii=False, indent=2)
        
        logger.info(f"LLM content enhancement completed, results saved to {enhanced_content_file}")
        return enhanced_content

    except Exception as e:
        logger.error(f"Error during LLM enhancement: {str(e)}")
        import traceback
        logger.debug(f"完整错误堆栈:\n{traceback.format_exc()}")
        return base_content


def _extract_tables_and_equations(llm, full_text: str, output_dir: str) -> Optional[Dict]:
    """
    Step 1: Specifically extract tables and formulas
    """
    try:
        # Import special character handling module
        from agent.parser.text_utils import preprocess_content_for_llm, postprocess_content_from_llm, validate_special_chars_in_output
        from agent.parser.prompts import EXTRACT_TABLES_AND_EQUATIONS_PROMPT
        
        # Preprocess text to protect special characters
        protected_text = preprocess_content_for_llm(full_text)
        logger.debug("Special characters have been preprocessed and protected")
        logger.debug(f"Preprocessed text length: {len(protected_text)}")
        
        prompt = ChatPromptTemplate.from_template(EXTRACT_TABLES_AND_EQUATIONS_PROMPT)
        chain = prompt | llm
        response = chain.invoke({"full_text": protected_text})
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        logger.debug(f"LLM raw response length: {len(response_text)}")
        
        # Restore special characters
        response_text = postprocess_content_from_llm(response_text)
        
        # 💾 保存原始响应用于调试
        raw_response_file = os.path.join(output_dir, "raw", "llm_response_raw.txt")
        os.makedirs(os.path.dirname(raw_response_file), exist_ok=True)
        with open(raw_response_file, 'w', encoding='utf-8') as f:
            f.write(response_text)
        logger.debug(f"原始 LLM 响应已保存到: {raw_response_file}")

        # Extract JSON part
        json_match = re.search(r'```(?:json)?(.*?)```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
        else:
            json_str = response_text.strip()
        
        logger.debug(f"提取的 JSON 字符串长度: {len(json_str)}")
        
        # 🔧 修复 JSON 转义问题（将单反斜杠替换为双反斜杠）
        json_str = _fix_json_escaping(json_str)
        
        # 💾 保存修复后的 JSON 用于调试
        fixed_json_file = os.path.join(output_dir, "raw", "llm_response_fixed.json")
        with open(fixed_json_file, 'w', encoding='utf-8') as f:
            f.write(json_str)
        logger.debug(f"修复后的 JSON 已保存到: {fixed_json_file}")
        
        # Parse JSON
        try:
            result = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON 解析失败: {e.msg}")
            logger.error(f"   位置: 第 {e.lineno} 行，第 {e.colno} 列 (字符 {e.pos})")
            
            # 显示错误上下文
            start = max(0, e.pos - 100)
            end = min(len(json_str), e.pos + 100)
            context = json_str[start:end]
            pointer = ' ' * min(100, e.pos - start) + '^'
            
            logger.error(f"   上下文:")
            logger.error(f"   ...{context}...")
            logger.error(f"   {pointer}")
            
            return None
        
        # Validate if special characters are lost
        if result.get('tables'):
            for table in result['tables']:
                markdown_content = table.get('markdown', '') or table.get('markdown_content', '')
                if markdown_content:
                    lost_chars = validate_special_chars_in_output(full_text, markdown_content)
                    if lost_chars:
                        logger.warning(f"Table {table.get('id', 'unknown')} lost special characters: {lost_chars}")
        
        logger.info(f"✅ 成功提取 {len(result.get('tables', []))} 个表格和 {len(result.get('equations', []))} 个公式")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error extracting tables and formulas: {str(e)}")
        import traceback
        logger.debug(f"完整错误堆栈:\n{traceback.format_exc()}")
        return None