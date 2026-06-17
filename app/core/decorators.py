import asyncio
import time
from functools import wraps
from typing import Any, Callable

from app.core.log import logger


def timing(func: Callable, desc: str = "") -> Callable:
    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            end_time = time.perf_counter()
            elapsed_ms = (end_time - start_time) * 1000
            logger.info(f"Function {func.__name__} executed in {elapsed_ms:.2f} ms")

    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        try:
            return await func(*args, **kwargs)
        finally:
            end_time = time.perf_counter()
            elapsed_ms = (end_time - start_time) * 1000
            logger.info(
                f"Async function {func.__name__} executed in {elapsed_ms:.2f} ms"
            )

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
