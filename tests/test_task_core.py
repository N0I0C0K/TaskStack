from task_core.task_unit import TaskUnit
from pytest import mark
import asyncio


@mark.asyncio
async def test_task_iter_return():
    from utils.thread_pool import set_main_loop
    from task_core.task_executor import TaskExecutor

    set_main_loop(asyncio.get_running_loop())

    from utils.thread_pool import main_loop

    assert main_loop.is_running() == True
    a = TaskExecutor(
        "temp.exe"
    )  # TaskExecutor("timeout /t 3 > nul & echo Hello World")
    await a.wait_until_run()
    assert a.stdout == ""
    while a.running:
        print(await a.readline())

    assert await a.wait(timeout=5) is not None
    await a.flush_stdout()
    assert a.stdout != ""


@mark.asyncio
async def test_taskexector_kill():
    from utils.thread_pool import set_main_loop
    from task_core.task_executor import TaskExecutor

    set_main_loop(asyncio.get_running_loop())

    a = TaskExecutor("timeout /t 100 > nul & echo Hello World")
    await a.wait_until_run()
    assert a.running == True
    a.kill()
    await a.wait()
    assert a.running == False


@mark.asyncio
async def test_add_del_task():
    from task_core.form_model import TaskAddForm
    from task_core.task_manager import task_manager
    from utils.thread_pool import set_main_loop

    set_main_loop(asyncio.get_running_loop())

    task = task_manager.add_task(TaskAddForm(name="test", command="whoami"))
    task.run()

    await task.task_exectuor.wait_until_run()

    assert task.task_exectuor.running is True

    await task.task_exectuor.wait()
    tl = await task.task_exectuor.flush_stdout()
    print(tl)
    assert tl != ""

    assert task.task_exectuor.running is False

    # task_manager.del_task(task.id)
    # assert task_manager.get_task(task.id) is None


@mark.asyncio
async def test_asyncio_command_exec():
    process = await asyncio.create_subprocess_shell(
        "timeout /t 5 > nul & echo Hello World", stdout=asyncio.subprocess.PIPE
    )

    async def read_stdout():
        while True:
            line = await process.stdout.readline()
            print(line)
            if line == b"":
                break

    asyncio.create_task(read_stdout())
    await process.wait()
    print(f"Process returned {process.returncode}")


@mark.asyncio
async def test_exector_input():
    from task_core.task_executor import TaskExecutor

    a = TaskExecutor("python ./task_test_program/test_input.py", input="3\n")

    await a.wait()
    print(a.stdout)


def test_database():
    from data import SessionInfo, dataManager

    with dataManager.session as sess:
        for r in sess.query(SessionInfo).all():
            assert r.id != ""
