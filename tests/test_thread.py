from .test_utils import clean_thread
from pytest import mark
from utils.thread_pool import thread_pool, get_second_loop
import asyncio


def test_cross_thread_modify(clean_thread):
    a = 1

    def modify_a():
        nonlocal a
        a = 2

    fur = thread_pool.submit(modify_a)
    fur.result()
    assert a == 2


@mark.asyncio
async def test_multiple_async():
    loop = asyncio.get_running_loop()
    loop2 = asyncio.new_event_loop()

    async def sle():
        await asyncio.sleep(2)

    await loop2.create_task(sle())
