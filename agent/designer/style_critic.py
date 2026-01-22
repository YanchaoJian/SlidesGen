# file: agent/designer/style_critic.py

import base64
from datetime import datetime
import json
import logging
import os
from typing import Any, Dict, Tuple

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

from agent.designer.prompts import STYLE_CRITIC_SYSTEM_PROMPT, STYLE_CRITIC_USER_PROMPT

# 初始化日志记录器
logger = logging.getLogger(__name__)

# --- Pydantic 模型定义：强制 LLM 返回结构化输出 ---
class StyleCritique(BaseModel):
    """
    这是一个 Pydantic 模型，用于定义风格审查员（Style Critic）返回结果的固定数据结构。
    通过与 LangChain 的 .with_structured_output() 方法结合，可以确保 LLM 的输出总是
    一个可以被程序直接使用的 Python 对象，而不是需要手动解析的字符串。
    """
    is_approved: bool = Field(description="If the protocol accurately reflects the image's style, this is True. Otherwise, it is False.")
    critique: str = Field(description="A detailed justification for the decision. If approved, explain why. If rejected, provide specific, actionable suggestions for revision.")

def review_visual_protocol(
    output_dir: str,
    image_path: str,
    style_protocol: Dict[str, Any],
    model_name: str,
    api_key: str,
    base_url: str,
) -> Tuple[bool, str]:
    """
    这是一个核心工具函数，负责调用 Vision LLM 来对比参考图片和已生成的视觉协议JSON文件。

    它封装了从数据加载、模型初始化到 Prompt 构建和 LLM 调用的完整逻辑，
    最终返回一个清晰的、程序可用的审查结果。

    Args:
        image_path (str): 原始参考图的文件路径。
        style_protocol: agent/designer/style_analyzer.py 生成的 visual_protocol.json 文件内容的字典。
        model_name (str): 要使用的 Vision LLM 模型名称 (例如, "gpt-4o")。
        api_key (str): OpenAI 服务的 API 密钥。
        base_url (str): OpenAI 服务的 API 基础 URL。

    Returns:
        Tuple[bool, str]: 一个元组，包含两个元素：
                           - is_approved (bool): 审查是否通过。
                           - critique (str): 详细的审查意见或修改建议。
    """
    logger.info("🧐 Style Critic is reviewing the visual protocol against the reference image...")
    # --- 步骤 1: 加载用于审查的必要数据 (图片和JSON协议) ---
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        image_url = f"data:image/jpeg;base64,{base64_image}"
        
    except Exception as e:
        logger.error(f"❌ Error loading image for style critic at {image_path}: {e}")
        # 返回一个明确的失败结果，并将错误信息作为审查意见
        return False, f"Failed to load required image for review: {e}"

    # --- 步骤 2: 初始化支持结构化输出的 LangChain LLM 实例 ---
    try:
        llm = ChatOpenAI(
            model=model_name,
            temperature=0.1,  # 审查任务需要低随机性以保证结果的一致性
            api_key=api_key,
            base_url=base_url
        )
        # 绑定 Pydantic 模型，使 LLM 的输出直接成为 StyleCritique 对象
        structured_llm = llm.with_structured_output(StyleCritique)
    except Exception as e:
        logger.error(f"❌ Failed to initialize ChatOpenAI for critic: {e}")
        return False, f"Failed to initialize the critic model: {e}"

    # --- 步骤 3: 构建 Prompt 并调用 Vision LLM ---
    logger.info("   -> Invoking Vision LLM for critique...")
    
    # 这里的 user_prompt_content 是多语言的，以便中文或英文模型都能理解
    user_prompt_content = STYLE_CRITIC_USER_PROMPT.format(json.dumps(style_protocol, ensure_ascii=False, indent=2)) 
    
    messages = [
        {"role": "system", "content": STYLE_CRITIC_SYSTEM_PROMPT},
        {"role": "user", "content": [
            {"type": "text", "text": user_prompt_content},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]}
    ]

    try:
        critique_result = structured_llm.invoke(messages)
        
        status = "APPROVED" if critique_result.is_approved else "REJECTED"
        logger.info(f"   -> Critic LLM call successful. Result: {status}")

        # 保存审查结果到历史记录文件
        _save_critique_history(output_dir, critique_result, )

        return critique_result.is_approved, critique_result.critique
        
    except Exception as e:
        logger.error(f"❌ Style critic LLM call failed: {e}")
        return False, f"A critical error occurred while invoking the critic model: {e}"
    
def _save_critique_history(output_dir: str, critique_result: StyleCritique) -> None:
    """
    保存批评结果到历史记录 JSON 文件，支持追加多条记录。
    
    Args:
        critique_result (StyleCritique): 审查结果对象
        protocol_path (str): 协议文件路径，用于提取时间戳目录
    """
    try:
        history_file = os.path.join(output_dir, "style", "critique_history.json")
        
        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        
        # 构建单条审查记录
        record = {
            "timestamp": datetime.now().isoformat(),
            "is_approved": critique_result.is_approved,
            "critique": critique_result.critique
        }
        
        # 加载现有历史记录或创建新列表
        if os.path.isfile(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = []
        else:
            history = []
        
        # 追加新记录
        history.append(record)
        
        # 保存更新后的历史记录
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        logger.info(f"   -> Critique history saved to: {history_file}")
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to save critique history: {e}")