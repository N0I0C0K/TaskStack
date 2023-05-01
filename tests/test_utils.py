import pytest

from utils.thread_pool import clean_up


@pytest.fixture
def clean_thread():
    yield
    clean_up()
