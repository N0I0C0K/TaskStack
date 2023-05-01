from concurrent.futures import Future, ThreadPoolExecutor
import asyncio
import threading

main_loop = asyncio.get_event_loop()
asyncio.set_event_loop(main_loop)
thread_pool = ThreadPoolExecutor(64)


def set_main_loop(loop: asyncio.AbstractEventLoop):
    global main_loop
    main_loop = loop


async def keep_loop_run():
    loop = asyncio.get_running_loop()
    while loop.is_running():
        await asyncio.sleep(1)


def get_loop_in_other_thread() -> asyncio.AbstractEventLoop:
    loop: asyncio.AbstractEventLoop = None
    event = threading.Event()

    def new_thread_loop():
        nonlocal loop
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            event.set()
            loop.run_until_complete(keep_loop_run())
        except Exception as e:
            print(e)
        finally:
            # 释放资源
            loop.close()

    thread_pool.submit(new_thread_loop)
    event.wait(timeout=5)
    if not event.is_set():
        raise TimeoutError("Event loop was not created within 5 seconds")
    return loop


# second_loop = get_loop_in_other_thread()

__second_loop: asyncio.AbstractEventLoop = None


def get_second_loop() -> asyncio.AbstractEventLoop:
    global __second_loop
    if __second_loop is not None:
        return __second_loop
    __second_loop = get_loop_in_other_thread()
    return __second_loop


def clean_up():
    if __second_loop is not None:
        __second_loop.stop()
    # thread_pool.shutdown(wait=False)


__all__ = [
    "thread_pool",
    "Future",
    "main_loop",
    "set_main_loop",
    "get_second_loop",
    "clean_up",
]
