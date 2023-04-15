from concurrent.futures import Future, ThreadPoolExecutor
import asyncio


main_loop = asyncio.get_event_loop()
thread_pool = ThreadPoolExecutor(5)

__all__ = ["thread_pool", "Future", "main_loop"]
