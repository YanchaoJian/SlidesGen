"""LangChain callback：在每次 LLM 调用结束时，把 usage 报到 MetricsStore。

挂载方式见 utils/llm.create_llm：末尾 `llm.with_config({"callbacks": [TokenCountingCallback(stage=...)]})`。
只依赖 langchain_core，不依赖主项目其他模块，避免循环引用。
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from langchain_core.callbacks import AsyncCallbackHandler

from utils.instrumentation.metrics_store import MetricsStore

logger = logging.getLogger(__name__)


class TokenCountingCallback(AsyncCallbackHandler):
    """按模型分账记录 token 消耗。stage 在构造时注入，用于 per-stage 聚合。"""

    def __init__(self, stage: Optional[str] = None):
        self.stage = stage

    # LangChain base 默认 on_chat_model_start 会 raise NotImplementedError 来触发
    # fallback，但回调调度器会把它当作异常记到日志（"Error in callback coroutine"）。
    # 我们在 start 阶段本来就不做任何事，实现成 no-op 即可静默警告。
    async def on_chat_model_start(self, *args: Any, **kwargs: Any) -> None:
        pass

    async def on_llm_start(self, *args: Any, **kwargs: Any) -> None:
        pass

    # ChatOpenAI 走 on_llm_end（non-chat 路径）或 on_chat_model_end（chat 路径）。
    # 两个都实现，指向同一处理逻辑，保证不同 langchain 版本都能命中。
    async def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        self._record(response, kwargs)

    async def on_chat_model_end(self, response: Any, **kwargs: Any) -> None:  # pragma: no cover
        self._record(response, kwargs)

    def _record(self, response: Any, kwargs: dict) -> None:
        try:
            llm_output = getattr(response, "llm_output", None) or {}
            usage = (
                llm_output.get("token_usage")
                or llm_output.get("usage")
                or {}
            )
            # fallback：有些 provider 把 usage 塞到 generation.message.usage_metadata
            if not usage:
                try:
                    gen = response.generations[0][0]
                    meta = getattr(gen, "message", None)
                    um = getattr(meta, "usage_metadata", None) if meta else None
                    if um:
                        usage = {
                            "prompt_tokens": um.get("input_tokens", 0),
                            "completion_tokens": um.get("output_tokens", 0),
                        }
                except Exception:
                    pass

            model = (
                llm_output.get("model_name")
                or llm_output.get("model")
                or (kwargs.get("invocation_params") or {}).get("model")
                or "unknown"
            )

            prompt = int(usage.get("prompt_tokens", 0) or 0)
            completion = int(usage.get("completion_tokens", 0) or 0)

            if prompt == 0 and completion == 0:
                return  # 流式场景可能没有 usage，静默跳过

            MetricsStore.record_tokens(
                model=model,
                prompt=prompt,
                completion=completion,
                stage=self.stage,
            )
        except Exception as e:  # 绝不让 instrumentation 层影响主流程
            logger.debug(f"TokenCountingCallback record failed: {e}")
