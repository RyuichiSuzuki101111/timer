from __future__ import annotations

import time
from types import TracebackType
from typing import Callable, Optional, ParamSpec

P = ParamSpec('P')


class TimerConfig:
    timeout: float = 2e7
    dt: float = 2e-7

    def __init__(self, timeout: Optional[float], dt: Optional[float]) -> None:
        if dt is None:
            self.dt = TimerConfig.dt
        else:
            self.dt = dt

        if timeout is None:
            self.timeout = TimerConfig.timeout
        else:
            self.timeout = timeout


def update_timer_defaults(
    timeout: Optional[float] = None, dt: Optional[float] = None
) -> None:
    if timeout is not None:
        TimerConfig.timeout = timeout
    if dt is not None:
        TimerConfig.dt = dt


class Timer:
    def __init__(
        self,
        timeout: Optional[float] = None,
        dt: Optional[float] = None,
        task_label: Optional[str] = None,
    ):
        self._config: TimerConfig = TimerConfig(timeout, dt)
        self.task_label = task_label
        self.start_timestamp = 0.0
        self.end_timestamp = 0.0

    @property
    def dt(self) -> float:
        return self._config.dt

    @property
    def timeout(self) -> float:
        return self._config.timeout

    def start(self) -> None:
        self.start_timestamp = time.time()
        self.end_timestamp = self.start_timestamp + self.timeout

    def sleep(self) -> None:
        time.sleep(self.dt)

    def check_timeout(self) -> bool:
        return self.end_timestamp <= time.time()

    def timeout_error(self) -> TimeoutError:
        if self.task_label is None:
            return TimeoutError('task timeout!')

        return TimeoutError(f"task: '{self.task_label}' timeout!")

    def wait_until(
        self, condition: Callable[P, bool], *args: P.args, **kwargs: P.kwargs
    ) -> None:
        """受け取った関数がTrueを返すまでループする。
        タイムアウトになった場合, TimeoutErrorを発生させる
        """
        while not self.check_timeout():
            if condition(*args, **kwargs):
                return
            self.sleep()
        raise self.timeout_error()

    def __enter__(self) -> Timer:
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[Exception],
        exc_value: Exception,
        exc_traceback: TracebackType,
    ) -> None:
        if exc_value is not None:
            raise exc_value
