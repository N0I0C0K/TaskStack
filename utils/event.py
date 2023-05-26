from typing import TypeVar, Generic, Callable
from utils import logger
from utils.thread_pool import thread_pool
import asyncio

T = TypeVar("T")
Ts = TypeVar


class Event(Generic[T]):
    def __init__(self) -> None:
        self.actions: set[Callable[[T], None]] = set()

    def invoke(
        self,
        p: T,
        *,
        loop: asyncio.AbstractEventLoop | None = None,
        use_multiple_thread: bool = True
    ):
        try:
            loop = asyncio.get_running_loop() if loop is None else loop
        except Exception as e:
            logger.error("get loop error: %s", e)

        for func in self.actions:
            try:
                if asyncio.iscoroutinefunction(func):
                    if loop is None:
                        raise RuntimeError(
                            "the event func is coroutine function but loop not found"
                        )
                    loop.create_task(func(p))
                elif use_multiple_thread:
                    thread_pool.submit(func, p)
                else:
                    func(p)
            except Exception as e:
                logger.error("event invoke error: %s", e)

    def __iadd__(self, func: Callable[[T], None]):
        self.actions.add(func)
        return self

    def __isub__(self, func: Callable[[T], None]):
        self.actions.remove(func)
        return self


class MultipleEvent(Generic[T]):
    # TODO 多参数的事件
    pass
