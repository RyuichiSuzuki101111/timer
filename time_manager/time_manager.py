from __future__ import annotations

import time
from types import TracebackType
from typing import Callable, Coroutine, Optional, ParamSpec
import asyncio

P = ParamSpec('P')


# TimerContextTokenと timeout, polling_timeのペアの対応を管理する辞書
_timer_context: dict[TimerContextToken, tuple[float, float]] = {}


class InvalidTokenError(Exception):
    """
    破壊済みのトークンを利用しようとしたときに発生する。
    """


class TimerContextToken:
    _is_active: bool = True

    def __hash__(self) -> int:
        if self._is_active:
            return id(self)

        raise InvalidTokenError(f'トークン{self!r}は破壊済みです。')

    def __eq__(self, other: TimerContextToken) -> bool:
        if not isinstance(other, TimerContextToken):
            return NotImplemented

        return self is other

    def destroy(self) -> None:
        if self._is_active:
            del _timer_context[self]
            self._is_active = False

    def __enter__(self) -> TimerContextToken:
        return self

    def __exit__(
        self,
        exc_type: type[Exception],
        exc_value: Exception,
        exc_traceback: TracebackType,
    ) -> bool:
        self.destroy()
        return False


def create_timer_context(
    timeout: float, polling_time: float
) -> TimerContextToken:
    token = TimerContextToken()
    _timer_context[token] = (timeout, polling_time)
    return token


class Timer:
    def __init__(
        self,
        context_token: TimerContextToken,
        task_label: Optional[str] = None,
    ):
        timeout, polling_time = _timer_context[context_token]
        self.task_label = task_label
        self._timeout = timeout
        self._polling_time = polling_time
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
