import base64
import json
import logging
import re
from typing import Any, Dict, Optional, TypedDict

from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


# ==============================================================================
# 致命 LLM 错误（401 / 配额耗尽等不可恢复错误）
# ==============================================================================

class FatalLLMError(BaseException):
    """
    不可恢复的 LLM 调用错误（如 401 鉴权失败、API key 配额耗尽）。

    继承自 BaseException 而非 Exception，使其能穿透 agent 层广泛使用的
    `except Exception` 捕获，直接向上冒泡，避免在子图内无限重试。
    """
    pass


# 匹配 401 / 配额耗尽 / 余额不足 等不可恢复错误的特征
_FATAL_PATTERNS = re.compile(
    r"(?:"
    r"401"
    r"|invalid[_\s-]*api[_\s-]*key"
    r"|incorrect\s+api\s+key"
    r"|authentication"
    r"|unauthorized"
    r"|insufficient[_\s-]*quota"
    r"|quota.*(?:exceeded|exhausted|used\s*up)"
    r"|额度.*(?:用尽|不足|耗尽)"
    r"|余额.*(?:不足|耗尽)"
    r"|RemainQuota\s*=\s*-"
    r"|billing"
    r"|payment\s+required"
    r"|402"
    r")",
    re.IGNORECASE,
)


def is_fatal_llm_error(exc: BaseException) -> bool:
    """判断异常是否属于不可恢复的 LLM 错误。"""
    if isinstance(exc, FatalLLMError):
        return True
    # 优先检查 openai SDK 的 status_code 属性
    status = getattr(exc, "status_code", None) or getattr(
        getattr(exc, "response", None), "status_code", None
    )
    if status in (401, 402, 403):
        return True
    return bool(_FATAL_PATTERNS.search(str(exc)))


def raise_if_fatal_llm_error(exc: BaseException) -> None:
    """
    若异常为不可恢复的 LLM 错误，则包装为 FatalLLMError 抛出。
    在 agent 层 `except Exception` 块开头调用，确保致命错误立即冒泡，
    不被子图的 retry 循环吞掉。
    """
    if is_fatal_llm_error(exc):
        raise FatalLLMError(f"Fatal LLM error (non-retryable): {exc}") from exc


# ==============================================================================
# LLM 配置类型与工厂函数
# ==============================================================================

class LLMConfig(TypedDict, total=False):
    """LLM 连接配置，替代散装的 api_key / base_url / model_name 参数。"""
    model_name: str
    api_key: str
    base_url: Optional[str]
    max_retries: int  # 可选；create_llm 会优先使用该字段
    stage: Optional[str]  # 可选；"vision"/"svg"/"text"，供 token 计数 per-stage 聚合


def create_llm(
    llm_config: LLMConfig,
    temperature: float = 0.1,
    timeout: float = 600.0,
    max_retries: int = 3,
) -> ChatOpenAI:
    """根据统一配置创建 ChatOpenAI 实例。

    若 ``llm_config`` 中包含 ``max_retries``，则覆盖入参默认值，
    实现"全局重试次数从 CLI 一处控制"。
    """
    effective_retries = llm_config.get("max_retries", max_retries)
    llm = ChatOpenAI(
        model=llm_config["model_name"],
        api_key=llm_config["api_key"],
        base_url=llm_config["base_url"],
        temperature=temperature,
        timeout=timeout,
        max_retries=effective_retries,
    )

    # 挂载 token 计数 callback（失败不影响主流程）
    try:
        from utils.instrumentation.token_callback import TokenCountingCallback
        llm = llm.with_config(
            {"callbacks": [TokenCountingCallback(stage=llm_config.get("stage"))]}
        )
    except Exception as _e:
        logger.debug(f"TokenCountingCallback not attached: {_e}")

    return llm


def encode_image_to_base64(image_path: str, max_dim: int = 2048) -> str:
    """将图片文件编码为 Base64 字符串。

    若任一边超过 ``max_dim``，按比例缩放后再编码，避免触发视觉模型
    的输入尺寸上限（如 2048x2048）。
    """
    try:
        from io import BytesIO
        from PIL import Image

        with Image.open(image_path) as img:
            w, h = img.size
            if max(w, h) > max_dim:
                img.thumbnail((max_dim, max_dim), Image.LANCZOS)
                logger.info(
                    f"Downscaled image {image_path} from {w}x{h} to {img.size[0]}x{img.size[1]}"
                )
                fmt = (img.format or "PNG").upper()
                if fmt not in ("PNG", "JPEG"):
                    fmt = "PNG"
                if fmt == "JPEG" and img.mode != "RGB":
                    img = img.convert("RGB")
                buf = BytesIO()
                img.save(buf, format=fmt)
                return base64.b64encode(buf.getvalue()).decode("utf-8")

        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        logger.error(f"Image file not found at: {image_path}")
        raise
    except Exception as e:
        logger.error(f"Failed to encode image {image_path}: {e}")
        raise


def extract_json_string(response_text: str) -> Optional[str]:
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

    # 匹配 <think>...</think> 及其变体
    cleaned_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
    # 匹配其他可能的推理标记
    cleaned_text = re.sub(r'\[thinking\].*?\[/thinking\]', '', cleaned_text, flags=re.DOTALL)
    
    json_str = None

    # 策略 1: ```json ... ```
    match = re.search(r'```json\s*(.*?)\s*```', cleaned_text, re.DOTALL)
    if match:
        json_str = match.group(1).strip()

    # 策略 2: ``` ... ```
    if json_str is None:
        match = re.search(r'```\s*(.*?)\s*```', cleaned_text, re.DOTALL)
        if match:
            json_str = match.group(1).strip()

    # 策略 3: 第一个 '{' 到最后一个 '}' (或 '[' 到 ']')
    if json_str is None:
        start_obj = cleaned_text.find('{')
        end_obj = cleaned_text.rfind('}')
        start_arr = cleaned_text.find('[')
        end_arr = cleaned_text.rfind(']')
        # 取更靠前的那个起始符
        candidates = []
        if start_obj != -1 and end_obj > start_obj:
            candidates.append((start_obj, end_obj + 1))
        if start_arr != -1 and end_arr > start_arr:
            candidates.append((start_arr, end_arr + 1))

        if candidates:
            start, end = min(candidates, key=lambda c: c[0])
            json_str = cleaned_text[start:end]

    # 策略 4: 直接使用原文
    if json_str is None:
        json_str = cleaned_text.strip()

    # 清理 BOM 字符
    json_str = json_str.lstrip('\ufeff')

    return json_str


def parse_json_response(response_text: str) -> Optional[Dict[str, Any]]:
    """
    从 LLM 返回的文本中提取并解析 JSON 对象。

    Returns:
        解析后的字典/列表，如果失败则返回 None。
    """
    json_str = extract_json_string(response_text)
    if json_str is None:
        return None

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        logger.debug(f"Invalid JSON string: {json_str[:500]}...")
        return None
