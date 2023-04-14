from utils.config import config
from utils.file import db_path

from utils.thread_pool import main_loop


def test_utils():
    print(db_path.as_posix())


from task_core.task_unit import TaskUnit
import time


async def test_task():
    a = TaskUnit(
        id="1",
        name="1",
        active=True,
        create_time=1.1,
        command="ipconfig",
    )
    a.run_task()
    time.sleep(2)
    print(a.task_exectuor.stdout)


main_loop.run_until_complete(test_task())


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
