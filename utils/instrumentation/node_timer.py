"""@time_node 装饰器：自动把节点耗时累加进 MetricsStore。

支持同步 / 异步函数；抛异常时也会在 finally 中记录一笔，便于观测失败节点的
实际开销。默认名字取自函数名去掉 `_node` 后缀，可显式传入 name 覆盖。
"""
from __future__ import annotations

import asyncio
import functools
import time
from typing import Callable, Optional

from utils.instrumentation.metrics_store import MetricsStore


def time_node(name: Optional[str] = None) -> Callable:
    def deco(fn: Callable) -> Callable:
        nm = name or fn.__name__
        if nm.endswith("_node"):
            nm = nm[: -len("_node")]

        if asyncio.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def awrap(*args, **kwargs):
                t0 = time.perf_counter()
                try:
                    return await fn(*args, **kwargs)
                finally:
                    MetricsStore.record_node(nm, time.perf_counter() - t0)
            return awrap

        @functools.wraps(fn)
        def swrap(*args, **kwargs):
            t0 = time.perf_counter()
            try:
                return fn(*args, **kwargs)
            finally:
                MetricsStore.record_node(nm, time.perf_counter() - t0)
        return swrap

    return deco
