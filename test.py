from utils.config import config
from utils.file import db_path

from utils.thread_pool import main_loop


def test_utils():
    print(db_path.as_posix())


from task_core.task_unit import TaskUnit, asdict
import time


async def test_task():
    a = TaskUnit(
        name="1",
        command="ipconfig",
    )
    print(asdict(a.__dict__))
    a.run()
    time.sleep(2)
    print(a.task_exectuor.stdout)


async def add_task():
    from task_core.task_manager import task_manager
    from task_core.form_model import TaskAddForm

    task = task_manager.add_task(TaskAddForm(name="test", command="ipconfig"))
    task.run()
    task.task_exectuor.wait()
    print(task.task_exectuor.stdout)


main_loop.run_until_complete(add_task())


def test_database():
    from data import dataManager, SessionInfo

    with dataManager.session as sess:
        for r in sess.query(SessionInfo).all():
            print(r)


def test_database_add():
    from data import dataManager, SessionInfo

    with dataManager.session as sess:
        a = SessionInfo(
            id="1",
            invoke_time=10,
            finish_time=111,
            task_id="111",
            command="111",
        )
        sess.add(a)
        sess.commit()


# test_database_add()

from pydantic import BaseModel
import functools


def test_other():
    class Test(BaseModel):
        a: str
        b: str

        @functools.wraps(BaseModel.__init__)
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            print("1")

    a = Test(a="1", b="1")
    a = Test()


# test_other()
