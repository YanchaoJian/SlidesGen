import json
import logging
import os
import re
from typing import Any, Dict, Optional

from langchain_core.prompts import ChatPromptTemplate

from utils.llm import LLMConfig, create_llm, extract_json_string

logger = logging.getLogger(__name__)


def _fix_json_escaping(json_str: str) -> str:
    fixed = re.sub(
        r'(?<!\\)\\(?!\\)',
        r'\\\\',
        json_str
    )
    changes = len(fixed) - len(json_str)
    if changes > 0:
        logger.info(f"✅ Fixed {changes // 2} unescaped backslashes")
        logger.debug(f"Before: {len(json_str)} chars, After: {len(fixed)} chars")
    else:
        logger.debug("✅ JSON escaping is correct, no fix needed")
    
    return fixed



def enhance_tables_and_equations(base_content, output_dir, llm_config: LLMConfig):
    if not llm_config.get("api_key"):
        logger.warning("OpenAI API key not provided, skipping LLM enhancement")
        return base_content

    try:
        llm = create_llm(llm_config, temperature=0.2)
        
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
            if "equations" in tables_equations_result:
                enhanced_content["equations"] = tables_equations_result["equations"]
                
        enhanced_content_file = os.path.join(output_dir, "raw", "enhanced_content.json")        
        os.makedirs(os.path.dirname(enhanced_content_file), exist_ok=True)

        with open(enhanced_content_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_content, f, ensure_ascii=False, indent=2)
        
        logger.info(f"LLM content enhancement completed, results saved to {enhanced_content_file}")
        return enhanced_content

    except Exception as e:
        logger.error(f"Error during LLM enhancement: {str(e)}")
        return base_content


def _extract_tables_and_equations(llm, full_text: str, output_dir: str) -> Optional[Dict]:
    """
    Step 1: Specifically extract tables and formulas
    """
    try:
        # Import special character handling module
        from utils.char_protection import preprocess_content_for_llm, postprocess_content_from_llm, validate_special_chars_in_output
        from agents.pdf_parser.prompts import EXTRACT_TABLES_AND_EQUATIONS_PROMPT
        
        # Preprocess text to protect special characters
        protected_text = preprocess_content_for_llm(full_text)
        logger.debug("Special characters have been preprocessed and protected")
        logger.debug(f"Preprocessed text length: {len(protected_text)}")
        
        prompt = ChatPromptTemplate.from_template(EXTRACT_TABLES_AND_EQUATIONS_PROMPT)
        chain = prompt | llm
        response = chain.invoke({"full_text": protected_text})
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        logger.debug(f"LLM raw response length: {len(response_text)}")
        logger.debug(f"Last 100 characters of LLM response: ...{response_text[-100:]}")
        
        # Restore special characters
        response_text = postprocess_content_from_llm(response_text)

        # Extract JSON string, then fix escaping before parsing
        json_str = extract_json_string(response_text)
        if not json_str:
            logger.warning("Failed to extract JSON string from LLM response")
            return None

        # 🔧 修复 JSON 转义问题（将单反斜杠替换为双反斜杠）
        json_str = _fix_json_escaping(json_str)

        # Parse JSON
        result = json.loads(json_str)
        
        # Validate if special characters are lost
        if result.get('tables'):
            for table in result['tables']:
                markdown_content = table.get('markdown_content', '')
                lost_chars = validate_special_chars_in_output(full_text, markdown_content)
                if lost_chars:
                    logger.warning(f"Table {table.get('id', 'unknown')} lost special characters: {lost_chars}")
        
        logger.info(f"Successfully extracted {len(result.get('tables', []))} tables and {len(result.get('equations', []))} equations")
        return result
        
    except Exception as e:
        logger.warning(f"Error extracting tables and formulas: {str(e)}")
        return None