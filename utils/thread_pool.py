from concurrent.futures import Future, ThreadPoolExecutor
import asyncio


main_loop = asyncio.get_event_loop()
asyncio.set_event_loop(main_loop)
thread_pool = ThreadPoolExecutor(5)


def set_main_loop(loop: asyncio.AbstractEventLoop):
    global main_loop
    main_loop = loop


__all__ = ["thread_pool", "Future", "main_loop", "set_main_loop"]
