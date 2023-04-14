from utils.config import config
from utils.file import db_path

from utils.thread_pool import main_loop


def test_utils():
    print(db_path.as_posix())


from task_core.task_unit import TaskUnit, asdict


def test_task():
    a = TaskUnit(
        name="1",
        command="ipconfig",
    )
    a.run()
    assert a.task_exectuor is not None
    a.task_exectuor.wait()
    assert a.task_exectuor.stdout != ""


def test_add_task():
    from task_core.task_manager import task_manager
    from task_core.form_model import TaskAddForm

    task = task_manager.add_task(TaskAddForm(name="test", command="ipconfig"))
    task.run()
    task.task_exectuor.wait()
    assert task.task_exectuor.stdout != ""


def test_database():
    from data import dataManager, SessionInfo

    with dataManager.session as sess:
        for r in sess.query(SessionInfo).all():
            assert r.id != ""


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
