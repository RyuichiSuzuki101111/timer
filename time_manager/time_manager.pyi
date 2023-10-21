# flake8: noqa
# pylint: disable=unused-argument
from __future__ import annotations

from types import TracebackType
from typing import Callable, Coroutine, Optional, ParamSpec, overload

P = ParamSpec('P')

def set_timer_defaults(
    timer_context_key: str = 'global',
    timeout: Optional[float] = None,
    polling_time: Optional[float] = None,
) -> None: ...

class Timer:
    @overload
    def __init__(self, task_label: Optional[str] = None): ...
    @overload
    def __init__(
        self,
        task_label: Optional[str] = None,
        *,
        timer_context_key: str = 'global',
    ): ...
    @overload
    def __init__(
        self,
        task_label: Optional[str] = None,
        *,
        timeout: Optional[float] = None,
        polling_time: Optional[float] = None,
    ): ...
    @property
    def polling_time(self) -> float: ...
    @property
    def timeout(self) -> float: ...
    def start(self) -> Timer: ...
    def check_timeout(self) -> bool: ...
    def timeout_error(self) -> TimeoutError: ...
    def wait_until(
        self,
        condition: Callable[P, bool],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None: ...
    async def wait_until_async(
        self,
        condition: Callable[P, Coroutine[bool, None, None]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None: ...
    def __enter__(self) -> Timer: ...
    def __exit__(
        self,
        exc_type: type[Exception],
        exc_value: Exception,
        exc_traceback: TracebackType,
    ) -> bool: ...
