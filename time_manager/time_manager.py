from __future__ import annotations

import time
from types import TracebackType
from typing import Callable, Coroutine, Optional, ParamSpec, overload
import asyncio

P = ParamSpec('P')


class _TimerConfig:
    timer_configs: dict[str, _TimerConfig] = {}
    default_timeout: float = 2e6
    default_polling_time: float = 2e-6

    def __init__(
        self, timeout: Optional[float], polling_time: Optional[float]
    ) -> None:
        if polling_time is None:
            self.polling_time = _TimerConfig.default_polling_time
        else:
            self.polling_time = polling_time

        if timeout is None:
            self.timeout = _TimerConfig.default_timeout
        else:
            self.timeout = timeout


def set_timer_defaults(
    timer_context_key: str = 'global',
    timeout: Optional[float] = None,
    polling_time: Optional[float] = None,
) -> None:
    match timer_context_key:
        case 'global':
            if polling_time is not None:
                _TimerConfig.default_polling_time = polling_time
            if timeout is not None:
                _TimerConfig.default_timeout = timeout
        case _:
            _TimerConfig.timer_configs[timer_context_key] = _TimerConfig(
                timeout, polling_time
            )


class Timer:
    @overload
    def __init__(self, task_label: Optional[str] = None):
        pass

    @overload
    def __init__(
        self,
        task_label: Optional[str] = None,
        *,
        timer_context_key: str = 'global',
    ):
        pass

    @overload
    def __init__(
        self,
        task_label: Optional[str] = None,
        *,
        timeout: Optional[float] = None,
        polling_time: Optional[float] = None,
    ):
        ...

    def __init__(
        self,
        task_label: Optional[str] = None,
        *,
        timer_context_key: Optional[str] = None,
        timeout: Optional[float] = None,
        polling_time: Optional[float] = None,
    ):
        if timer_context_key is None:
            timer_context_key = 'global'

        timer_config = _TimerConfig.timer_configs.get(timer_context_key)
        if timer_config is None:
            raise ValueError(
                f'timer_context_keyに未登録のコンテキストキー{timer_context_key}'
                'が設定されています。'
            )

        if timeout:
            self._timeout = timeout
        else:
            self._timeout = timer_config.timeout

        if polling_time:
            self._polling_time = polling_time
        else:
            self._polling_time = timer_config.polling_time

        self.task_label = task_label
        self.start_timestamp: float
        self.end_timestamp: float
        self.start()

    @property
    def polling_time(self) -> float:
        return self._polling_time

    @property
    def timeout(self) -> float:
        return self._timeout

    def start(self) -> Timer:
        """タイムアウトの時刻を(再)設定して、自身を返す。
        Timerクラスがコンテキストマネージャであるため、

        with timer.start():
            await timer.wait_until_async(some_condition, arg1, arg2)

        のような使い方ができる。
        """
        self.start_timestamp = time.time()
        self.end_timestamp = self.start_timestamp + self.timeout
        return self

    def check_timeout(self) -> bool:
        """現在の時刻がタイムアウト時刻を超えているかどうかを判定する。"""
        return self.end_timestamp <= time.time()

    def timeout_error(self) -> TimeoutError:
        """TimeoutError オブジェクトを作成する。"""
        if self.task_label is None:
            return TimeoutError('タスクがタイムアウトしました。')

        return TimeoutError(f"タスク'{self.task_label}'がタイムアウトしました。")

    def wait_until(
        self,
        condition: Callable[P, bool],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        """
        受け取った関数がTrueを返すまでループする。
        タイムアウトになった場合, TimeoutErrorを発生させる。
        """
        while not self.check_timeout():
            if condition(*args, **kwargs):
                return

            time.sleep(self.polling_time)

        raise self.timeout_error()

    async def wait_until_async(
        self,
        condition: Callable[P, Coroutine[bool, None, None]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        """
        受け取った非同期関数がTrueを返すまでループする。
        タイムアウトになった場合, TimeoutErrorを発生させる。
        """
        while not self.check_timeout():
            if await condition(*args, **kwargs):
                return

            await asyncio.sleep(self.polling_time)

        raise self.timeout_error()

    def __enter__(self) -> Timer:
        return self

    def __exit__(
        self,
        exc_type: type[Exception],
        exc_value: Exception,
        exc_traceback: TracebackType,
    ) -> bool:
        return False
