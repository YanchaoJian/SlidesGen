"""模型价格表（每 1K token 美元价）与成本计算。

未列出的模型走前缀匹配 fallback；均不命中则返回 (0, 0)，由调用方记 warning。
数据来源：各厂商官方定价页面。按需扩展。
"""
from typing import Tuple

# (prompt_per_1k_usd, completion_per_1k_usd)
MODEL_PRICING: dict[str, Tuple[float, float]] = {
    # OpenAI
    "gpt-4o":             (0.0025, 0.0100),
    "gpt-4o-mini":        (0.00015, 0.00060),
    "gpt-4-turbo":        (0.0100, 0.0300),
    "gpt-4":              (0.0300, 0.0600),
    "gpt-3.5-turbo":      (0.0005, 0.0015),
    "o1":                 (0.0150, 0.0600),
    "o1-mini":            (0.0030, 0.0120),
    "o3-mini":            (0.0011, 0.0044),
    # Anthropic
    "claude-3-5-sonnet":  (0.0030, 0.0150),
    "claude-3-5-haiku":   (0.0008, 0.0040),
    "claude-3-opus":      (0.0150, 0.0750),
    "claude-opus-4":      (0.0150, 0.0750),
    "claude-opus-4-6":    (0.0150, 0.0750),
    "claude-sonnet-4":    (0.0030, 0.0150),
    "claude-haiku-4-5":   (0.0010, 0.0050),
    # 常见国产 / 第三方（OpenAI-compatible gateway）
    "deepseek-chat":      (0.00027, 0.0011),
    "deepseek-reasoner":  (0.00055, 0.00219),
    "glm-4":              (0.00014, 0.00014),
    "glm-4-plus":         (0.0070, 0.0070),
    "qwen-max":           (0.0020, 0.0060),
    "qwen-plus":          (0.00040, 0.0012),
    "MS":                 (0.0, 0.0),  # 占位，用于本地/未知模型别名
}


def lookup_price(model: str) -> Tuple[float, float]:
    """精确匹配 → 前缀匹配 → (0, 0)。"""
    if not model:
        return (0.0, 0.0)
    if model in MODEL_PRICING:
        return MODEL_PRICING[model]
    # 前缀匹配：处理带日期/版本后缀的变体，如 gpt-4o-2024-11-20
    # 取最长的匹配前缀以避免 "gpt-4" 误匹配 "gpt-4o-..."
    best_key = None
    for key in MODEL_PRICING:
        if model.startswith(key) and (best_key is None or len(key) > len(best_key)):
            best_key = key
    if best_key:
        return MODEL_PRICING[best_key]
    return (0.0, 0.0)


def calc_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """按模型倍率计算美元成本，保留 6 位小数。"""
    p_in, p_out = lookup_price(model)
    return round(prompt_tokens / 1000 * p_in + completion_tokens / 1000 * p_out, 6)


def is_known(model: str) -> bool:
    return lookup_price(model) != (0.0, 0.0)
