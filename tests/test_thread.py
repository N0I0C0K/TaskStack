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
