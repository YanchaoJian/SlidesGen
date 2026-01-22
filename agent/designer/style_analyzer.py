import os
import base64
import json
import re
import logging
from typing import Dict, Any, Optional

# LangChain / OpenAI 依赖
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# 导入 Prompt
from agent.designer.prompts import ANALYZE_STYLE_SYSTEM_PROMPT, ANALYZE_STYLE_USER_PROMPT, ANALYZE_STYLE_REFINEMENT_USER_PROMPT

logger = logging.getLogger(__name__)

# ==============================================================================
# 2. 核心工具函数
# ==============================================================================

def _encode_image_to_base64(image_path: str) -> str:
    """将图片文件编码为 Base64 字符串。"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        logger.error(f"Image file not found at: {image_path}")
        raise
    except Exception as e:
        logger.error(f"Failed to encode image {image_path}: {e}")
        raise

def _extract_json_from_response(response_text: str) -> str:
    """
    [旧版方法] 从 LLM 返回的 Markdown 文本中提取纯 JSON 字符串。
    使用正则表达式匹配，存在一定的不稳定性。
    """
    # 策略 1: 匹配 ```json ... ``` 代码块
    match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # 策略 2: 匹配通用代码块 ``` ... ```
    match = re.search(r'```\s*(.*?)\s*```', response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # 策略 3: 如果没有代码块，尝试寻找从第一个 '{' 到最后一个 '}' 的内容
    try:
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start != -1 and end != 0:
            return response_text[start:end]
    except Exception:
        pass
        
    return response_text

def analyze_style(
    style_image_path: str, 
    output_dir: str,
    api_key: str, 
    base_url: str, 
    model_name: str,
    previous_protocol: Optional[Dict[str, Any]] = None,
    previous_protocol_critique: Optional[str] = None,
    style_protocol_retry_count: Optional[int] = 0,
    style_protocol_verified: Optional[bool] = False
) -> Optional[Dict[str, Any]]:
    """
    调用 Vision LLM 分析 PPT 截图风格，并返回结构化的字典。
    本版本使用正则表达式从原始文本中提取 JSON。

    Args:
        image_path: 参考图的文件路径。
        api_key: OpenAI API key。
        base_url: OpenAI API base URL。
        model_name: 要使用的 Vision 模型名称 (如 'gpt-4o')。

    Returns:
        一个包含视觉协议的字典，如果失败则返回 None。
    """
    logger.info(f"🎨 Analyzing style from image: {os.path.basename(style_image_path)}")

    try:
        base64_image = _encode_image_to_base64(style_image_path)
    except Exception:
        return None

    # 1. 初始化 LLM
    llm = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=0.1,
    )

    if previous_protocol and not style_protocol_verified:
        # 将 JSON 对象转为格式化的字符串，方便 LLM 阅读
        prev_json_str = json.dumps(previous_protocol, ensure_ascii=False, indent=2)
        
        # 填充模板
        user_prompt = ANALYZE_STYLE_REFINEMENT_USER_PROMPT.format(
            previous_protocol_json=prev_json_str,
            critique_text=previous_protocol_critique
        )
        
        logging.info("Using previous style protocol and critique for refinement.")
    else:
        user_prompt = ANALYZE_STYLE_USER_PROMPT
    
    # 2. 构建消息体 
    messages = [
        SystemMessage(content=ANALYZE_STYLE_SYSTEM_PROMPT),
        HumanMessage(content=[
            {"type": "text", "text": user_prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
        ])
    ]

    # 3. 调用 LLM 并解析结果
    try:
        response = llm.invoke(messages)
        content = response.content
        
        # 3.1 使用旧方法提取 JSON 字符串
        json_str = _extract_json_from_response(content)
        
        # 3.2 解析 JSON 字符串为字典
        style_data = json.loads(json_str)
        
        logger.info("✅ Style analysis successful.")


        # 将结果保存到文件
        result_dir = os.path.join(output_dir, "style")
        os.makedirs(result_dir, exist_ok=True)
        version = style_protocol_retry_count  # None/0 视为首次
        protocol_path = os.path.join(result_dir, f"style_protocol_v{version}.json")
        with open(protocol_path, "w", encoding='utf-8') as f:
            json.dump(style_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Style protocol saved to {protocol_path}")
        return style_data

    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to parse JSON from LLM response: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ LLM call for style analysis failed: {e}")
        return None