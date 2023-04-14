from typing import TypeVar, Generic, Callable

T = TypeVar("T")


class Event(Generic[T]):
    def __init__(self) -> None:
        self.actions: set[Callable[[T], None]] = set()

    def invoke(self, p: T):
        for func in self.actions:
            func(p)

    def __iadd__(self, func: Callable[[T], None]):
        self.actions.add(func)
        return self

    def __isub__(self, func: Callable[[T], None]):
        self.actions.remove(func)
        return self
