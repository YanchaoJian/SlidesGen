"""模型价格表（每 1M token 美元价）与成本计算。

未列出的模型走前缀匹配 fallback；均不命中则返回 (0, 0)，由调用方记 warning。
数据来源：各厂商官方定价页面。按需扩展。
"""
from typing import Tuple

# (prompt_per_1M_usd, completion_per_1M_usd)
MODEL_PRICING: dict[str, Tuple[float, float]] = {
    # OpenAI
    "gpt-5.4-mini":            (0.45, 2.70),
    # Anthropic
    "claude-sonnet-4-6":       (3.00, 15.00),
    # Gemini
    "gemini-3.1-pro-preview":  (1.60, 9.60),
    "gemini-3.1-flash-lite-preview": (0.375, 2.25),
    # 常见国产 / 第三方
    "MiniMax-M2.7":            (2.10, 8.40),
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
    return round(prompt_tokens / 1_000_000 * p_in + completion_tokens / 1_000_000 * p_out, 6)


def is_known(model: str) -> bool:
    return lookup_price(model) != (0.0, 0.0)
