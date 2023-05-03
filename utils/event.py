from typing import TypeVar, Generic, Callable, Type
import asyncio

T = TypeVar("T")
Ts = TypeVar


class Event(Generic[T]):
    def __init__(self) -> None:
        self.actions: set[Callable[[T], None]] = set()

    def invoke(self, p: T, *, loop: asyncio.AbstractEventLoop | None = None):
        loop = asyncio.get_running_loop() if loop is None else loop
        for func in self.actions:
            if asyncio.iscoroutinefunction(func):
                loop.create_task(func(p))
            else:
                func(p)

    def __iadd__(self, func: Callable[[T], None]):
        self.actions.add(func)
        return self

    def __isub__(self, func: Callable[[T], None]):
        self.actions.remove(func)
        return self


class MultipleEvent(Generic[T]):
    # TODO 多参数的事件
    pass
