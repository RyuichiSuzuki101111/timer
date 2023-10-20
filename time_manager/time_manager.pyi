# flake8: noqa
# pylint: disable=unused-argument
from __future__ import annotations

from types import TracebackType
from typing import Callable, Optional, ParamSpec

P = ParamSpec('P')

def update_timer_defaults(
    timeout: Optional[float] = None, dt: Optional[float] = None
) -> None: ...

class Timer:
    def __init__(
        self,
        timeout: Optional[float] = None,
        dt: Optional[float] = None,
        task_label: Optional[str] = None,
    ) -> None: ...
    @property
    def dt(self) -> float: ...
    @property
    def timeout(self) -> float: ...
    def start(self) -> None: ...
    def sleep(self) -> None: ...
    def check_timeout(self) -> bool: ...
    def timeout_error(self) -> TimeoutError: ...
    def wait_until(
        self, condition: Callable[P, bool], *args: P.args, **kwargs: P.kwargs
    ) -> None: ...
    def __enter__(self) -> Timer: ...
    def __exit__(
        self,
        exc_type: type[Exception],
        exc_value: Exception,
        exc_traceback: TracebackType,
    ) -> None: ...
