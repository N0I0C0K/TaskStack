from concurrent.futures import Future, ThreadPoolExecutor
from deprecated import deprecated
from typing import Callable
import asyncio
import threading

main_loop = asyncio.get_event_loop()
asyncio.set_event_loop(main_loop)
thread_pool = ThreadPoolExecutor(64)


def set_main_loop(loop: asyncio.AbstractEventLoop):
    global main_loop
    main_loop = loop


def get_loop_in_other_thread() -> tuple[asyncio.AbstractEventLoop, asyncio.Event]:
    loop: asyncio.AbstractEventLoop = None
    event = threading.Event()
    close_event: asyncio.Event | None = None

    async def keep_loop_run():
        nonlocal close_event
        close_event = asyncio.Event()
        event.set()
        await close_event.wait()
        print("close")

    def close_loop():
        close_event.set()

    def new_thread_loop():
        nonlocal loop
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            event.set()
            loop.run_forever()
        except Exception as e:
            print(e)
        finally:
            # 释放资源
            loop.close()

    thread_pool.submit(new_thread_loop)
    event.wait(timeout=5)
    if not event.is_set():
        raise TimeoutError("Event loop was not created within 5 seconds")
    return loop, close_event


__all__ = [
    "thread_pool",
    "Future",
    "main_loop",
    "set_main_loop",
    "get_loop_in_other_thread",
]
