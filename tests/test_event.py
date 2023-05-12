from utils.event import Event
from pytest import mark


def test_event():
    a = Event[str]()
    s_l = []

    def add(s: str):
        s_l.append(s)

    a += add

    a.invoke("1")
    assert s_l[0] == "1"
    a -= add
    a.invoke("2")
    assert len(s_l) == 1


@mark.asyncio
async def test_async_event():
    import asyncio

    num = 1
    loc = asyncio.Event()

    async def func1(t: int):
        nonlocal num
        num += t
        loc.set()

    async def func2(t: int):
        await loc.wait()
        nonlocal num
        num *= t

    ev = Event[int]()
    ev += func1
    ev += func2
    ev.invoke(2)
    await asyncio.sleep(1)
    assert num == 6


def test_thread_event():
    import threading

    a = Event[str]()
    s_l = []

    def add(s: str):
        s_l.append(s)

    a += add

    threading.Thread(target=a.invoke, args=("1",)).start()
    assert s_l[0] == "1"
    a -= add
    threading.Thread(target=a.invoke, args=("2",)).start()
    assert len(s_l) == 1
