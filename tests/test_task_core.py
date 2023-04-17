from task_core.task_unit import TaskUnit


def test_task():
    a = TaskUnit(
        name="1",
        command="ipconfig",
    )
    a.run()
    print(a.to_dict())
    assert a.task_exectuor is not None
    a.task_exectuor.wait()
    assert a.task_exectuor.stdout != ""


def test_add_del_task():
    from task_core.form_model import TaskAddForm
    from task_core.task_manager import task_manager
    from utils.thread_pool import main_loop

    async def test():
        task = task_manager.add_task(TaskAddForm(name="test", command="whoami"))
        assert main_loop.is_closed() is False
        task.run()
        assert task.last_exec_time != 0
        task.task_exectuor.wait()
        assert task.task_exectuor.stdout != ""

        assert main_loop.is_closed() is False
        task_manager.del_task(task.id)
        assert task_manager.get_task(task.id) is None

    main_loop.run_until_complete(test())


def test_database():
    from data import SessionInfo, dataManager

    with dataManager.session as sess:
        for r in sess.query(SessionInfo).all():
            assert r.id != ""
