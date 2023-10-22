# flake8: noqa
# pylint: disable=unused-argument,multiple-statements
from __future__ import annotations

from types import TracebackType
from typing import Callable, Coroutine, Optional, ParamSpec

P = ParamSpec('P')

class InvalidTokenError(Exception): ...

class TimerContextToken:
    def __hash__(self) -> int: ...
    def __eq__(self, other: TimerContextToken) -> bool: ...
    def destroy(self) -> None: ...
    def __enter__(self) -> TimerContextToken: ...
    def __exit__(
        self,
        exc_type: type[Exception],
        exc_value: Exception,
        exc_traceback: TracebackType,
    ) -> bool: ...

def create_timer_context(
    timeout: float, polling_time: float
) -> TimerContextToken: ...

class Timer:
    def __init__(
        self,
        context_token: TimerContextToken,
        task_label: Optional[str] = None,
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
