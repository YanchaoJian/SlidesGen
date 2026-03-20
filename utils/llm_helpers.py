import base64
import json
import logging
import re
from typing import Any, Dict, Optional, TypedDict

from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


# ==============================================================================
# LLM 配置类型与工厂函数
# ==============================================================================

class LLMConfig(TypedDict):
    """LLM 连接配置，替代散装的 api_key / base_url / model_name 参数。"""
    model_name: str
    api_key: str
    base_url: Optional[str]


def create_llm(llm_config: LLMConfig, temperature: float = 0.1) -> ChatOpenAI:
    """根据统一配置创建 ChatOpenAI 实例。"""
    return ChatOpenAI(
        model=llm_config["model_name"],
        api_key=llm_config["api_key"],
        base_url=llm_config["base_url"],
        temperature=temperature,
    )


def encode_image_to_base64(image_path: str) -> str:
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


def extract_json_string_from_response(response_text: str) -> Optional[str]:
    """
    从 LLM 返回的文本中提取 JSON 字符串（不解析）。

    按优先级尝试以下策略：
      1. 匹配 ```json ... ``` 代码块
      2. 匹配通用 ``` ... ``` 代码块
      3. 寻找第一个 '{' / '[' 到最后一个 '}' / ']' 之间的内容
      4. 直接返回原文

    Returns:
        提取到的 JSON 字符串，如果输入为空则返回 None。
    """
    if not response_text:
        return None

    json_str = None

    # 策略 1: ```json ... ```
    match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
    if match:
        json_str = match.group(1).strip()

    # 策略 2: ``` ... ```
    if json_str is None:
        match = re.search(r'```\s*(.*?)\s*```', response_text, re.DOTALL)
        if match:
            json_str = match.group(1).strip()

    # 策略 3: 第一个 '{' 到最后一个 '}' (或 '[' 到 ']')
    if json_str is None:
        start_obj = response_text.find('{')
        end_obj = response_text.rfind('}')
        start_arr = response_text.find('[')
        end_arr = response_text.rfind(']')

        # 取更靠前的那个起始符
        candidates = []
        if start_obj != -1 and end_obj > start_obj:
            candidates.append((start_obj, end_obj + 1))
        if start_arr != -1 and end_arr > start_arr:
            candidates.append((start_arr, end_arr + 1))

        if candidates:
            start, end = min(candidates, key=lambda c: c[0])
            json_str = response_text[start:end]

    # 策略 4: 直接使用原文
    if json_str is None:
        json_str = response_text.strip()

    # 清理 BOM 字符
    json_str = json_str.lstrip('\ufeff')

    return json_str


def extract_json_from_response(response_text: str) -> Optional[Dict[str, Any]]:
    """
    从 LLM 返回的文本中提取并解析 JSON 对象。

    Returns:
        解析后的字典/列表，如果失败则返回 None。
    """
    json_str = extract_json_string_from_response(response_text)
    if json_str is None:
        return None

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        logger.debug(f"Invalid JSON string: {json_str[:500]}...")
        return None
