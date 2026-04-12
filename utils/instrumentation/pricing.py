"""模型价格表（每 1M token 美元价）与成本计算。

未列出的模型走前缀匹配 fallback；均不命中则返回 (0, 0)，由调用方记 warning。
数据来源：各厂商官方定价页面。按需扩展。
"""
from typing import Tuple

# (prompt_per_1M_usd, completion_per_1M_usd)
MODEL_PRICING: dict[str, Tuple[float, float]] = {
    # OpenAI
    "gpt-4o":             (2.50, 10.00),
    "gpt-4o-mini":        (0.15, 0.60),
    "gpt-4-turbo":        (10.00, 30.00),
    "gpt-4":              (30.00, 60.00),
    "gpt-3.5-turbo":      (0.50, 1.50),
    "o1":                 (15.00, 60.00),
    "o1-mini":            (3.00, 12.00),
    "o3-mini":            (1.10, 4.40),
    # Anthropic
    "claude-3-5-sonnet":  (3.00, 15.00),
    "claude-3-5-haiku":   (0.80, 4.00),
    "claude-3-opus":      (15.00, 75.00),
    "claude-opus-4":      (15.00, 75.00),
    "claude-opus-4-6":    (15.00, 75.00),
    "claude-sonnet-4":    (3.00, 15.00),
    "claude-haiku-4-5":   (1.00, 5.00),
    # 常见国产 / 第三方（OpenAI-compatible gateway）
    "deepseek-chat":      (0.27, 1.10),
    "deepseek-reasoner":  (0.55, 2.19),
    "glm-4":              (0.14, 0.14),
    "glm-4-plus":         (7.00, 7.00),
    "qwen-max":           (2.00, 6.00),
    "qwen-plus":          (0.40, 1.20),
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
    return round(prompt_tokens / 1_000_000 * p_in + completion_tokens / 1_000_000 * p_out, 6)


def is_known(model: str) -> bool:
    return lookup_price(model) != (0.0, 0.0)
