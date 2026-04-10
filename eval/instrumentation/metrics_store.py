"""线程安全的进程级指标累加器。

统一容器，同时承载：
- 节点耗时（per-node wall-clock sum / count）
- Token 消耗（按模型分账，外加 per-stage 聚合）

所有方法都是 classmethod，供装饰器和 callback 全局调用；`reset()` 在每次运行
开始时清空，`snapshot()` 在运行结束时导出。
"""
from __future__ import annotations

import logging
import threading
from typing import Any, Dict, Optional

from eval.instrumentation.pricing import calc_cost, is_known

logger = logging.getLogger(__name__)


class MetricsStore:
    _lock = threading.Lock()

    # name -> {"total": float, "count": int}
    _nodes: Dict[str, Dict[str, float]] = {}

    # model -> {"prompt_tokens","completion_tokens","total_tokens","calls"}
    _tokens: Dict[str, Dict[str, int]] = {}

    # stage -> {"prompt_tokens","completion_tokens","total_tokens","calls"}
    _stage_tokens: Dict[str, Dict[str, int]] = {}

    _warnings: list[str] = []

    # -------- lifecycle --------
    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._nodes = {}
            cls._tokens = {}
            cls._stage_tokens = {}
            cls._warnings = []

    # -------- node timing --------
    @classmethod
    def record_node(cls, name: str, elapsed: float) -> None:
        with cls._lock:
            entry = cls._nodes.setdefault(name, {"total": 0.0, "count": 0})
            entry["total"] += float(elapsed)
            entry["count"] += 1

    @classmethod
    def nodes_snapshot(cls) -> Dict[str, Dict[str, float]]:
        with cls._lock:
            out: Dict[str, Dict[str, float]] = {}
            for name, e in cls._nodes.items():
                total = round(e["total"], 3)
                count = int(e["count"])
                avg = round(total / count, 3) if count else 0.0
                out[name] = {"total": total, "count": count, "avg": avg}
            return out

    # -------- tokens --------
    @classmethod
    def record_tokens(
        cls,
        model: str,
        prompt: int,
        completion: int,
        stage: Optional[str] = None,
    ) -> None:
        model = model or "unknown"
        prompt = int(prompt or 0)
        completion = int(completion or 0)
        total = prompt + completion

        with cls._lock:
            e = cls._tokens.setdefault(
                model,
                {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "calls": 0},
            )
            e["prompt_tokens"] += prompt
            e["completion_tokens"] += completion
            e["total_tokens"] += total
            e["calls"] += 1

            if stage:
                s = cls._stage_tokens.setdefault(
                    stage,
                    {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "calls": 0},
                )
                s["prompt_tokens"] += prompt
                s["completion_tokens"] += completion
                s["total_tokens"] += total
                s["calls"] += 1

            if not is_known(model) and model != "unknown":
                msg = f"unknown model pricing: {model}"
                if msg not in cls._warnings:
                    cls._warnings.append(msg)
                    logger.warning(
                        f"[MetricsStore] {msg} — cost_usd will be 0. "
                        f"Add it to eval/instrumentation/pricing.py."
                    )

    @classmethod
    def tokens_snapshot(cls) -> Dict[str, Any]:
        with cls._lock:
            by_model: Dict[str, Dict[str, Any]] = {}
            total_prompt = total_completion = total_all = total_calls = 0
            total_cost = 0.0
            for model, e in cls._tokens.items():
                cost = calc_cost(model, e["prompt_tokens"], e["completion_tokens"])
                by_model[model] = {
                    "prompt_tokens": e["prompt_tokens"],
                    "completion_tokens": e["completion_tokens"],
                    "total_tokens": e["total_tokens"],
                    "calls": e["calls"],
                    "cost_usd": cost,
                }
                total_prompt += e["prompt_tokens"]
                total_completion += e["completion_tokens"]
                total_all += e["total_tokens"]
                total_calls += e["calls"]
                total_cost += cost

            total = {
                "prompt_tokens": total_prompt,
                "completion_tokens": total_completion,
                "total_tokens": total_all,
                "calls": total_calls,
                "cost_usd": round(total_cost, 6),
            }

            by_stage = {k: dict(v) for k, v in cls._stage_tokens.items()}

            return {"by_model": by_model, "total": total, "by_stage": by_stage}

    # -------- warnings --------
    @classmethod
    def warnings(cls) -> list[str]:
        with cls._lock:
            return list(cls._warnings)
